import os
import json
import asyncio
import aiohttp
import requests

from logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()


async def delete_emails(emails_to_remove, access_token):
    """
    Asynchronously delete multiple emails using aiohttp.

    """

    failed_emails = []
    emails_not_found = []

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
        logger.error(
            "DELETE_BASE_URL environment variable not set",
            LineFileProvider().get_file_info(),
        )
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": "DELETE_BASE_URL environment variable not set"}
            ),
        }
    for email in emails_to_remove:
        try:
            response = requests.delete(f"{base_url}/{email}", headers=headers)

            if response.status_code == 400:
                emails_not_found.append({"email": email, "error": response.text})

            elif response.status_code != 204:
                failed_emails.append({"email": email, "error": response.text})
        except requests.exceptions.RequestException as e:
            failed_emails.append({"email": email, "error": str(e)})

    # Return 200 for full success, 207 for partial success, 500 for all failures
    if not failed_emails and not emails_not_found:
        status_code = 200
        message = "Successfully deleted all emails"

    elif len(failed_emails) + len(emails_not_found) < len(emails_to_remove):
        status_code = 207
        message = "Some emails deleted successfully"

    else:
        status_code = 500
        message = "No emails deleted successfully"

    return {
        "statusCode": status_code,
        "body": json.dumps(
            {
                "message": message,
                "failed_emails": failed_emails,
                "emails_not_found": emails_not_found,
            }
        ),
    }
