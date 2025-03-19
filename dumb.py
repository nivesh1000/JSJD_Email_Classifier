To adapt your Lambda-based project for an EC2 environment with Celery, Redis (AOF with appendfsync always), and asyncio, while maintaining clean coding practices and modularity, I’ll restructure the code into separate files and functions. The flow you’ve outlined—fetching emails every 24 hours, classifying and storing them in Redis, triggering a posting process via Celery, and deleting batches only on successful API response—will be preserved. Here’s how we’ll organize it:

Project Structure
text

Collapse

Wrap

Copy
email_processor/
├── main.py              # Entry point, Flask app, scheduler setup
├── email_fetcher.py     # Async email fetching and processing
├── email_poster.py      # Celery task for posting emails to API
├── token_refresher.py   # Token management (adapted from Lambda)
├── delete_emails.py     # Email deletion logic
├── filter_emails.py     # Email classification logic
├── get_filters.py       # Fetch filters from API
├── utils.py             # Shared utilities (URL generation, JSON reading)
└── logger.py            # Logger setup (assumed unchanged)
Requirements
Celery: For task queuing (fetching and posting).
Redis: As a broker and storage with AOF persistence (appendfsync always).
Asyncio: For non-blocking email fetching.
Flask: Lightweight web framework to run the app.
APScheduler: For scheduling fetches every 24 hours.
Redis Configuration
Edit redis.conf:

conf

Collapse

Wrap

Copy
appendonly yes
appendfsync always  # Sync every write for maximum durability
save 3600 1         # Optional RDB snapshot every hour


File-by-File Implementation

main.py
#!/usr/bin/env python3
"""Main application for email fetching, processing, and posting on EC2."""

import asyncio
import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from celery import Celery
from flask import Flask
import redis

from email_fetcher import fetch_emails_task
from email_poster import post_emails_task
from logger import EmailParser

# Constants
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
SCHEDULE_INTERVAL_HOURS = 24

# Logger setup
logger = EmailParser.get_logger()

# Celery setup
celery_app = Celery(__name__, broker=CELERY_BROKER_URL)


def setup_flask_app() -> Flask:
    """Initialize and configure the Flask application.

    Returns:
        Flask: Configured Flask app instance.
    """
    app = Flask(__name__)
    app.config["CELERY_BROKER_URL"] = CELERY_BROKER_URL
    app.config["CELERY_RESULT_BACKEND"] = CELERY_BROKER_URL
    celery_app.conf.update(app.config)
    return app


def setup_scheduler() -> BackgroundScheduler:
    """Set up the background scheduler for periodic email fetching.

    Returns:
        BackgroundScheduler: Configured scheduler instance.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: fetch_emails_task.delay(),
        "interval",
        hours=SCHEDULE_INTERVAL_HOURS,
    )
    return scheduler


def main() -> None:
    """Main entry point to set up and run the email processing application.

    Note:
        Redis uses AOF persistence with `appendfsync always` for maximum durability.
        Fetching occurs every 24 hours, with posting triggered via Celery.
    """
    try:
        # Setup Flask and Celery
        app = setup_flask_app()
        logger.info("Flask application initialized")

        # Setup scheduler
        scheduler = setup_scheduler()
        scheduler.start()
        logger.info(f"Scheduler started, fetching emails every {SCHEDULE_INTERVAL_HOURS} hours")

        # Initial fetch
        logger.info("Running initial email fetch on startup")
        fetch_emails_task.delay()

        # Start Flask app
        logger.info(f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT}")
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
    
    
--------------------------------------------------------------------
email_fetcher.py

"""Asynchronous email fetching and processing module."""

import asyncio
import json
import logging
import re
from typing import List, Dict, Optional

import aiohttp
from bs4 import BeautifulSoup

from celery import Celery
from delete_emails import delete_emails
from filter_emails import classify_emails
from get_filters import fetch_groups
from logger import EmailParser
from token_refresher import TokenManager
from app.utils import generate_today_email_url, read_json_file

# Constants from main
from main import REDIS_HOST, REDIS_PORT, REDIS_DB, celery_app
import redis

logger = EmailParser.get_logger()


async def process_and_store_emails(
    emails: List[Dict],
    filters: List[Dict],
    no_reply_emails: List[str],
    deletion_ids: List[str],
    redis_client,
) -> None:
    """Process a batch of emails, classify, and store in Redis.

    Args:
        emails: Raw email data from API.
        filters: Active filters for classification.
        no_reply_emails: List of no-reply email prefixes.
        deletion_ids: List to collect email IDs for deletion.
        redis_client: Redis client instance.
    """
    try:
        batch_emails = []
        for email in emails:
            email_id = email.get("id", "Unknown ID")
            from_address = email.get("from", {}).get("emailAddress", {}).get("address", "N/A")
            to_recipients = email.get("toRecipients", [])
            to_address = (
                to_recipients[0].get("emailAddress", {}).get("address", "N/A")
                if to_recipients
                else "N/A"
            )
            subject = email.get("subject", "")
            raw_body = email.get("body", {}).get("content", "")
            clean_body = BeautifulSoup(raw_body, "html.parser").get_text().strip()
            received_time = email.get("receivedDateTime", "Unknown Timestamp")

            if from_address in no_reply_emails:
                deletion_ids.append(email_id)
                continue

            if not clean_body and not subject:
                continue

            email_data = {
                "email_id": email_id,
                "to": to_address,
                "from": from_address,
                "subject": subject,
                "body": clean_body,
                "received_time": received_time,
                "subscriber_email": "",
                "group": [],
            }

            if from_address.startswith(tuple(no_reply_emails)):
                email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                subscriber_emails = re.findall(email_pattern, clean_body)
                email_data["subscriber_email"] = ", ".join(subscriber_emails)

            batch_emails.append(email_data)

        if batch_emails:
            classified_emails = await asyncio.to_thread(classify_emails, batch_emails, filters)
            batch_data = {"data": classified_emails}
            batch_key = f"email_batch_{len(classified_emails)}_{int(asyncio.get_event_loop().time())}"
            redis_client.set(batch_key, json.dumps(batch_data))
            logger.info(f"Stored batch {batch_key} with {len(classified_emails)} emails in Redis")

            # Trigger posting task
            from email_poster import post_emails_task
            post_emails_task.delay(batch_key)

    except Exception as e:
        logger.error(f"Error processing emails: {e}")
        raise


@celery_app.task
async def fetch_emails_task() -> None:
    """Celery task to fetch emails asynchronously and process them."""
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    try:
        token_manager = TokenManager()
        access_token = await token_manager.refreshing_token_async()
        if not access_token:
            logger.error("Failed to refresh access token")
            return

        filters_and_deletion_emails = fetch_groups()
        if not filters_and_deletion_emails or "data" not in filters_and_deletion_emails:
            logger.error("Failed to fetch filters and deletion emails")
            return

        filters = filters_and_deletion_emails["data"]["groups"]
        del_emails = [email["email_address"] for email in filters_and_deletion_emails["data"]["emailsToRemove"]]
        active_filters = [group for group in filters if group.get("status") == "active"]

        no_reply_obj = read_json_file("no_reply_variations.json")
        no_reply_variations = (
            [sample[:sample.find("@")] for sample in no_reply_obj["no_reply_variations"] if "@" in sample]
            if no_reply_obj
            else []
        )

        email_url = generate_today_email_url()
        headers = {"Authorization": f"Bearer {access_token}"}
        deletion_ids = []

        async with aiohttp.ClientSession(headers=headers) as session:
            next_url = email_url
            while next_url:
                async with session.get(next_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        emails = data.get("value", [])
                        if not emails:
                            logger.info("No emails found.")
                            break
                        await process_and_store_emails(
                            emails, active_filters, del_emails, deletion_ids, redis_client
                        )
                        next_url = data.get("@odata.nextLink", None)
                    else:
                        logger.error(f"Failed to fetch emails: {await response.text()}")
                        break

        if deletion_ids:
            await asyncio.to_thread(delete_emails, deletion_ids, access_token)
            logger.info(f"Deleted {len(deletion_ids)} emails")

    except Exception as e:
        logger.error(f"Error in fetch_emails_task: {e}")
        raise
    finally:
        redis_client.close()
----------------------------------------------------------------------
----------------------------------------------------------------------
email_poster.py

"""Celery task for posting email batches to the API."""

import json
import logging
import os

import aiohttp
from celery import Celery

from logger import EmailParser
from main import REDIS_HOST, REDIS_PORT, REDIS_DB, celery_app
import redis

logger = EmailParser.get_logger()

POST_API_URL = os.environ.get("POST_API_URL", "https://staging.jsjdmedia.com/api/emails/store")


@celery_app.task(bind=True, max_retries=5)
async def post_emails_task(self, batch_key: str) -> None:
    """Post a batch of emails to the API and delete from Redis on success.

    Args:
        batch_key: Redis key for the email batch.
    """
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    try:
        batch_data = redis_client.get(batch_key)
        if not batch_data:
            logger.error(f"Batch {batch_key} not found in Redis")
            return

        classified_emails = json.loads(batch_data.decode("utf-8"))
        if not classified_emails.get("data"):
            logger.info(f"No data in batch {batch_key}")
            redis_client.delete(batch_key)
            return

        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(POST_API_URL, json=classified_emails, headers=headers) as response:
                if response.status == 201:
                    response_json = await response.json()
                    if response_json.get("status") == "success":
                        logger.info(f"Successfully posted batch {batch_key}: {len(classified_emails['data'])} emails")
                        redis_client.delete(batch_key)
                    else:
                        logger.error(f"Failed to post batch {batch_key}: {response_json}")
                        raise self.retry(countdown=300)  # Retry after 5 minutes
                else:
                    logger.error(f"Failed to post batch {batch_key}: {response.status}")
                    raise self.retry(countdown=300)

    except Exception as e:
        logger.error(f"Error posting batch {batch_key}: {e}")
        raise self.retry(countdown=300)
    finally:
        redis_client.close()
        
-------------------------------------------------------------------
----------------------------------------------------------
token_refresher.py

"""Token management module with async refresh."""

import asyncio
import logging
import os

import aiohttp
import boto3
from config import TENANT_ID, CLIENT_ID, SCOPES
from logger import EmailParser

logger = EmailParser.get_logger()


class TokenManager:
    """Manages access and refresh tokens with SSM Parameter Store."""

    def __init__(self):
        self.tenant_id = TENANT_ID
        self.client_id = CLIENT_ID
        self.scopes = SCOPES
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        if not self.tenant_id or not self.client_id:
            raise ValueError("Missing required credentials in the configuration.")

    def get_ssm_parameters(self) -> dict:
        """Retrieve tokens from AWS SSM Parameter Store."""
        region_name = os.environ.get("REGION_NAME", "us-east-1")
        ssm = boto3.client("ssm", region_name=region_name)
        try:
            access_token = ssm.get_parameter(Name="ACCESS_TOKEN", WithDecryption=False)["Parameter"]["Value"]
            refresh_token = ssm.get_parameter(Name="REFRESH_TOKEN", WithDecryption=False)["Parameter"]["Value"]
            return {"ACCESS_TOKEN": access_token, "REFRESH_TOKEN": refresh_token}
        except Exception as e:
            logger.error(f"Error retrieving SSM parameters: {e}")
            raise

    def update_ssm_parameters(self, access_token: str, refresh_token: str) -> dict:
        """Update tokens in AWS SSM Parameter Store."""
        ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        try:
            ssm.put_parameter(Name="ACCESS_TOKEN", Value=access_token, Type="String", Overwrite=True)
            ssm.put_parameter(Name="REFRESH_TOKEN", Value=refresh_token, Type="String", Overwrite=True)
            return {"message": "Parameters updated successfully"}
        except Exception as e:
            logger.error(f"Error updating SSM parameters: {e}")
            raise

    async def refreshing_token_async(self) -> Optional[str]:
        """Asynchronously refresh the access token."""
        tokens = self.get_ssm_parameters()
        refresh_token = tokens["REFRESH_TOKEN"]
        if not refresh_token:
            logger.error("Missing REFRESH_TOKEN")
            return None

        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
            "scope": self.scopes,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=payload) as response:
                    if response.status == 200:
                        updated_tokens = await response.json()
                        new_access_token = updated_tokens["access_token"]
                        new_refresh_token = updated_tokens.get("refresh_token", refresh_token)
                        self.update_ssm_parameters(new_access_token, new_refresh_token)
                        logger.info("Tokens refreshed successfully")
                        return new_access_token
                    else:
                        logger.error(f"Token refresh failed: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
------------------------------------------------------------------------------
---------------------------------------------------------------------------------
delete_emails.py

"""Module for deleting emails via Microsoft Graph API."""

import logging
import os

import requests
from logger import EmailParser

logger = EmailParser.get_logger()
DELETE_BASE_URL = os.environ.get("DELETE_BASE_URL", "https://graph.microsoft.com/v1.0/me/messages")


def delete_emails(emails_to_remove: list, access_token: str) -> dict:
    """Delete specified emails using the Graph API.

    Args:
        emails_to_remove: List of email IDs to delete.
        access_token: Access token for authentication.
    """
    if not emails_to_remove:
        return {"statusCode": 400, "body": json.dumps({"error": "No emails provided"})}
    if not access_token:
        return {"statusCode": 401, "body": json.dumps({"error": "No access token provided"})}

    headers = {"Authorization": f"Bearer {access_token}"}
    failed_emails = []
    emails_not_found = []

    try:
        for email in emails_to_remove:
            try:
                response = requests.delete(f"{DELETE_BASE_URL}/{email}", headers=headers)
                if response.status_code == 400:
                    emails_not_found.append({"email": email, "error": response.text})
                elif response.status_code != 204:
                    failed_emails.append({"email": email, "error": response.text})
            except requests.RequestException as e:
                failed_emails.append({"email": email, "error": str(e)})

        if not failed_emails and not emails_not_found:
            status_code = 200
            message = "Successfully deleted all emails"
        elif len(failed_emails) + len(emails_not_found) < len(emails_to_remove):
            status_code = 207
            message = "Some emails deleted successfully"
        else:
            status_code = 500
            message = "No emails deleted successfully"

        return {
            "statusCode": status_code,
            "body": json.dumps({"message": message, "failed_emails": failed_emails, "emails_not_found": emails_not_found}),
        }
    except Exception as e:
        logger.error(f"Error deleting emails: {e}")
        raise
        
---------------------------------------------------------
-------------------------------------------------------------
filter_emails.py

"""Email classification module."""

import re
import logging
from typing import List, Dict

from logger import EmailParser

logger = EmailParser.get_logger()


def classify_emails(emails: List[Dict], groups: List[Dict]) -> List[Dict]:
    """Classify emails into groups based on keywords.

    Args:
        emails: List of email dictionaries.
        groups: List of group dictionaries with keywords.

    Returns:
        List of emails with assigned groups.
    """
    default_group = next((group for group in groups if not group.get("keywords")), None)
    unsubscribe_group = next((group for group in groups if group.get("name") == "Unsubscribe Requests"), None)

    for email in emails:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        matched_groups = {}

        if unsubscribe_group:
            for keyword_data in unsubscribe_group.get("keywords", []):
                keyword = keyword_data["keyword"].lower()
                if keywordmatcher(subject, keyword) or keywordmatcher(body, keyword):
                    email["group"] = [{"group_id": unsubscribe_group["id"], "keyword_id": [keyword_data["id"]]}]
                    break

        if email.get("group"):
            continue

        for group in groups:
            for keyword_data in group.get("keywords", []):
                keyword = keyword_data["keyword"].lower()
                if keywordmatcher(subject, keyword) or keywordmatcher(body, keyword):
                    if group["id"] not in matched_groups:
                        matched_groups[group["id"]] = []
                    if keyword_data["id"] not in matched_groups[group["id"]]:
                        matched_groups[group["id"]].append(keyword_data["id"])

        email["group"] = [{"group_id": gid, "keyword_id": kids} for gid, kids in matched_groups.items()]
        if not email["group"] and default_group:
            email["group"] = [{"group_id": default_group["id"], "keyword_id": []}]

    return emails


def keywordmatcher(text: str, keyword: str) -> bool:
    """Check if a keyword matches in text with word boundaries."""
    return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
  ----------------------------------------------------------
  ------------------------------------------------------------------------------------------------
  
get_filters.py

"""Module to fetch filter groups from an API."""

import logging
import os

import requests
from logger import EmailParser

logger = EmailParser.get_logger()


def fetch_groups() -> dict:
    """Fetch filter groups from the API."""
    url = os.environ.get("GET_FILTER_API")
    if not url:
        logger.error("GET_FILTER_API environment variable not set")
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching filters: {e}")
        return None
-------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
utils.py
#!/usr/bin/env python3
"""Utility functions for the email processor."""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

from logger import EmailParser

logger = EmailParser.get_logger()


def generate_today_email_url() -> str:
    """Generate URL to fetch today's emails from Microsoft Graph API."""
    try:
        today = datetime.utcnow()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
        start_time = start_of_day.isoformat() + "Z"
        end_time = end_of_day.isoformat() + "Z"
        return (
            f"https://graph.microsoft.com/v1.0/me/messages?"
            f"$top=100&"
            f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
            f"&$orderby=receivedDateTime DESC"
        )
    except Exception as e:
        logger.error(f"Error generating today email URL: {e}")
        raise


def read_json_file(file_path: str) -> Optional[Dict]:
    """Read a JSON file and return its contents."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return None
        -------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
Key Changes and Features

Celery Integration:

fetch_emails_task runs every 24 hours via Celery and scheduler.
post_emails_task triggers automatically when a batch is stored in Redis.

-------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
Redis with AOF:

Batches are stored in Redis with unique keys.

appendfsync always ensures every SET and DELETE is durable.
-------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
Asyncio:

fetch_emails_task uses aiohttp for non-blocking API calls.

Token refresh is async with refreshing_token_async.
-------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
Flow:

- Emails fetched every 24 hours (fetch_emails_task).

- Classified and stored in Redis (process_and_store_emails).

- Redis storage triggers post_emails_task.

- Successful API post deletes the batch from Redis.

- Coding Guidelines:

- Modular files for reusability (e.g., utils.py, email_poster.py).

- Type hints, docstrings, and consistent error handling.

- No unnecessary logic changes from Lambda—just adapted for EC2.

- Running the Project


Set Environment Variables:

export POST_API_URL="https://staging.jsjdmedia.com/api/emails/store"
export DELETE_BASE_URL="https://graph.microsoft.com/v1.0/me/messages"
export GET_FILTER_API="your_filter_api_url"
export REGION_NAME="us-east-1"
-------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
Start Redis:

redis-server /etc/redis/redis.conf
-------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
Start Celery Worker:

celery -A main.celery_app worker --loglevel=info
Run the App:

python3 main.py

-------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
Notes

Lambda Features Removed: The POST endpoint for deleting emails is omitted as it’s Lambda-specific. If needed on EC2, add a Flask route.

Dependencies: Install aiohttp, celery, redis, flask, apscheduler, requests, boto3, beautifulsoup4.

Config: Ensure config.py exists with TENANT_ID, CLIENT_ID, SCOPES.

This setup meets your requirements with clean, reusable code while leveraging Celery, Redis, and asyncio effectively! Let me know if you need adjustments.