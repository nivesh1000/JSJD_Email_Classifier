import json
import requests
import threading
from app.Scheduler.filter import classify_emails
from app.Delete_Emails.delete_emails import delete_emails
from app.Logger.logger import JsJdLogger, LineFileProvider
from app.get_filters import get_filters_and_delete_ids
from app.Logger.logger import JsJdLogger, LineFileProvider
from app.Config.settings import redis_client, redis_lock, USER_EMAIL_ADDRESS
from app.events import fetch_emails, process_redis
from app.Utilities.utils import text_normalization, extract_emails_by_sender_type
from app.Token_Refresher.token_refresher import TokenManager
import time

logger = JsJdLogger()

class EmailProcessor:

    def fetch_emails(self, email_url: str, no_reply_emails):
        """
        Fetch emails from Microsoft Graph API in batches.

        """
        token_manager = TokenManager()

        # Token expiry time in seconds. Set to refresh at 55 minutes
        token_expiry_threshold = 55 * 60

        ACCESS_TOKEN = token_manager.refresh_tokens()

        if not ACCESS_TOKEN:
            logger.error("Access token is missing.", LineFileProvider().get_file_info())
            return

        # Time at which token was initally issued
        token_issued_time = time.time()

        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

        next_url = email_url

        active_filters, emails_to_delete = get_filters_and_delete_ids()

        if not active_filters:
            logger.error(
                "Failed to fetch active filters.", LineFileProvider().get_file_info()
            )
            return

        batch_id = 0

        while next_url:

            # wait for fetch emails event
            fetch_emails.wait()
            # reset event
            fetch_emails.clear()

            batch_id += 1

            try:
                with requests.get(next_url, headers=headers) as response:
                    response.raise_for_status()

                    if time.time() - token_issued_time > token_expiry_threshold:

                        logger.forensic(
                            "Token about to expire. Refreshing....",
                            LineFileProvider().get_file_info(),
                        )

                        ACCESS_TOKEN = token_manager.refresh_tokens()

                        if not ACCESS_TOKEN:

                            logger.error(
                                "Failed to retrieve ACCESS_TOKEN. Returning.....",
                                LineFileProvider().get_file_info(),
                            )
                            return {"error": "Failed to retrieve ACCESS_TOKEN"}
                    token_issued_time = time.time()

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
                    delete_thread = self.process_emails(
                        emails,
                        active_filters,
                        emails_to_delete,
                        no_reply_emails,
                        ACCESS_TOKEN,
                        redis_client,
                        batch_id,
                    )

                    # set process redis event
                    process_redis.set()

                    # wait for delete thread to end
                    if delete_thread:
                        delete_thread.join()

                    next_url = data.get("@odata.nextLink", None)
                    # logger.forensic(
                    #     f"Email batch fetched : {emails}",
                    #     LineFileProvider().get_file_info(),
                    # )
            except requests.RequestException as e:
                logger.error(
                    f"Failed to fetch emails: {e}", LineFileProvider().get_file_info()
                )
                break

        logger.info(
            "All batches fetched. signaling store email to exit.",
            LineFileProvider().get_file_info(),
        )

        # set for last iteration
        process_redis.set()

    def process_emails(
        self,
        emails,
        filters,
        emails_to_delete,
        no_reply_emails,
        ACCESS_TOKEN,
        redis_client,
        batch_id,
    ):

        try:
            delete_email_ids = []
            emails_batch = []

            # Process the current batch of emails
            for email in emails:

                # logger.info(f"Processing email: {email}")
                to_recipients = email.get("toRecipients", [])
                to_address = (
                    to_recipients[0].get(
                        "emailAddress", {}).get("address", USER_EMAIL_ADDRESS)
                    if to_recipients
                    else USER_EMAIL_ADDRESS
                    )
                from_address = (
                    email.get("from", {}).get("emailAddress", {}).get("address", "N/A")
                )
                get_headers = email.get("internetMessageHeaders", [])
                to_header, subject_header=to_address,""

                for get_header in get_headers:
                    header_name = get_header["name"].lower()
                    if header_name == "to":
                        to_header = get_header["value"]
                        start = to_header.find("<")
                        end = to_header.find(">")
                        to_header = to_header[start + 1 : end]

                    if header_name == "subject":
                        subject_header = get_header["value"]

                # Extract required fields
                email_id = email.get("id", "Unknown ID")


                raw_body = email.get("body", {}).get("content", "")

                clean_body = text_normalization(raw_body)

                received_time = email.get("receivedDateTime", "Unknown Timestamp")

                if from_address in emails_to_delete:
                    delete_email_ids.append(email_id)
                    continue

                if not clean_body and not subject_header:
                    continue

                # Append the email dictionary to the list
                email_data = {
                    "email_id": email_id,
                    "to": to_header,
                    "from": from_address,
                    "subject": subject_header,
                    "body": clean_body,
                    "received_time": received_time,  # Added timestamp
                    "subscriber_email": "",
                    "group": [],
                }

                emails_batch.append(email_data)

            emails_batch = extract_emails_by_sender_type(emails_batch, no_reply_emails)

            # delete emails on seperate thread
            delete_thread = None
            if delete_email_ids:
                delete_thread = threading.Thread(
                    target=delete_emails, args=(delete_email_ids, ACCESS_TOKEN)
                )
                delete_thread.start()

            # classify emails
            if emails_batch:
                classified_emails = classify_emails(emails_batch, filters)

                classified_emails = {"data": classified_emails}

                logger.info(
                    f"Classified Emails: {classified_emails}",
                    LineFileProvider().get_file_info(),
                )

                # acquire lock, blocking -> true so if any function holds lock, it waits until released.

                if redis_lock.acquire(blocking=True):
                    try:
                        redis_client.hset(
                            "email_batches", batch_id, json.dumps(classified_emails)
                        )
                        logger.info(
                            "Batch Stored successfully",
                            LineFileProvider().get_file_info(),
                        )
                    except Exception as e:
                        logger.error(
                            f"Some error occured: {e}",
                            LineFileProvider().get_file_info(),
                        )

                    finally:  # finally always execute, even if error. Will make sure lock is released.
                        redis_lock.release()

            return delete_thread

        except Exception as e:
            logger.error(
                f"Error Processing emails: {e}", LineFileProvider().get_file_info()
            )
            raise
