import requests

def fetch_emails_by_page(access_token: str, user_id: str, email_url: str):
    """
    Fetches emails from a user's mailbox for the given page URL.
    Yields the emails of the current page.

    Args:
        access_token (str): The access token for authentication.
        user_id (str): The email ID of the mailbox to query.
        email_url (str): The Graph API URL for fetching emails (e.g., first page or next page).

    Yields:
        list: A list of emails from the current page.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(email_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            emails = data.get("value", [])
            yield emails  # Yield the emails from the current page

            # Get the next page URL
            next_url = data.get("@odata.nextLink")
            if next_url:
                yield next_url  # Yield the next page URL
        else:
            print(f"Failed to fetch emails: {response.status_code}, {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
