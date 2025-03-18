from Token_Refresher.token_refresher import TokenManager
from API.email_rules import fetch_filter_and_deletion_emails
from logger import get_logger
from Utilities.url_generator import generate_today_email_url, generate_last_3_days_email_url
from Utilities.json_reader import read_json_file
from Scheduler.email_fetcher import fetch_emails
from dotenv import load_dotenv
import os
from Scheduler.filter import classify_emails
from Utilities.subscriber_email_finder import extract_emails_by_sender_type
from Utilities.text_normalization import body_normalization

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

logger=get_logger()

def no_reply_variation(no_reply_obj):
    no_reply_variations = []

    for sample in no_reply_obj["no_reply_variations"]:
        index = sample.find("@")
        if index != -1:  # Ensure "@" exists
            no_reply_variations.append(sample[:index])
    return no_reply_variations        


# Function that fetches, filters, groups, and posts emails
def fetch_process_post_emails():
    token_manager = TokenManager()
    try:
        token_manager.refresh_tokens()
        logger.info("Refreshed tokens successfully")
    except Exception as e:
        logger.error(f"Error during token refresh: {e}")

    # Fetch filters and emails to delete
    filters_and_deletion_emails = fetch_filter_and_deletion_emails()
    if not filters_and_deletion_emails:
        logger.error("Error fetching filters and deletion emails")
    filters= filters_and_deletion_emails["filters"]
    delete_emails = filters_and_deletion_emails["deletion_emails"]
    email_url = generate_today_email_url()
    no_reply_obj = read_json_file("app/Utilities/no_reply_variations.json")
    no_reply_variations = no_reply_variation(no_reply_obj)
    # c=1
    for email_batch in fetch_emails(email_url, ACCESS_TOKEN, delete_emails):
        # print('batch recieved------------------------ ',c)
        # print(email_batch[0])

        email_batch=extract_emails_by_sender_type(email_batch, no_reply_variations)
        email_batch = body_normalization(email_batch)
        filtered_emails = classify_emails(email_batch, filters)
        # print('batch filtered------------------------ ',c)
        # print(email_batch)
        # c+=1

# fetch_process_post_emails()