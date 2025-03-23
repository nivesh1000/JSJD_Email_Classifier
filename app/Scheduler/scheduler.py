import threading

from app.events import shutdown

from app.post_data import PostData

from app.Config.settings import ACCESS_TOKEN

from app.email_processor import EmailProcessor


from app.Logger.logger import JsJdLogger, LineFileProvider

from app.Token_Refresher.token_refresher import TokenManager


from app.Utilities.utils import (
    generate_today_email_url,
    no_reply_variation,
)
from app.events import set_initial_events

email_processor = EmailProcessor()
post_data = PostData()

# Logger initialize
logger = JsJdLogger()


# Function that fetches, filters, groups, and posts emails
def fetch_process_post_emails():

    set_initial_events()

    # check thread id
    current_thread = threading.current_thread()
    logger.forensic(
        f"Starting fetch_process_post_emails in thread {current_thread.name} (ID: {current_thread.ident})",
        LineFileProvider().get_file_info(),
    )

    token_manager = TokenManager()
    try:
        token_manager.refresh_tokens()
        logger.info("Refreshed tokens successfully", LineFileProvider().get_file_info())
    except Exception as e:
        logger.error(
            f"Error during token refresh: {e}", LineFileProvider().get_file_info()
        )

    email_url = generate_today_email_url()

    no_reply_emails = no_reply_variation()

    # Create Threads
    fetch_emails_thread = threading.Thread(
        target=email_processor.fetch_emails,
        args=(email_url, no_reply_emails),
        name="fetch-mail",
    )

    redis_processor_thread = threading.Thread(target=post_data.redis_processor)

    # Start Threads
    redis_processor_thread.start()
    fetch_emails_thread.start()

    # Wait for threads to end
    fetch_emails_thread.join()

    shutdown.set()
    redis_processor_thread.join()


    logger.info("All batches processed.", LineFileProvider().get_file_info())
