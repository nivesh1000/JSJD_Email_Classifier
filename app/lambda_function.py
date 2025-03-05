import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config.config import (
    TENANT_ID,
    CLIENT_ID,
    CERT_THUMBPRINT,
    PRIVATE_KEY_PATH,
    MAILBOX_USER_ID,
    EMAIL_API_BASE_URL,
)
from Authenticator.authenticator import Authenticator
from Email_Fetcher.email_fetcher import fetch_today_emails
from datetime import datetime, timedelta

def generate_today_email_url(user_id: str) -> str:
    """
    Generate the URL to fetch emails received today using Microsoft Graph API with application permissions.

    Args:
        user_id (str): The ID or email of the user whose emails need to be fetched.

    Returns:
        str: The URL for fetching today's emails.
    """
    today = datetime.utcnow()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    # Format times in ISO 8601
    start_time = start_of_day.isoformat() + "Z"
    end_time = end_of_day.isoformat() + "Z"

    # Construct the URL for filtering emails by receivedDateTime using application permissions
    url = (
        f"https://graph.microsoft.com/v1.0/users/{user_id}/messages?"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        f"&$orderby=receivedDateTime DESC"
    )
    return url

def lambda_handler():
    """Main function to authenticate and fetch emails."""
    try:
        # Authenticate and get access token
        authenticator = Authenticator(TENANT_ID, CLIENT_ID, CERT_THUMBPRINT, PRIVATE_KEY_PATH)
        access_token = authenticator.acquire_token()
        print("Successfully authenticated!")

        # Generate the email URL for today's emails
        email_url = generate_today_email_url(MAILBOX_USER_ID)

        # Fetch today's emails using the generated URL and access token
        try:
            fetch_today_emails(email_url, access_token)
        except Exception as e:
            print(f"Error fetching today's emails: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    lambda_handler()
