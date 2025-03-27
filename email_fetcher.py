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
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
import time
from token_refresher import TokenManager

def extract_email_by_sender_type(email,no_reply_emails):
    from_address=email['from']
    to_address = email['to']
    if from_address.startswith(tuple(no_reply_emails)):
        email_pattern = (
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        )
        subscriber_emails = re.findall(
            email_pattern, email['body'])
        
        filtered_subscriber_email=[subscriber_email for subscriber_email in subscriber_emails if subscriber_email not in [to_address, from_address]]
 
        email["subscriber_email"] = ", ".join(
                filtered_subscriber_email
            )
    return email 

def text_normalization(text):
    body = (
    BeautifulSoup(
        text, "html.parser")
    )
    body.prettify()
    for a_tag in body.find_all("a"):
        a_tag.decompose()
    return body.get_text().strip()

logger = EmailParser.get_logger()
import json

def post_batch(classified_emails):
    """
    Send classified emails via POST request to the API.

    Args:
        classified_emails (dict): Dictionary containing classified email data.
    """
    # POST_API_URL = os.environ["POST_API_URL"]
    # POST_API_URL = "https://staging.jsjdmedia.com/api/emails/store"
    POST_API_URL = "https://webhook.site/c587be7a-4d35-496c-a52e-4b6f209b2c5c"
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
    email_url: str, filters, del_emails, no_reply_emails
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
    token_manager = TokenManager()
    token_expiry_threshold = 55 * 60  # 55 minutes
    # Refresh and update tokens
    ACCESS_TOKEN=token_manager.refresh_tokens()
    if not ACCESS_TOKEN:
        return {"error": "Failed to retrieve ACCESS_TOKEN"}
    
    token_issued_time = time.time()
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    next_url = email_url  # Start with the initial URL
    email_list = []  # To store email data
    classified_emails = []  # To store classified emails
    deletion_ids = []
    user_email_address = os.environ["USER_EMAIL_ADDRESS"]
    try:
        while next_url:  # Keep iterating until there are no more pages
            # print("1 iteration---------------------------------------------")
            response = requests.get(next_url, headers=headers)
            current_time = time.time()-token_issued_time
            # print(current_time)
            if current_time > token_expiry_threshold:
                ACCESS_TOKEN=token_manager.refresh_tokens()
                if not ACCESS_TOKEN:
                    return {"error": "Failed to retrieve ACCESS_TOKEN"}
                token_issued_time = time.time()
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
                    get_headers= email.get("internetMessageHeaders", [])
                    for get_header in get_headers:
                        if get_header['name'].lower() == 'to':
                            to_header = get_header['value']
                            start = to_header.find('<')
                            end = to_header.find('>')
                            to_header=to_header[start + 1:end]
                        if get_header['name'].lower() == 'subject':
                            subject_header = get_header['value']
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


                    clean_body=text_normalization(raw_body)
                    received_time = email.get(
                        "receivedDateTime", "Unknown Timestamp")
                    if from_address in del_emails:
                        deletion_ids.append(email_id)
                        continue
 
                    if not clean_body and not subject:
                        continue
                    
                    if from_address == user_email_address:
                        continue
 

                    email_data = {
                        "email_id": email_id,
                        "to": to_header,
                        "from": from_address,
                        "subject": subject_header,
                        "body": clean_body,
                        # "raw_body": raw_body,
                        "received_time": received_time,
                        "subscriber_email": "",
                        "group": [],
                        }
                    # print(raw_body)
                    # if subject == "Your Communication Preferences Have Been Updated":
                    #     print(raw_body)
                    #     exit(1)

                    
                    
                    email_data = extract_email_by_sender_type(email_data,no_reply_emails)

                    # Append the email dictionary to the list
                    email_list.append(email_data
                        
                    )
                # print(email_list)
                delete_response = {}
                if deletion_ids:
                    pass
                    # delete_emails(deletion_ids, access_token)
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
    # print(classified_emails)
    return classified_emails