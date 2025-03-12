import os
import json
from app.token_refresher import TokenManager
from datetime import datetime, timedelta
from app.Email_Fetcher.email_fetcher import fetch_emails
from app.filter import classify_emails
from app.delete_emails import delete_emails
from app.get_filters import fetch_groups

from app.logger import EmailParser

logger = EmailParser.get_logger()


def generate_today_email_url() -> str:
    """
    Generate the URL to fetch emails received today using Microsoft Graph API.

    Returns:
        str: The URL for fetching today's emails.
    """
    today = datetime.utcnow()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    # Format times in ISO 8601
    start_time = start_of_day.isoformat() + "Z"
    end_time = end_of_day.isoformat() + "Z"

    # Construct the URL for filtering emails by receivedDateTime
    url = (f"https://graph.microsoft.com/v1.0/me/messages?"f"$top=100&"f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"f"&$orderby=receivedDateTime DESC")
    # url="https://graph.microsoft.com/v1.0/me/messages?$filter=receivedDateTime ge 2025-02-20T00:00:00Z and receivedDateTime le 2025-02-20T23:59:59Z&$orderby=receivedDateTime DESC"
    return url


def read_json_file(file_path):
    """
    Reads a JSON file and returns the data as a Python object.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or list: The data loaded from the JSON file.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# def get_ssm_parameters():
#     """Retrieve ACCESS_TOKEN and REFRESH_TOKEN from AWS SSM Parameter Store"""
#     # region_name = os.environ["REGION_NAME"]
#     region_name = "us-east-1""

#     ssm = boto3.client("ssm", region_name=region_name)  # Fixed region

#     try:
#         # Fetch ACCESS_TOKEN
#         access_token = ssm.get_parameter(Name="ACCESS_TOKEN", WithDecryption=False)[
#             "Parameter"
#         ]["Value"]

#         # Fetch REFRESH_TOKEN
#         refresh_token = ssm.get_parameter(Name="REFRESH_TOKEN", WithDecryption=False)[
#             "Parameter"
#         ]["Value"]

#         return {"ACCESS_TOKEN": access_token, "REFRESH_TOKEN": refresh_token}

#     except Exception as e:
#         print(f"Error retrieving SSM parameters: {e}")
#         return {"error": str(e)}


def generate_all_email_url() -> str:
    """
    Generate the URL to fetch all emails using Microsoft Graph API.

    Returns:
        str: The URL for fetching all emails.
    """
    try:
        url = (
            "https://graph.microsoft.com/v1.0/me/messages?"
            "$top=100&"
            "$orderby=receivedDateTime"
        )
        return url
    except Exception as e:
        logger.error(f"Error generating all email URL: {e}")
        return ""


def generate_last_3_days_email_url() -> str:
    """
    Generate the URL to fetch emails received in the last 3 days using Microsoft Graph API.

    Returns:
        str: The URL for fetching emails from the last 3 days.
    """
    today = datetime.utcnow()
    start_of_range = today - timedelta(days=3)  # 3 days ago
    end_of_range = today

    # Format times in ISO 8601
    start_time = (
        start_of_range.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        + "Z"
    )
    end_time = end_of_range.isoformat() + "Z"

    # Construct the URL for filtering emails by receivedDateTime
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages?"
        f"$top=100&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        f"&$orderby=receivedDateTime DESC"
    )

    return url


def lambda_handler(event):
    try:
        # Initialize Token Manager and Fetch Parameters Once
        token_manager = TokenManager()
        # tokens = get_ssm_parameters()
        ACCESS_TOKEN = token_manager.refresh_tokens()
        if not ACCESS_TOKEN:
            return {"error": "Failed to retrieve ACCESS_TOKEN"}

        # API Request to delete emails
        if "requestContext" in event:
            API_AUTHENTICATION_KEY = os.environ.get("API_AUTHENTICATION_KEY")
            if not API_AUTHENTICATION_KEY:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"Error": "Missing API authentication key"}),
                }

            headers = event.get("headers", {})
            auth_key = headers.get("authorization", "").strip()

            if auth_key != API_AUTHENTICATION_KEY:
                return {
                    "statusCode": 401,
                    "body": json.dumps({"Authorization": "Invalid authorization key"}),
                }

            # Extract and parse request body
            try:
                body = json.loads(event.get("body", "{}"))
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {
                            "Authorization": "Successfully authenticated",
                            "Error": "Invalid JSON format",
                        }
                    ),
                }

            emails_to_remove = body.get("delete_emails", [])
            if not emails_to_remove:
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {
                            "Authorization": "Successfully authenticated",
                            "Error": "No emails to remove provided",
                        }
                    ),
                }

            # token_manager.refreshing_token(
            #     tokens
            # )  # To be uncommented when testing/deployed

            # Attempt to delete emails and handle potential errors
            try:
                output = delete_emails(emails_to_remove, ACCESS_TOKEN)
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps(
                        {
                            "Authorization": "Successfully authenticated",
                            "Error": f"Failed to delete emails: {str(e)}",
                        }
                    ),
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"Authorization": "Successfully authenticated", "Result": output}
                ),
            }

        # EventBridge (scheduler) invocation

        task = event.get("task")

        if task == "refresh_tokens":
            try:
                return token_manager.refreshing_token(tokens)
            except Exception as e:
                return {"error": f"Failed to refresh tokens: {str(e)}"}

        elif task == "fetch_emails":
            try:
                filters_and_deletion_emails = fetch_groups()
                filters= filters_and_deletion_emails["data"]["groups"]
                delete_emails = filters_and_deletion_emails["data"]["emailsToRemove"] # Object of email IDs to delete

                deletion_emails_list = [delete_email['email_address'] for delete_email in delete_emails]
                active_filters = []
                for group in filters:
                    if group.get("status") == "active":
                        active_filters.append(group) # Only include active groups
                if not ACCESS_TOKEN:
                    return {"error": "Access token not found"}

                email_url = generate_today_email_url()
                # email_url = generate_all_email_url()
                # deletion_emails_list = ['nivesh.kumar@cynoteck.com']
                no_reply_obj=read_json_file("no_reply_variations.json")
                no_reply_variations = []

                for sample in no_reply_obj["no_reply_variations"]:
                    index = sample.find("@")
                    if index != -1:  # Ensure "@" exists
                        no_reply_variations.append(sample[:index])
                result = fetch_emails(email_url, ACCESS_TOKEN, active_filters, deletion_emails_list, no_reply_variations)
                return result
            except Exception as e:
                return {"error": f"Failed to fetch emails: {str(e)}"}

        return {"error": "Invalid task specified"}

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"Error": f"Unexpected server error: {str(e)}"}),
        }


if __name__ == "__main__":
    event = {"task": "fetch_emails"}
    output = lambda_handler(event=event)
    print(output)
