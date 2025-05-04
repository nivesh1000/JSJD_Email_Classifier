import os
import time 
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from filter import classify_emails
# from enhanced_filter import classify_emails
from logger import EmailParser
import re
from bs4 import BeautifulSoup
import time
from token_refresher import TokenManager
import json
from unidecode import unidecode
from datetime import datetime, timedelta, timezone

def subtract_hours_from_iso(timestamp_str: str, hours: int = 5) -> str:
    # Parse the input string assuming it's in UTC (ends with 'Z')
    dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=timezone.utc)
    
    # Subtract the given number of hours
    new_dt = dt - timedelta(hours=hours)
    
    # Return in the same ISO 8601 format with 'Z'
    return new_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def send_bounced_email(bounced_emails_data: list[dict]) -> tuple[int, dict]:
    """
    Sends bounced email data to the given API endpoint.

    Args:
        data (list[dict]): A list of dictionaries containing bounced email data.

    Returns:
        tuple: (status_code, response_json)
    """
    # url = 'https://staging.jsjdmedia.com/api/emails/store-bounced-email'
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "data": bounced_emails_data
    }

    try:
        logger.info(f"Sending {len(payload['data'])} bounced emails to API...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return 500, {"error": str(e)}

def extract_email_from_body(body):
    """
    Extracts the first email address found in the body of the bounced email address.
    """
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.findall(email_pattern, body)
    if match:
        return list(set(match))
    else:
        return None

def extract_email_by_sender_type(email,no_reply_emails):
    """
    Extracts email addresses from the body of the email if the sender is a no-reply address.
    """
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

def multi_space_remover(text):
    return re.sub(r'\s+', ' ', text)


def text_normalization(text):
    # Parse the HTML content
    soup = BeautifulSoup(text, "html.parser")
    
    # Remove all <a> tags (links)
    for a_tag in soup.find_all("a"):
        a_tag.decompose()
    
    # Extract text while preserving original whitespace
    result = soup.get_text(separator=" ", strip=False)
    
    # Use unidecode to transliterate Unicode to ASCII
    result = unidecode(result)
    final_body = multi_space_remover(result)
    
    return final_body.strip(" ")

logger = EmailParser.get_logger()
import json

def post_batch(classified_emails):
    """
    Send classified emails via POST request to the API.

    Args:
        classified_emails (dict): Dictionary containing classified email data.
    """
    # print("classified_emails",classified_emails)
    # POST_API_URL = os.environ["POST_API_URL"]
    POST_API_URL = "https://staging.jsjdmedia.com/api/emails/store"
    # POST_API_URL = "https://webhook-test.com/b0c15df5360d56622509e42fa4dc3552"
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
    email_url: str, filters, del_emails, no_reply_emails, bounced_emails_info
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
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
        "Prefer": 'IdType="ImmutableId"'
        }
    next_url = email_url  # Start with the initial URL
    email_list = []  # To store the data of the email which will be filtered
    bounced_emails_data = []  # To store the bounced email list which wont be filtered
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
                    subject = email.get("subject", "")
                    raw_body = email.get("body", {}).get("content", "")


                    clean_body=text_normalization(raw_body)
                    received_time = email.get(
                        "receivedDateTime", "Unknown Timestamp")
                    received_time = subtract_hours_from_iso(received_time)
                    if from_address in del_emails:
                        deletion_ids.append(email_id)
                        continue
                    # bounced_email_list = list(bounced_email_info.values())
                    bounced_emails_before = len(bounced_emails_data)

                    for bounced_email_id, bounced_email_address in bounced_emails_info.items():
                        if from_address == bounced_email_address:

                            body_from_address = extract_email_from_body(raw_body)
                            if body_from_address is not None:
                                bounced_emails_data.append({
                                    "email_id": email_id,
                                    "to": to_header,
                                    "from": body_from_address,
                                    "subject": subject_header,
                                    "body": clean_body,
                                    "received_time": received_time,
                                    "subscriber_email": "",
                                    "bounced_email_source_id": bounced_email_id,
                                })
                            continue
                    bounced_emails_after = len(bounced_emails_data)    

                    # print("previous length", bounced_emails_before)
                    # print("current length", bounced_emails_after)
                    # print("bounced_emails_data after", bounced_emails_data)

                    if bounced_emails_before < bounced_emails_after:
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
                if classified_emails:
                    classified_emails = {"data": classified_emails}
                    
    
                    logger.info(classified_emails)
    
                    # Send classified emails via POST request
                    success, status_code, error_msg = post_batch(classified_emails)
                    if success:
                        logger.info(
                            f"Emails sent successfully. Status: {status_code}")
                        print("classified emails_sent successfully")
                        print(classified_emails)
                        email_list = []  # Clear list only on success
                        # Move to next page
                        
                    else:
                        logger.error(f"Failed to send emails. Status: {status_code}, Error: {error_msg}")

                if bounced_emails_data:
                    bounced_status_code, bounced_response = send_bounced_email(bounced_emails_data)    
                    if bounced_status_code == 201:
                        logger.info(
                            f"Bounced emails sent successfully. Status: {bounced_status_code}")
                        print("bounced_emails_sent successfully")
                        print(bounced_emails_data)
                        bounced_emails_data = []  # Clear list only on success
                    else:
                        logger.error(f"Failed to send bounced emails. Status: {bounced_status_code}, Error: {bounced_response}")

                next_url = data.get("@odata.nextLink", None)    
 
            else:
                logger.error(f"Failed to fetch emails: {response.json()}")
                break
 
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    # print(classified_emails)
    return classified_emails