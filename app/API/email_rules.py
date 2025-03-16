import os
import requests
from app.Config.settings import GET_FILTER_API
from app.logger import get_logger
logger=get_logger()

def fetch_filter_and_deletion_emails():
    try:
        url = GET_FILTER_API
        response = requests.get(url)
        data = response.json()  # Parse JSON response
        logger.info('Filters and Deletion emails recieved successfully!!')
        filters= data["data"]["groups"]
        delete_emails = data["data"]["emailsToRemove"] # Object of email IDs to delete
        deletion_emails_list = [delete_email['email_address'] for delete_email in delete_emails]
        active_filters = []
        for group in filters:
            if group.get("status") == "active":
                active_filters.append(group) # Only include active groups

        return {"filters": active_filters, "deletion_emails": deletion_emails_list}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None