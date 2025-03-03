import os
import json
import boto3
from token_refresher import TokenManager
from datetime import datetime, timedelta
from email_fetcher import fetch_emails
from filter import classify_emails
from delete_emails import delete_emails
from get_filters import fetch_groups
from config import CLIENT_ID, TENANT_ID, EMAIL_API_BASE_URL, SCOPES
from dotenv import load_dotenv
import logging

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Load environment variables from .env file
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")


def generate_today_email_url() -> str:
    """
    Generate the URL to fetch emails received today using Microsoft Graph API.

    Returns:
        str: The URL for fetching today's emails.
    """
    today = datetime.utcnow()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    # Format times in ISO 8601
    start_time = start_of_day.isoformat() + "Z"
    end_time = end_of_day.isoformat() + "Z"

    # Construct the URL for filtering emails by receivedDateTime
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages?"
        f"$top=100&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        f"&$orderby=receivedDateTime DESC"
    )
    # url="https://graph.microsoft.com/v1.0/me/messages?$filter=receivedDateTime ge 2025-02-20T00:00:00Z and receivedDateTime le 2025-02-20T23:59:59Z&$orderby=receivedDateTime DESC"
    return url


def read_json_file(file_path):
    """
    Reads a JSON file and returns the data as a Python object.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or list: The data loaded from the JSON file.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def generate_all_email_url() -> str:
    """
    Generate the URL to fetch all emails using Microsoft Graph API.

    Returns:
        str: The URL for fetching all emails.
    """
    try:
        url = (
            "https://graph.microsoft.com/v1.0/me/messages?"
            "$top=100&"
            "$orderby=receivedDateTime"
        )
        return url
    except Exception as e:
        logger.error(f"Error generating all email URL: {e}")
        return ""


def generate_last_3_days_email_url() -> str:
    """
    Generate the URL to fetch emails received in the last 3 days using Microsoft Graph API.

    Returns:
        str: The URL for fetching emails from the last 3 days.
    """
    today = datetime.utcnow()
    start_of_range = today - timedelta(days=3)  # 3 days ago
    end_of_range = today

    # Format times in ISO 8601
    start_time = (
        start_of_range.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        + "Z"
    )
    end_time = end_of_range.isoformat() + "Z"

    # Construct the URL for filtering emails by receivedDateTime
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages?"
        f"$top=100&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        f"&$orderby=receivedDateTime DESC"
    )

    return url


def lambda_handler(event):

    # EventBridge (scheduler) invocation
    task = event.get("task")

    if task == "refresh_tokens":
        try:
            return token_manager.refreshing_token(tokens)
        except Exception as e:
            return {"error": f"Failed to refresh tokens: {str(e)}"}

    elif task == "fetch_emails":
        try:
            filters = fetch_groups()
            email_url = generate_today_email_url()
            # email_url = generate_all_email_url()
            # email_url = generate_last_3_days_email_url()
            result = fetch_emails(email_url, ACCESS_TOKEN, filters)
            return result
        except Exception as e:
            return {"error": f"Failed to fetch emails: {str(e)}"}

    return {"error": "Invalid task specified"}


if __name__ == "__main__":
    event = {"task": "fetch_emails"}
    output = lambda_handler(event=event)
    print(output)
