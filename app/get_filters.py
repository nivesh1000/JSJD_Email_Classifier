import requests
import json
import os
import logging

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def fetch_groups():
    url = os.getenv("GET_FILTER_API")
    # Configure logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for non-200 responses
        data = response.json()  # Parse JSON response
        # logger.info(data)
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
