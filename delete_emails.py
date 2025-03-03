import os
import json
import requests
from logger import EmailParser

logger = EmailParser.get_logger()


def delete_emails(emails_to_remove, access_token):
    if not emails_to_remove:
        return {"statusCode": 400, "body": json.dumps({"error": "No emails provided"})}

    headers = {"Authorization": f"Bearer {access_token}"}
    # base_url = os.environ["DELETE_BASE_URL"]
    base_url = ""

    for email in emails_to_remove:
        try:
            url = f"{base_url}/{email}"
            response = requests.delete(url, headers=headers)
            logger.debug(
                f"Response for {url}: Status {response.status_code}, Text: {response.text}"
            )
            if response.status_code == 204:
                logger.info(f"Successfully deleted email: {email}")
            else:
                logger.error(
                    f"Failed to delete email: {email} - Status: {response.status_code}, Error: {response.text}"
                )
                return {
                    "statusCode": response.status_code,
                    "body": json.dumps(
                        {
                            "error": f"Failed to delete email: {email}",
                            "details": response.text,
                        }
                    ),
                }

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout occurred while deleting: {email}: {str(e)}")
            return {
                "statusCode": 504,
                "body": json.dumps(
                    {
                        "error": f"Timeout occurred while deleting: {email}",
                        "details": str(e),
                    }
                ),
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while deleting: {email}: {str(e)}")
            return {
                "statusCode": 503,
                "body": json.dumps(
                    {
                        "error": f"Connection error while deleting: {email}",
                        "details": str(e),
                    }
                ),
            }
        except Exception as e:
            logger.error(f"Unexpected error while deleting: {email}: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {
                        "error": f"Unexpected error while deleting: {email}",
                        "details": str(e),
                    }
                ),
            }

    return {
        "statusCode": 200,
        "body": json.dumps({"success": "Successfully deleted emails"}),
    }
