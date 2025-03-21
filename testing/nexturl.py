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

# logger = EmailParser.get_logger()
import pytz  # Required for timezone conversion
def generate_today_email_url() -> str:
    """
    Generate the URL to fetch emails received today in CST (Central Standard Time)
    using Microsoft Graph API.

    Returns:
        str: The URL for fetching today's emails.
    """
    cst = pytz.timezone("America/Chicago")

    # Get the current date and time in CST
    now_cst = datetime.now(cst)

    # Set the start and end of the current day in CST
    start_of_day = now_cst.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    # Convert CST to UTC for API compatibility
    start_time = start_of_day.astimezone(pytz.utc).isoformat()
    end_time = end_of_day.astimezone(pytz.utc).isoformat()

    # Construct query parameters with proper encoding
    query_params = {
        "$top": "150",
        "$select": "toRecipients,from,subject,body,receivedDateTime,internetMessageHeaders",
        "$filter": f"receivedDateTime ge {start_time} and receivedDateTime le {end_time}",
        "$orderby": "receivedDateTime DESC"
    }

    # Build URL
    base_url = "https://graph.microsoft.com/v1.0/me/messages"
    url = f"{base_url}?{urlencode(query_params)}"

    return url



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
        "$top=10&"
       f"$select=toRecipients,from,subject,body,receivedDateTime,internetMessageHeaders&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        # f"$select=toRecipients,from,subject,body,receivedDateTime,internetMessageHeaders&"
    
    )

    return url


def next_url_gen(email_url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    next_url = email_url
    print(next_url)
    while next_url:
        response = requests.get(next_url, headers=headers)

        print(response.status_code)
        try:
            if response.status_code == 200:
                data = response.json()
                try: 
                    emails = data.get("value", [])
                    if not emails:
                        print("No emails found.")
                    else:
                        print("Emails found") 
                        try:
                            for email in emails:
                                pass
                                headersss= email.get("internetMessageHeaders", [])
                    #             print(headers)
                        except Exception as e:
                            print(e)        

                except Exception as e:
                    print(e)
                        
                next_url = data.get("@odata.nextLink", None)
                if next_url:
                    print(next_url)
                else:
                    print("No more emails to fetch.")    
            else:
                print("next_url_gen: Error fetching next URL")    
        except Exception as e:
            print(e)        

email_url=generate_last_3_days_email_url()
next_url_gen(email_url, access_token)