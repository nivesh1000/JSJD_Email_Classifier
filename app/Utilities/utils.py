import re
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from unidecode import unidecode
from zoneinfo import ZoneInfo


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


# def body_normalization(emails):
#     for email in emails:
#         body = BeautifulSoup(email["body"], "html.parser")
#         body.prettify()
#         for a_tag in body.find_all("a"):
#             a_tag.decompose()
#         clean_body = body.get_text().strip()

#         email["body"] = clean_body
#     logger.info("Email batch body normalized successfully!!")
#     return emails


def text_normalization(text):
    # Parse the HTML content
    soup = BeautifulSoup(text, "html.parser")
    
    # Remove all <a> tags (links)
    for a_tag in soup.find_all("a"):
        a_tag.decompose()
    
    # Extract text while preserving original whitespace
    result = soup.get_text(separator="", strip=False)
    
    # Use unidecode to transliterate Unicode to ASCII
    result = unidecode(result)
    
    return repr(result)

def generate_today_email_url() -> str:
    """
    Generate the URL to fetch emails received today using Microsoft Graph API.

    Returns:
        str: The URL for fetching today's emails.
    """
    cst = ZoneInfo('America/Chicago')  # CST timezone
    today = datetime.now().astimezone(cst)
    start_of_range = today - timedelta(days=1) # set no. of days to fetch emails
    end_of_range = today

    # Format times in ISO 8601 without 'Z' since they are no longer in UTC
    start_time = start_of_range.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()

    end_time = end_of_range.isoformat()

    # Construct the URL for filtering emails by receivedDateTime
    url = (
        "https://graph.microsoft.com/v1.0/me/mailFolders/AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZAAuAAAAAACmpm51Pxn4S6hR8gC58iFDAQCY28Rccs6eQ6vSFsjSkG-hAAAAAAEMAAA=/messages?"
        "$top=20&"
        f"$select=toRecipients,from,subject,body,receivedDateTime,internetMessageHeaders&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
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
