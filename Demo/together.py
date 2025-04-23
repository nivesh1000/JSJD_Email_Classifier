import requests
import json

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Credentials
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def fetch_email_headers_optimized(access_token):
    url = "https://graph.microsoft.com/v1.0/me/messages?$select=subject,from,body,toRecipients,internetMessageHeaders"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        # Save the complete response data to 'together.json'
        with open("together.json", "w") as json_file:
            json.dump(data, json_file, indent=4)
        
        print("Email data successfully saved in 'together.json'.")

        # Extract relevant details
        emails = data.get('value', [])
        extracted_info = []

        for email in emails:
            subject = email.get('subject')
            to_recipients = [
                recipient['emailAddress']['address']
                for recipient in email.get('toRecipients', [])
            ]

            headers = email.get('internetMessageHeaders', [])
            to_header = None
            subject_header = None

            for header in headers:
                if header['name'].lower() == 'to':
                    to_header = header['value']
                if header['name'].lower() == 'subject':
                    subject_header = header['value']

            extracted_info.append({
                "Subject": subject_header or subject,
                "To": to_header or ', '.join(to_recipients)
            })

        return extracted_info

    else:
        print(f"Failed to fetch headers. Status code: {response.status_code}")
        print(response.text)
        return []

# Example usage
access_token = ACCESS_TOKEN
emails = fetch_email_headers_optimized(access_token)
for email in emails:
    print(email)
