import json
from datetime import datetime, timedelta
from logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()


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
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages?"
        f"$top=1&"
        f"$filter=receivedDateTime ge {start_time} and receivedDateTime le {end_time}"
        f"&$orderby=receivedDateTime DESC"
    )
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
        logger.error(
            f"Error: The file '{file_path}' was not found.",
            LineFileProvider().get_file_info(),
        )
    except json.JSONDecodeError:
        logger.error(
            f"Error: The file '{file_path}' is not a valid JSON file.",
            LineFileProvider().get_file_info(),
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {e}", LineFileProvider().get_file_info()
        )
