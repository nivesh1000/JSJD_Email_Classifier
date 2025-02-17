import os
from dotenv import load_dotenv
from Authenticator.authenticator import Authenticator
from Email_Fetcher.email_fetcher import fetch_emails_by_page

# Load environment variables
load_dotenv("config/.env")

def lambda_handler():
    """Main function to authenticate and fetch emails."""
    # Load credentials from .env
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    cert_thumbprint = os.getenv("CERT_THUMBPRINT")
    private_key_path = os.getenv("PRIVATE_KEY_PATH")
    user_email = os.getenv("MAILBOX_USER_ID")
    email_api_base_url = os.getenv("EMAIL_API_BASE_URL", "https://graph.microsoft.com/v1.0")
    email_url = f"{email_api_base_url}/users/{user_email}/messages?$top=10&$orderby=receivedDateTime DESC"
    try:
        # Authenticate and get access token
        authenticator = Authenticator(tenant_id, client_id, cert_thumbprint, private_key_path)
        access_token = authenticator.acquire_token()
        print("Successfully authenticated!")

        # Fetch emails page by page
        current_url = email_url
        while current_url:
            results = fetch_emails_by_page(access_token, user_email, current_url)

            # Process emails on the current page
            emails = next(results, [])
            for email in emails:
                print(f"Subject: {email.get('subject')}")
                # Additional processing can be added here

            # Get the next page URL
            current_url = next(results, None)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    lambda_handler()
