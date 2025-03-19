import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from filter import classify_emails
from delete_emails import delete_emails
from get_filters import get_filters_and_delete_ids
import asyncio
from post_data import post_email_batch
from logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()


def process_emails(emails, filters, emails_to_delete, no_reply_emails, access_token):
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

        # delete emails without blocking event loop and classify emails on a seperate thread
        if delete_email_ids and emails_batch:

            delete_task = delete_emails(delete_email_ids, access_token)

            classify_task = asyncio.to_thread(classify_emails, emails_batch, filters)

            # Run both tasks at the same time and wait for both to finish
            delete_output, classified_emails = await asyncio.gather(
                delete_task, classify_task
            )

            classified_emails = {"data": classified_emails}

            logger.info(
                f"Deletion output: {delete_output}",
                LineFileProvider().get_file_info(),
            )
            logger.info(
                f"Classified Emails: {classified_emails}",
                LineFileProvider().get_file_info(),
            )

            # ----ADD to Redis here----

            # Trigger posting task

        return delete_email_ids

    except Exception as e:
        logger.error(
            f"Error Processing emails: {e}", LineFileProvider().get_file_info()
        )
        raise


def fetch_emails(email_url: str, access_token: str, no_reply_emails):
    """
    Fetch emails from Microsoft Graph API, handling pagination.

    Args:
            email_url (str): The initial URL to fetch emails.
            access_token (str): The access token for authenticating the API request.

    Returns:
            List[Dict]: A list of dictionaries containing email details.

    Raises:
            Exception: If the API request fails.
    """
    try:
        if not access_token:
            logger.error(
                "Failed to fetch active filters.", LineFileProvider().get_file_info()
            )
            return

        headers = {"Authorization": f"Bearer {access_token}"}

        next_url = email_url  # Start with the initial URL

        active_filters, emails_to_delete = get_filters_and_delete_ids()

        if not active_filters:
            logger.error(
                "Failed to fetch active filters.", LineFileProvider().get_file_info()
            )
            return

        while next_url:  # Keep iterating until there are no more pages
            response = requests.get(next_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                emails = data.get("value", [])

                if not emails:
                    logger.info("No emails found.", LineFileProvider().get_file_info())
                    return

                asyncio.run(
                    process_emails(
                        emails,
                        active_filters,
                        emails_to_delete,
                        no_reply_emails,
                        access_token,
                    )
                )

                next_url = data.get("@odata.nextLink", None)

            else:

                logger.error(
                    f"Failed to fetch emails: {response.json()}",
                    LineFileProvider().get_file_info(),
                )
                break

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", LineFileProvider().get_file_info())
        raise
