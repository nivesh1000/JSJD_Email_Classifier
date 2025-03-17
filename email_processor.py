import re
import json
import redis
import requests
import threading
from bs4 import BeautifulSoup
from filter import classify_emails
from post_data import post_email_batch
from delete_emails import delete_emails
from logger import JsJdLogger, LineFileProvider
from get_filters import get_filters_and_delete_ids
from utils import generate_today_email_url
from logger import JsJdLogger, LineFileProvider
from get_filters import get_filters_and_delete_ids
from app.config import ACCESS_TOKEN, redis_client, redis_lock


# Logger initialize
logger = JsJdLogger()


class EmailProcessor:

    def fetch_emails(
        self, email_url: str, access_token: str, no_reply_emails, redis_client
    ):
        """
        Fetch emails from Microsoft Graph API in batches.

        """

        if not access_token:
            logger.error("Access token is missing.", LineFileProvider().get_file_info())
            return

        headers = {"Authorization": f"Bearer {access_token}"}

        next_url = email_url

        active_filters, emails_to_delete = get_filters_and_delete_ids()

        if not active_filters:
            logger.error(
                "Failed to fetch active filters.", LineFileProvider().get_file_info()
            )
            return

        batch_id = 0
        while next_url:
            batch_id += 1
            try:
                response = requests.get(next_url, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                emails = data.get("value", [])

                if not emails:
                    logger.info(
                        "No emails found in batch.",
                        LineFileProvider().get_file_info(),
                    )
                    break

                logger.info(
                    f"Fetched batch with {len(emails)} emails.",
                    LineFileProvider().get_file_info(),
                )

                # Send emails to get processed and classified
                self.process_emails(
                    emails,
                    active_filters,
                    emails_to_delete,
                    no_reply_emails,
                    access_token,
                    redis_client,
                    batch_id,
                )

                logger.info(
                    "Sending batch to get stored...",
                    LineFileProvider().get_file_info(),
                )

                next_url = data.get("@odata.nextLink", None)

            except requests.RequestException as e:
                logger.error(
                    f"Failed to fetch emails: {e}", LineFileProvider().get_file_info()
                )
                break

        logger.info(
            "All batches fetched. signaling store email to exit.",
            LineFileProvider().get_file_info(),
        )

    def process_emails(
        self,
        emails,
        filters,
        emails_to_delete,
        no_reply_emails,
        access_token,
        redis_client,
        batch_id,
    ):

        try:
            delete_email_ids = []
            emails_batch = []

            # Process the current batch of emails
            for email in emails:

                # logger.info(f"Processing email: {email}")

                # Extract required fields
                email_id = email.get("id", "Unknown ID")

                from_address = (
                    email.get("from", {}).get("emailAddress", {}).get("address", "N/A")
                )

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

                if from_address in emails_to_delete:
                    delete_email_ids.append(email_id)
                    continue

                if not clean_body and not subject:
                    continue

                # Append the email dictionary to the list
                email_data = {
                    "email_id": email_id,
                    "to": to_address,
                    "from": from_address,
                    "subject": subject,
                    "body": clean_body,
                    "received_time": received_time,  # Added timestamp
                    "subscriber_email": "",
                    "group": [],
                }

                if from_address.startswith(tuple(no_reply_emails)):

                    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

                    subscriber_emails = re.findall(email_pattern, clean_body)

                    email_data["subscriber_email"] = ", ".join(subscriber_emails)

                emails_batch.append(email_data)

            # delete emails on seperate thread
            if delete_email_ids:
                delete_task_output = delete_emails(delete_email_ids, access_token)

            # classify emails
            if emails_batch:
                classified_emails = classify_emails(emails_batch, filters)

                classified_emails = {"data": classified_emails}

                logger.info(
                    f"Deletion output: {delete_task_output}",
                    LineFileProvider().get_file_info(),
                )
                logger.info(
                    f"Classified Emails: {classified_emails}",
                    LineFileProvider().get_file_info(),
                )

                # ------------------- ADD emails to Redis ----------------------
                # acquire lock, blocking-> true so if any function holds lock, it waits until released.

                if redis_lock.acquire(blocking=True):
                    try:
                        redis_client.hset(
                            "email_batches", batch_id, json.dumps(classified_emails)
                        )

                    finally:  # finally always execute, even if error. Will make sure lock is released.
                        redis_lock.release()

            return delete_email_ids

        except Exception as e:
            logger.error(
                f"Error Processing emails: {e}", LineFileProvider().get_file_info()
            )
            raise


if __name__ == "__main__":

    email_url = generate_today_email_url()

    access_token = ACCESS_TOKEN

    no_reply_emails = []

    emails_manager = EmailProcessor()

    # Create threads
    fetch_thread = threading.Thread(
        target=emails_manager.fetch_emails,
        args=(email_url, access_token, no_reply_emails),
        name="fetch-mail",
    )

    # Start threads
    fetch_thread.start()

    # Wait for both threads to complete
    fetch_thread.join()

    logger.info("All batches processed.", LineFileProvider().get_file_info())

    # checking redis contents
    logger.info("Checking Redis contents:", LineFileProvider().get_file_info())

    data = redis_client.hgetall("email_batches")

    for batch_id, email_data in data.items():
        email_data = json.dumps(email_data)

        logger.forensic(
            f"\nBatch: {batch_id}, Data = {email_data}",
            LineFileProvider().get_file_info(),
        )
