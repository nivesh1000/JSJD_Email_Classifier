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

    while next_url:
        try:
            response = requests.get(next_url, headers=headers)
            response.raise_for_status()  # Raise HTTP errors

            data = response.json()  # Convert response to JSON

            # 🔍 **Print Debugging Information**
            print(f"\n🔍 DEBUG: Response Data Type: {type(data)}")  # Check if it's a dict
            print(f"🔍 DEBUG: Response Data Content: {json.dumps(data, indent=2)}")  # Pretty print

            if not isinstance(data, dict):
                print("⚠️ ERROR: Expected a dictionary but got something else. Exiting.")
                break  

            emails = data.get("value", [])
            print(f"🔍 DEBUG: Extracted Emails Type: {type(emails)}")  # Should be a list

            if not isinstance(emails, list):
                print("⚠️ ERROR: 'value' is not a list. Exiting.")
                break  

            for email in emails:
                headers = email.get("internetMessageHeaders", [])
                
                if not isinstance(headers, list):
                    print("⚠️ ERROR: 'internetMessageHeaders' is not a list. Skipping email.")
                    continue  

                to_header = subject_header = "Unknown"
                for header in headers:
                    if not isinstance(header, dict):
                        print("⚠️ ERROR: Expected dict in headers but got:", type(header))
                        continue  

                    if header.get("name", "").lower() == "to":
                        to_header = header.get("value", "Unknown")
                    if header.get("name", "").lower() == "subject":
                        subject_header = header.get("value", "Unknown")

                print(f"📧 To: {to_header}, Subject: {subject_header}")

            # 🔍 DEBUG: Print Next URL
            next_url = data.get("@odata.nextLink")
            print(f"🔍 DEBUG: Next URL: {next_url}")

            if not next_url:
                print("✅ Reached the last page of emails. Exiting.")
                break  

        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            break
        except json.JSONDecodeError:
            print("❌ ERROR: Response could not be parsed as JSON.")
            break
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            break

email_url = generate_last_3_days_email_url()
next_url_gen(email_url, access_token)
