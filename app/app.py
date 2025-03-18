import os
import json
import redis
import events
import threading
from logger import JsJdLogger, LineFileProvider
from email_processor import EmailProcessor
from post_data import PostData
from utils import generate_today_email_url, read_json_file
from config import ACCESS_TOKEN

logger = JsJdLogger()

email_processor = EmailProcessor()
post_data = PostData()


def main():
    "Entry Point"

    email_url = generate_today_email_url()

    no_reply_obj = read_json_file("no_reply_variations.json")

    no_reply_emails = []

    for sample in no_reply_obj["no_reply_variations"]:
        index = sample.find("@")
        if index != -1:  # Ensure "@" exists
            no_reply_emails.append(sample[:index])

    # Create Threads
    fetch_emails_thread = threading.Thread(
        target=email_processor.fetch_emails,
        args=(email_url, ACCESS_TOKEN, no_reply_emails),
        name="fetch-mail",
    )

    redis_processor_thread = threading.Thread(target=post_data.redis_processor)

    # Start Threads
    redis_processor_thread.start()
    fetch_emails_thread.start()

    #

    # Wait for threads to end
    fetch_emails_thread.join()

    events.shutdown.set()
    redis_processor_thread.join()

    logger.info("All batches processed.", LineFileProvider().get_file_info())


if __name__ == "__main__":
    main()
