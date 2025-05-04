import os
import requests
import json
from dotenv import load_dotenv

# Load your ACCESS_TOKEN from env
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def delete_emails_in_bulk(user_id: str, message_ids: list[str]) -> dict:
    """
    Deletes multiple emails in one batch request via Microsoft Graph.

    Args:
        user_id (str): The user's email or user ID.
        message_ids (list[str]): List of message IDs to delete.

    Returns:
        dict: The parsed JSON response from the batch API.
    """
    batch_url = "https://graph.microsoft.com/v1.0/$batch"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Build batch requests payload
    requests_payload = []
    for i, msg_id in enumerate(message_ids, start=1):
        requests_payload.append({
            "id": str(i),
            "method": "DELETE",
            "url": f"/users/{user_id}/messages/{msg_id}"
        })

    batch_body = { "requests": requests_payload }

    resp = requests.post(batch_url, headers=headers, json=batch_body)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    # Example usage:
    USER_ID = "editor@arpnewsletters.com"
    MESSAGE_IDS = [
        "AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZABGAAAAAACmpm51Pxn4S6hR8gC58iFDBwCY28Rccs6eQ6vSFsjSkG-hAAAAAAEMAACY28Rccs6eQ6vSFsjSkG-hAAHHNHQGAAA=", 
        "AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZABGAAAAAACmpm51Pxn4S6hR8gC58iFDBwCY28Rccs6eQ6vSFsjSkG-hAAAAAAEMAACY28Rccs6eQ6vSFsjSkG-hAAHHNHQFAAA=",
        "AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZABGAAAAAACmpm51Pxn4S6hR8gC58iFDBwCY28Rccs6eQ6vSFsjSkG-hAAAAAAEMAACY28Rccs6eQ6vSFsjSkG-hAAHHNHQEAAA="
    ]
    result = delete_emails_in_bulk(USER_ID, MESSAGE_IDS)
    print(json.dumps(result, indent=2))