import threading
import requests
import redis
import json
from config import ACCESS_TOKEN
from token_refresher import TokenManager
from utils import generate_today_email_url
from process_emails import process_emails
from logger import JsJdLogger, LineFileProvider
from get_filters import get_filters_and_delete_ids

logger = JsJdLogger()



# Event objects
emails_fetched = threading.Event()
emails_stored = threading.Event()

# Define emails_batch globally
emails_batch = None


def fetch_emails(email_url: str, access_token: str, no_reply_emails):
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

    while next_url:

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
            process_emails(
                emails, active_filters, emails_to_delete, no_reply_emails, access_token
            )

            logger.info(
                "Sending batch to get stored...",
                LineFileProvider().get_file_info(),
            )
            # Sets event flag true to signal store email thread
            emails_fetched.set()

            # Waits for store emails event flag to become truee
            emails_stored.wait()

            # Sets store email event flag false
            emails_stored.clear()

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

    emails_batch = None

    emails_fetched.set()
    emails_stored.set()


# def store_emails():
#     """
#     Waits for emails to be fetched, then stores them in Redis.
#     """
#     batch_id = 0
#     while True:
#         batch_id += 1
#         # Wait until fetcher signals that emails are ready
#         emails_fetched.wait()


#         # Exit condition when no more emails
#         if emails_batch is None:
#             logger.info(
#                 "No more emails to store, exiting.", LineFileProvider().get_file_info()
#             )
#             emails_stored.set()
#             break

#         # redis_key = f"batch:{batch_id}"
#         redis_client.hset("email_batches", batch_id, json.dumps(emails_batch))

#         logger.info(
#             f"Stored {len(emails_batch)} emails in Redis.",
#             LineFileProvider().get_file_info(),
#         )

#         # Signal fetcher to fetch the next batch
#         emails_fetched.clear()
#         emails_stored.set()


if __name__ == "__main__":

    # Redis intialize
    redis_client = redis.Redis(
        host="localhost", port=6379, db=0, decode_responses=True
    )  # move to app.py?

    email_url = generate_today_email_url()

    access_token = ACCESS_TOKEN
    no_reply_emails = []

    # Initially, fetcher can start, storer waits
    emails_fetched.clear()
    emails_stored.clear()  # Allows fetcher to start first batch

    # Create threads
    fetch_thread = threading.Thread(
        target=fetch_emails,
        args=(email_url, access_token, no_reply_emails),
        name="fetch-mail",
    )
    store_thread = threading.Thread(target=store_emails, name="store-mail")

    # Start threads
    fetch_thread.start()
    store_thread.start()

    # Wait for both threads to complete
    fetch_thread.join()
    store_thread.join()

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
