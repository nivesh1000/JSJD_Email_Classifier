from authenticator import authenticate
from email_fetcher import fetch_emails_by_page

def lambda_handler():
    # Azure AD credentials
    tenant_id = "ecefbb66-e571-4a04-ad37-82492edec860"
    client_id = "2ec46f47-7192-47af-b640-f5cbb6cbf849"
    cert_thumbprint = "10EA8AED98BD728831AC3CBDC82CA4C1E2200566"
    private_key_path = "config/private_key.pem"
    
    # User email and initial Graph API URL
    user_email = "harshit.lohani@cynoteck.com"
    email_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages?$top=10&$orderby=receivedDateTime DESC"

    try:
        # Authenticate and get access token
        access_token = authenticate(tenant_id, client_id, cert_thumbprint, private_key_path)
        print("✅ Successfully authenticated!")

        # Fetch emails page by page
        current_url = email_url
        while current_url:
            results = fetch_emails_by_page(access_token, user_email, current_url)
            
            # Get emails from the current page
            emails = next(results, [])
            for email in emails:
                print(f"Subject: {email.get('subject')}")
                # Uncomment and process additional details if needed
                # print(f"From: {email.get('from', {}).get('emailAddress', {}).get('address')}")
                # print(f"Received: {email.get('receivedDateTime')}")

            # Get the next page URL, if available
            current_url = next(results, None)

    except Exception as e:
        print(f"🚨 Error: {e}")


if __name__ == "__main__":
    lambda_handler()
