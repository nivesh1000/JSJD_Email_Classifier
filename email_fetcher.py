import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from filter import classify_emails

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

POST_API_URL = "https://staging.jsjdmedia.com/api/emails/store"


def fetch_emails(email_url: str, access_token: str, filters) -> List[Dict]:
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

    # POST_API_URL = os.environ["POST_API_URL"]
    try:
        while next_url:  # Keep iterating until there are no more pages
            response = requests.get(next_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
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
                        to_recipients[0].get("emailAddress", {}).get("address", "N/A")
                        if to_recipients
                        else "N/A"
                    )
                    subject = email.get("subject", "No subject")
                    raw_body = email.get("body", {}).get("content", "No body available")
                    clean_body = (
                        BeautifulSoup(raw_body, "html.parser").get_text().strip()
                    )
                    received_time = email.get("receivedDateTime", "Unknown Timestamp")

                    # Append the email dictionary to the list
                    email_list.append(
                        {
                            "email_id": email_id,
                            "to": to_address,
                            "from": from_address,
                            "subject": subject,
                            "body": clean_body,
                            "received_time": received_time,  # Added timestamp
                            "group": [],
                        }
                    )
                classified_emails = classify_emails(email_list, filters)
                classified_emails = {"data": classified_emails}
                logger.info(classified_emails)
                # Send classified emails via POST request
                if classified_emails:
                    try:
                        post_headers = {"Content-Type": "application/json"}
                        logger.info(
                            f"Sending {len(classified_emails)} classified emails to API..."
                        )

                        post_response = requests.post(
                            POST_API_URL, json=classified_emails, headers=post_headers
                        )
                        post_response.raise_for_status()

                        response_json = post_response.json()

                        if (
                            post_response.status_code == 201
                            and response_json.get("status") == "success"
                        ):
                            logger.info(
                                f"Successfully sent emails. API Response: {post_response.status_code} - {post_response.text}"
                            )
                            # Only update next_url if the response matches expected success criteria
                            next_url = data.get("@odata.nextLink", None)
                        else:
                            logger.warning(
                                f"Unexpected API response: {post_response.status_code} - {post_response.text}"
                            )
                            # time.sleep(2)  # Delay before retrying or proceeding further

                    except requests.RequestException as e:
                        logger.error(f"Failed to send emails: {str(e)}")
                        # time.sleep(2)  # Delay in case of a request failure

                    email_list = []
                # Check if there's a next page
                next_url = data.get("@odata.nextLink", None)
            else:
                logger.error(f"Failed to fetch emails: {response.json()}")
                break

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

    logger.info(f"total length: {len(classified_emails)}")
    return classified_emails
