import threading
import requests
import redis
import json
import time
from app.config import ACCESS_TOKEN
from app.token_refresher import TokenManager
from app.utils import generate_today_email_url
from app.logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()

# Redis intialize
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Event objects
emails_fetched = threading.Event()
emails_stored = threading.Event()


def fetch_emails(email_url: str, access_token: str, no_reply_emails):
	"""
	Fetch emails from Microsoft Graph API in batches. After fetching, signal thread 2.
	"""

	if not access_token:
		print("Access token is missing.")
		return

	headers = {"Authorization": f"Bearer {access_token}"}
	next_url = email_url

	while next_url:
		try:
			response = requests.get(next_url, headers=headers)

			if response.status_code == 200:
				data = response.json()
				emails = data.get("value", [])

				if not emails:
					logger.error("No emails found.", LineFileProvider().get_file_info())
					break

				# Store fetched emails in shared buffer
				global emails_batch
				emails_batch = emails
				
				logger.forensic(emails,LineFileProvider().get_file_info())

				# Signal thread 2- store emails
				emails_fetched.set()

				# Wait for thread 2 to finish
				emails_fetched.wait()
				emails_fetched.clear()

				# Update next_url for pagination
				next_url = data.get("@odata.nextLink", None)

		except requests.RequestException as e:
			print(f"Fetcher: Failed to fetch emails: {e}")
			break


def store_emails():
    """
    Waits for emails to be fetched, then stores them in Redis.
    """

    while True:
        # Wait until Thread 1 signals that emails are ready
        emails_fetched.wait()

        global emails_batch

        if emails_batch:
            # Store emails in Redis
            redis_client.set("emails", json.dumps(emails_batch))

            logger.info(
                f"Stored emails in Redis: {emails_batch}",
                LineFileProvider().get_file_info(),
            )

            # Clear the buffer after storing
            emails_batch = []

        # Allow Thread 1 to fetch the next batch
        emails_fetched.clear()
        emails_stored.set()


if __name__ == "__main__":

    email_url = generate_today_email_url()

    access_token = ACCESS_TOKEN
    no_reply_emails = []

    # Create threads
    fetch_thread = threading.Thread(
        target=fetch_emails,
        args=(email_url, access_token, no_reply_emails),
        name="fetch-mail",
    )
    store_thread = threading.Thread(target=store_emails, name="store-mail")

    # Start threads
    store_thread.start()
    fetch_thread.start()

    fetch_thread.join()
    store_thread.join()
