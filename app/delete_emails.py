import os
import json
import requests
from app.logger import EmailParser

logger = EmailParser.get_logger()


def delete_emails(emails_to_remove, access_token):

    failed_emails = []

    if not emails_to_remove:
        return {"statusCode": 400, "body": json.dumps({"error": "No emails provided"})}

    if not access_token:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "No access token provided"}),
        }

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        base_url = os.environ["DELETE_BASE_URL"]
    except KeyError:
        logger.error("DELETE_BASE_URL environment variable not set")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": "DELETE_BASE_URL environment variable not set"}
            ),
        }
    for email in emails_to_remove:
        try:
            response = requests.delete(f"{base_url}/{email}", headers=headers)
            if response.status_code != 204:
                failed_emails.append({"email": email, "error": response.text})
        except requests.exceptions.RequestException as e:
            failed_emails.append({"email": email, "error": str(e)})

    # Return 200 for full success, 207 for partial success, 500 for all failures
    if not failed_emails:
        status_code = 200
        message = "Successfully deleted all emails"

    elif len(failed_emails) < len(emails_to_remove):
        status_code = 207
        message = "Some emails deleted successfully"

    else:
        status_code = 500
        message = "No emails deleted successfully"

    return {
        "statusCode": status_code,
        "body": json.dumps({"message": message, "failed_emails": failed_emails}),
        "statusCode": status_code,
        "body": json.dumps({"message": message, "failed_emails": failed_emails}),
    }