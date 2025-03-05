import os
import json
import requests
from logger import EmailParser

logger = EmailParser.get_logger()


def delete_emails(emails_to_remove, access_token):

    failed_emails = []

    if not emails_to_remove:
        return {"statusCode": 400, "body": json.dumps({"error": "No emails provided"})}

    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = os.environ["DELETE_BASE_URL"]

    for email in emails_to_remove:
        try:
            response = requests.delete(f"{base_url}/{email}", headers=headers)
            if response.status_code != 204:
                failed_emails.append({"email": email, "error": response.text})
        except requests.exceptions.RequestException as e:
            failed_emails.append({"email": email, "error": str(e)})

    return {
        "statusCode": 200 if not failed_emails else 207,
        "body": json.dumps({"success": "Processed emails", "failed_emails": failed_emails}),
    }
