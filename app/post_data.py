import json
import events
import requests
from config import redis_client, redis_lock, ACCESS_TOKEN

from logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()


class PostData:

    def redis_processor(self):
        """
        Function to get and update Redis data according to api response.
        """

        # wait signal for process redis
        while not events.shutdown.is_set():

            events.process_redis.wait()

            events.process_redis.clear()

            if redis_lock.acquire(blocking=True):
                try:
                    # check if redis has some data
                    batch_count = redis_client.hlen("email_batches")
                    if batch_count == 0:
                        logger.info(
                            "Redis is empty", LineFileProvider().get_file_info()
                        )

                        # set event to fetch emails since redis is empty
                        events.fetch_emails.set()

                    for batch_id in redis_client.hkeys("email_batches"):

                        batch_data = redis_client.hget("email_batches", batch_id)

                        if batch_data is not None:
                            emails_batch = json.loads(batch_data)
                            logger.info(
                                f"Posting batch: {batch_id}- {emails_batch[:50]} to api",
                                LineFileProvider().get_file_info(),
                            )
                        else:
                            logger.warning(f"Batch ID {batch_id} not found in Redis.")

                        response = self.post_email_batch_to_api(emails_batch)

                        if response is True:
                            logger.info(
                                f"Successfully sent email batch: {batch_id}",
                                LineFileProvider().get_file_info(),
                            )
                            logger.info(
                                f"Batch {batch_id} sent, deleting from redis",
                                LineFileProvider().get_file_info(),
                            )
                            redis_client.hdel("email_batches", batch_id)

                        elif response is False:
                            logger.error(
                                f"API failed for batch: {batch_id}",
                                LineFileProvider().get_file_info(),
                            )
                        # set event
                        events.fetch_emails.set()

                except Exception as e:
                    logger.error(
                        f"Error occured: {e}", LineFileProvider().get_file_info()
                    )

                finally:
                    redis_lock.release()

    def post_email_batch_to_api(self, classified_emails):
        """
        Send classified emails via POST request to the API.

        Args:
            classified_emails (dict): Dictionary containing classified email data.
        """

        # POST_API_URL = os.environ["POST_API_URL"]
        # POST_API_URL = "https://staging.jsjdmedia.com/api/emails/store"

        POST_API_URL = "https://webhook-test.com/e1f31828b5e96782a60cada71aee9f73"

        if not classified_emails.get("data"):
            logger.info(
                "No classified emails to send.", LineFileProvider().get_file_info()
            )
            return None

        try:
            post_headers = {"Content-Type": "application/json"}
            logger.info(
                f"Sending {len(classified_emails['data'])} classified emails to API...",
                LineFileProvider().get_file_info(),
            )

            post_response = requests.post(
                POST_API_URL, json=classified_emails, headers=post_headers
            )

            post_response.raise_for_status()

            return True

        except requests.RequestException as e:
            logger.error(
                f"Request exception while sending emails: {str(e)}",
                LineFileProvider().get_file_info(),
            )
            return False

