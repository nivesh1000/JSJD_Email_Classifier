import os
import json
# from token_refresher import TokenManager
from datetime import datetime, timedelta
# from email_fetcher import fetch_emails
# from filter import classify_emails
# from delete_emails import delete_emails
# from get_filters import fetch_groups
import requests
# from logger import EmailParser
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Load environment variables
load_dotenv()

# Credentials
access_token = os.getenv("ACCESS_TOKEN")

def generate_last_3_days_email_url() -> str:
    """
    Generate the URL to fetch emails received in the last 3 days using Microsoft Graph API,
    with timestamps in CST (Central Standard Time).

    Returns:
        str: The URL for fetching emails from the last 3 days.
    """
    cst = ZoneInfo('America/Chicago')  # CST timezone
    today = datetime.now().astimezone(cst)
    start_of_range = today - timedelta(days=1)  # 3 days ago
    end_of_range = today

    # Format times in ISO 8601 without 'Z' since they are no longer in UTC
    start_time = start_of_range.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()

    end_time = end_of_range.isoformat()

    # Construct the URL for filtering emails by receivedDateTime
    url = (
        "https://graph.microsoft.com/v1.0/me/mailFolders/AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZAAuAAAAAACmpm51Pxn4S6hR8gC58iFDAQCY28Rccs6eQ6vSFsjSkG-hAAAAAAEMAAA=/messages?"
        "$top=5&"
      
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        # f"$select=toRecipients,from,subject,body,receivedDateTime,internetMessageHeaders&"
    
    )

    return url



def next_url_gen(email_url, access_token):

    headers = {"Authorization": f"Bearer {access_token}"}
    next_url = email_url
    print(next_url)
    while next_url:
        print("before response")
        response = requests.get(next_url, headers=headers)
        # import time
        # time.sleep(5)
        print(response.status_code)
        print("after rsponse")
        if response.status_code == 200:
            data = response.json()
            next_url = data.get("@odata.nextLink", None)
            print(next_url)
        else:
            print("next_url_gen: Error fetching next URL")
            print(response.status_code)   

email_url=generate_last_3_days_email_url()
next_url_gen(email_url, access_token)