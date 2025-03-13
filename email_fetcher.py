import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from filter import classify_emails
from delete_emails import delete_emails
from logger import EmailParser
import re
from bs4 import BeautifulSoup

logger = EmailParser.get_logger()


def post_batch(classified_emails):
    """
    Send classified emails via POST request to the API.

    Args:
        classified_emails (dict): Dictionary containing classified email data.
    """
    # POST_API_URL = os.environ["POST_API_URL"]
    # POST_API_URL = "https://staging.jsjdmedia.com/api/emails/store"
    
    if not classified_emails.get("data"):
        logger.info("No classified emails to send.")
        return False, 0, "No data to send"

    try:
        post_headers = {"Content-Type": "application/json"}
        logger.info(f"Sending {len(classified_emails['data'])} classified emails to API...")

        post_response = requests.post(
            POST_API_URL, json=classified_emails, headers=post_headers
        )
        status_code = post_response.status_code

        # Try to parse JSON
        try:
            response_json = post_response.json()
            if status_code == 201 and response_json.get("status") == "success":
                logger.info(f"Successfully sent emails. Status: {status_code}")
                return True, status_code, ""
            error_msg = response_json.get("error", "Unknown error")
        except ValueError:
            error_msg = "Invalid JSON response"

        logger.error(
            f"Failed to send emails. Status: {status_code}, Error: {error_msg}"
        )
        return False, status_code, error_msg

    except requests.RequestException as e:
        logger.error(f"Request exception while sending emails: {str(e)}")
        return False, 0, str(e)


def fetch_emails(
    email_url: str, access_token: str, filters, del_emails, no_reply_emails
) -> List[Dict]:
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
    headers = {"Authorization": f"Bearer {access_token}"}
    next_url = email_url  # Start with the initial URL
    email_list = []  # To store email data
    classified_emails = []  # To store classified emails
    deletion_ids = []
    # POST_API_URL = os.environ["POST_API_URL"]
    try:
        while next_url:  # Keep iterating until there are no more pages
            response = requests.get(next_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # print(data)
                emails = data.get("value", [])

                if not emails:
                    logger.info("No emails found.")
                    return email_list

                # Process the current batch of emails
                for email in emails:
                    # logger.info(f"Processing email: {email}")
                    # Extract required fields
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
                    # print(raw_body)
                    body = (
                        BeautifulSoup(
                            raw_body, "html.parser")
                    )
                    for a_tag in body.find_all("a"):
                        a_tag.decompose()
                    clean_body = body.get_text().strip().replace("\xa0", "")
                    received_time = email.get(
                        "receivedDateTime", "Unknown Timestamp")
                    if from_address in del_emails:
                        deletion_ids.append(email_id)
                        continue

                    if not clean_body and not subject:
                        continue
                    # Append the email dictionary to the list
                    email_list.append(
                        {
                            "email_id": email_id,
                            "to": to_address,
                            "from": from_address,
                            "subject": subject,
                            "body": clean_body,
                            "received_time": received_time,  # Added timestamp
                            "subscriber_email": "",
                            "group": [],
                        }
                    )
                    if from_address.startswith(tuple(no_reply_emails)):
                        email_pattern = (
                            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                        )
                        subscriber_emails = re.findall(
                            email_pattern, clean_body)
                        email_list[-1]["subscriber_email"] = ", ".join(
                            subscriber_emails
                        )
                if deletion_ids:
                    delete_emails(deletion_ids, access_token)
                classified_emails = classify_emails(email_list, filters)

                classified_emails = {"data": classified_emails}

                logger.info(classified_emails)

                # Send classified emails via POST request
                success, status_code, error_msg = post_batch(classified_emails)
                if success:
                    logger.info(
                        f"Emails sent successfully. Status: {status_code}")
                    email_list = []  # Clear list only on success
                    # Move to next page
                    next_url = data.get("@odata.nextLink", None)
                else:
                    logger.error(f"Failed to send emails. Status: {status_code}, Error: {error_msg}")
                    next_url = data.get(
                        "@odata.nextLink", None
                    )  # Still proceed to next page

            else:
                logger.error(f"Failed to fetch emails: {response.json()}")
                break

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

    # logger.info(f"total length: {len(classified_emails)}")
    return classified_emails
