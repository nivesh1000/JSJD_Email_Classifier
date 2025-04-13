import requests
import os
from app.Logger.logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()


def get_filters_and_delete_ids():

    url = os.getenv("GET_FILTER_API")

    try:
        response = requests.get(url)

        response.raise_for_status()  # Raises an error for non-200 responses

        data = response.json()  # Parse JSON response

        filters = data["data"]["groups"]

        delete_to_emails = data["data"][
            "emailsToRemove"
        ]  # Object of email IDs to delete

        delete_emails_list = [
            delete_email["email_address"] for delete_email in delete_to_emails
        ]
        
        active_filters = []

        for group in filters:
            if group.get("status") == "active":
                active_filters.append(group)  # Only include active groups

        return active_filters, delete_emails_list

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}", LineFileProvider().get_file_info())
        return None
