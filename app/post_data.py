import time
import json
import requests

from app.events import process_redis, fetch_emails, shutdown
from app.Config.settings import redis_client, redis_lock, ACCESS_TOKEN

from app.Logger.logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()


class PostData:

    def redis_processor(self):
        """
        Function to get and update Redis data according to api response.
        """

        # wait signal for process redis
        while not shutdown.is_set():

            process_redis.wait()

            process_redis.clear()

            if redis_lock.acquire(blocking=True):
                try:
                    # check if redis has some data
                    if not (_ := redis_client.hlen("email_batches")):
                        logger.info(
                            "Redis is empty", LineFileProvider().get_file_info()
                        )

                        # set event to fetch emails since redis is empty
                        fetch_emails.set()

                    for batch_id in redis_client.hkeys("email_batches"):

                        batch_data = redis_client.hget("email_batches", batch_id)

                        if batch_data is not None:
                            emails_batch = json.loads(batch_data)
                            logger.forensic(
                                f"Posting batch: {batch_id}- {emails_batch} to api",
                                LineFileProvider().get_file_info(),
                            )
                        else:
                            logger.warning(
                                f"Batch ID {batch_id} not found in Redis.",
                                LineFileProvider().get_file_info(),
                            )

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
                        fetch_emails.set()

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

        MAX_RETRIES = 5
        INITIAL_DELAY = 1

        if not classified_emails.get("data"):
            logger.info(
                "No classified emails to send.", LineFileProvider().get_file_info()
            )
            return None

        post_headers = {"Content-Type": "application/json"}

        logger.info(
            f"Sending {len(classified_emails['data'])} classified emails to API...",
            LineFileProvider().get_file_info(),
        )
        retry_count = 0

        while retry_count < MAX_RETRIES:
            try:
                """Using with here:
                Without with, each failed attempt could leave an open connection hanging until the next retry or garbage collection.
                Using with ensures each request’s connection closes immediately."""

                with requests.post(
                    POST_API_URL, json=classified_emails, headers=post_headers
                ) as post_response:

                    if post_response.status_code == 429:
                        retry_after = post_response.headers.get("Retry-After")
                        if retry_after:
                            delay = float(retry_after)
                        else:
                            delay = INITIAL_DELAY * (2**retry_count)

                        logger.warning(
                            f"Rate limit exceeded. Retrying after {delay} seconds... "
                            f"Attempt {retry_count + 1}/{MAX_RETRIES}",
                            LineFileProvider().get_file_info(),
                        )
                        time.sleep(delay)
                        retry_count += 1
                        continue

                    post_response.raise_for_status()

                    return True

            except requests.RequestException as e:
                logger.error(
                    f"Request exception while sending emails: {str(e)}",
                    LineFileProvider().get_file_info(),
                )
                return False
