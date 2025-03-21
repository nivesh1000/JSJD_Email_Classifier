import re
import json
import redis
import requests
import threading
from bs4 import BeautifulSoup
from app.filter import classify_emails
from app.Delete_Emails.delete_emails import delete_emails
from app.Logger.logger import JsJdLogger, LineFileProvider
from app.get_filters import get_filters_and_delete_ids
from app.Logger.logger import JsJdLogger, LineFileProvider
from app.Config.settings import ACCESS_TOKEN, redis_client, redis_lock
from app.events import fetch_emails, process_redis

# Logger initialize
logger = JsJdLogger()


class EmailProcessor:

    def fetch_emails(self, email_url: str, access_token: str, no_reply_emails):
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

            # wait for fetch emails event
            fetch_emails.wait()
            # reset event
            fetch_emails.clear()

            batch_id += 1

            try:
                response = requests.get(next_url, headers=headers)
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
                delete_thread = self.process_emails(
                    emails,
                    active_filters,
                    emails_to_delete,
                    no_reply_emails,
                    access_token,
                    redis_client,
                    batch_id,
                )

                # set process redis event
                process_redis.set()

                # wait for delete thread to end
                if delete_thread:
                    delete_thread.join()

                next_url = data.get("@odata.nextLink", None)
                logger.info(
                    f"Email batch fetched : {emails}", LineFileProvider().get_file_info()
                )
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

                # logger.info(
                #     f"Deletion output: {delete_task_output}",
                #     LineFileProvider().get_file_info(),
                # )
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
