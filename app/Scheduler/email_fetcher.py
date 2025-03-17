import requests
from typing import Generator, List, Dict
from bs4 import BeautifulSoup
from logger import get_logger
from Email_Deletion.delete_emails import delete_emails
import re

logger = get_logger()

def fetch_emails(
    email_url: str, access_token: str, del_emails
) -> Generator[List[Dict], None, None]:
    """
    Fetch emails from Microsoft Graph API, handling pagination.

    Args:
        email_url (str): The initial URL to fetch emails.
        access_token (str): The access token for authenticating the API request.

    Yields:
        List[Dict]: A list of dictionaries containing email details.

    Raises:
        Exception: If the API request fails.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    next_url = email_url  # Start with the initial URL
    email_list = []  # To store email data
    classified_emails = []  # To store classified emails
    deletion_ids = []

    try:
        while next_url:  # Keep iterating until there are no more pages
            response = requests.get(next_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                emails = data.get("value", [])

                if not emails:
                    logger.info("No emails found.")
                    break

                # Process the current batch of emails
                for email in emails:
                    email_id = email.get("id", "Unknown ID")
                    from_address = (
                        email.get("from", {})
                        .get("emailAddress", {})
                        .get("address", "N/A")
                    )
                    to_recipients = email.get("toRecipients", [])
                    to_address = (
                        to_recipients[0].get(
                            "emailAddress", {}).get("address", "N/A")
                        if to_recipients
                        else "N/A"
                    )
                    subject = email.get("subject", "")
                    raw_body = email.get("body", {}).get("content", "")
                    received_time = email.get(
                        "receivedDateTime", "Unknown Timestamp")

                    if from_address in del_emails:
                        deletion_ids.append(email_id)
                        continue

                    if not raw_body and not subject:
                        continue

                    email_list.append(
                        {
                            "email_id": email_id,
                            "to": to_address,
                            "from": from_address,
                            "subject": subject,
                            "body": raw_body,
                            "raw_body": raw_body,
                            "received_time": received_time,
                            "subscriber_email": "",
                            "group": [],
                        }
                    )

                if deletion_ids:
                    delete_emails(deletion_ids, access_token)

                yield email_list
                email_list = []  # Clear list only on success

                # Move to next page
                next_url = data.get("@odata.nextLink", None)

            else:
                logger.error(f"Failed to fetch emails: {response.json()}")
                break

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
