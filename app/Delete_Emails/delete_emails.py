import os
import json
import requests
import time
from app.Token_Refresher.token_refresher import TokenManager

from app.Logger.logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()

SUCCESS_CODES = {200, 204}  # Define success codes as a set for O(1) lookup
NOT_FOUND_CODES = {400, 404}


def delete_emails(emails_to_remove):
    """
    Asynchronously delete multiple emails using aiohttp.

    """

    token_manager = TokenManager()

    # Token expiry time in seconds. Set to refresh at 55 minutes
    token_expiry_threshold = 55 * 60

    ACCESS_TOKEN = token_manager.refresh_tokens()

    if not ACCESS_TOKEN:
        logger.error("Access token is missing.", LineFileProvider().get_file_info())
        return

    # Time at which token was initally issued
    token_issued_time = time.time()

    failed_emails = []
    emails_not_found = []
    total_emails = len(emails_to_remove)

    if not emails_to_remove:
        return {"statusCode": 400, "body": json.dumps({"error": "No emails provided"})}

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

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
    for i, email in enumerate(emails_to_remove, 1):
        try:
            if time.time() - token_issued_time > token_expiry_threshold:

                logger.forensic(
                    "Token about to expire. Refreshing....",
                    LineFileProvider().get_file_info(),
                )

                ACCESS_TOKEN = token_manager.refresh_tokens()

                if not ACCESS_TOKEN:

                    logger.error(
                        "Failed to retrieve ACCESS_TOKEN. Returning.....",
                        LineFileProvider().get_file_info(),
                    )
                    return {"error": "Failed to retrieve ACCESS_TOKEN"}
            token_issued_time = time.time()

            response = requests.delete(f"{base_url}/{email}", headers=headers)

            status = response.status_code

            response_text = response.text if response.text else "No resposne body"

            if status in NOT_FOUND_CODES:
                logger.warning(
                    f"Email Not Found: {email} ({i}/{total_emails})",
                    LineFileProvider().get_file_info(),
                )

                emails_not_found.append({"email": email, "error": response_text})

            elif status in SUCCESS_CODES:
                logger.info(
                    f"Successfully Deleted {email} ({i}/{total_emails})",
                    LineFileProvider().get_file_info(),
                )
            else:

                failed_emails.append({"email": email, "error": response_text})

                logger.error(
                    f"Failed to Delete email: {email} ({i}/{total_emails})",
                    LineFileProvider().get_file_info(),
                )

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
