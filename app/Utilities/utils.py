import re
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def read_json_file(file_path):
    """
    Reads a JSON file and returns the data as a Python object.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or list: The data loaded from the JSON file.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def extract_emails_by_sender_type(emails, no_reply_variations):
    for email in emails:
        from_address = email["from"]
        to_address = email["to"]

        body = email["body"]
        if from_address.startswith(tuple(no_reply_variations)):
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            subscriber_emails = re.findall(email_pattern, body)
            filtered_subscriber_email = [
                subscriber_email
                for subscriber_email in subscriber_emails
                if subscriber_email not in [to_address, from_address]
            ]

            email["subscriber_email"] = ", ".join(filtered_subscriber_email)
    return emails


def body_normalization(emails):
    for email in emails:
        body = BeautifulSoup(email["body"], "html.parser")
        body.prettify()
        for a_tag in body.find_all("a"):
            a_tag.decompose()
        clean_body = body.get_text().strip()

        email["body"] = clean_body
    logger.info("Email batch body normalized successfully!!")
    return emails


def generate_today_email_url() -> str:
    """
    Generate the URL to fetch emails received today using Microsoft Graph API.

    Returns:
        str: The URL for fetching today's emails.
    """
    today = datetime.utcnow()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    # Format times in ISO 8601
    start_time = start_of_day.isoformat() + "Z"
    end_time = end_of_day.isoformat() + "Z"

    # Construct the URL for filtering emails by receivedDateTime
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages?"
        f"$top=100&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        f"&$orderby=receivedDateTime DESC"
    )
    # url="https://graph.microsoft.com/v1.0/me/messages?$filter=receivedDateTime ge 2025-02-20T00:00:00Z and receivedDateTime le 2025-02-20T23:59:59Z&$orderby=receivedDateTime DESC"
    return url


def generate_all_email_url() -> str:
    """
    Generate the URL to fetch all emails using Microsoft Graph API.

    Returns:
        str: The URL for fetching all emails.
    """
    try:
        url = (
            "https://graph.microsoft.com/v1.0/me/messages?"
            "$top=100&"
            "$orderby=receivedDateTime"
        )
        return url
    except Exception as e:
        logger.error(f"Error generating all email URL: {e}")
        return ""


def generate_last_3_days_email_url() -> str:
    """
    Generate the URL to fetch emails received in the last 3 days using Microsoft Graph API.

    Returns:
        str: The URL for fetching emails from the last 3 days.
    """
    today = datetime.utcnow()
    start_of_range = today - timedelta(days=3)  # 3 days ago
    end_of_range = today

    # Format times in ISO 8601
    start_time = (
        start_of_range.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        + "Z"
    )
    end_time = end_of_range.isoformat() + "Z"

    # Construct the URL for filtering emails by receivedDateTime
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages?"
        f"$top=100&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        f"&$orderby=receivedDateTime DESC"
    )

    return url


def no_reply_variation():
    
    no_reply_obj = read_json_file("app/Utilities/no_reply_variations.json")
    
    no_reply_variations = []

    for sample in no_reply_obj["no_reply_variations"]:
        index = sample.find("@")
        if index != -1:  # Ensure "@" exists
            no_reply_variations.append(sample[:index])
    return no_reply_variations
