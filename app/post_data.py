import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from app.filter import classify_emails
from app.delete_emails import delete_emails
from app.logger import EmailParser
import re

logger = EmailParser.get_logger()


def post_email_batch(classified_emails):
    """
    Send classified emails via POST request to the API.

    Args:
        classified_emails (dict): Dictionary containing classified email data.
    """
    # POST_API_URL = os.environ["POST_API_URL"]
    # POST_API_URL = "https://staging.jsjdmedia.com/api/emails/store"

    if not classified_emails.get("data"):
        logger.info("No classified emails to send.")
        return False, 0, "No data to send"

    try:
        post_headers = {"Content-Type": "application/json"}
        logger.info(
            f"Sending {len(classified_emails['data'])
                       } classified emails to API..."
        )

        post_response = requests.post(
            POST_API_URL, json=classified_emails, headers=post_headers
        )
        status_code = post_response.status_code

        # Try to parse JSON
        try:
            response_json = post_response.json()
            if status_code == 201 and response_json.get("status") == "success":
                logger.info(f"Successfully sent emails. Status: {status_code}")
                return True, status_code, ""
            error_msg = response_json.get("error", "Unknown error")
        except ValueError:
            error_msg = "Invalid JSON response"

        logger.error(
            f"Failed to send emails. Status: {status_code}, Error: {error_msg}"
        )
        return False, status_code, error_msg

    except requests.RequestException as e:
        logger.error(f"Request exception while sending emails: {str(e)}")
        return False, 0, str(e)