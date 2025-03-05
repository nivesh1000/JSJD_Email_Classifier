import requests
from bs4 import BeautifulSoup
def fetch_today_emails(email_url: str, access_token: str) -> None:
    """
    Fetch emails from Microsoft Graph API for the current day and display their details.

    Args:
        email_url (str): The URL to fetch today's emails.
        access_token (str): The access token for authenticating the API request.

    Raises:
        Exception: If the API request fails.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(email_url, headers=headers)

        if response.status_code == 200:
            emails = response.json().get("value", [])
            if not emails:
                print("No emails found for today.")
                return

            for email in emails:
                print(f"Subject: {email.get('subject')}")
                print(
                    f"From: {email.get('from', {}).get('emailAddress', {}).get('address')}"
                )
                print(
                    f"To: {email.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', 'N/A')}"
                )
                print(f"Received: {email.get('receivedDateTime')}")

                # Extract and clean email body
                raw_body = email.get("body", {}).get("content", "No body available")
                clean_body = BeautifulSoup(raw_body, "html.parser").get_text()
                print(f"Body:\n{clean_body.strip()}")
                print("-" * 80)
        else:
            print("Failed to fetch emails:", response.json())

    except requests.exceptions.RequestException as e:
        print(f"🚨 Network Error: {e}")
        raise