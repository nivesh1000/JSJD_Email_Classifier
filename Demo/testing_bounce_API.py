
import requests

from bs4 import BeautifulSoup
import time

import json

def send_bounced_email(bounced_emails_data: list[dict]) -> tuple[int, dict]:
    """
    Sends bounced email data to the given API endpoint.

    Args:
        data (list[dict]): A list of dictionaries containing bounced email data.

    Returns:
        tuple: (status_code, response_json)
    """
    url = 'https://staging.jsjdmedia.com/api/emails/store-bounced-email'
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "data": bounced_emails_data
    }

    try:
        # logger.info(f"Sending {len(bounced_emails_data['data'])} bounced emails to API...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return 500, {"error": str(e)}
    

bounced_emails_data = [
        {
        "email_id": "AAMkADUyNWJkNzc1LWUzOTYtNDA3NC05YzUxLWM4YjM5YzkxMzA4OQBGAAAAAAA8gPqitF6FSbY_38fmfSv5BwAh1pkWyVTVQ6n1J3WQcgRhAAAAAAEMAAAh1pkWyVTVQ6n1J3WQcgRhAAAHiDDPAAA=",
        "to": "jsjd@cynoteck.com",
        "from": "nivesh.kumar@cynoteck.com",
        "subject": "",
        "body": "",
        "received_time": "2025-03-04T04:25:27Z",
        "subscriber_email":"test@gmail.com",
        "bounced_email_source_id":1
        }
    ]
    

bounced_emails_data = [{'email_id': 'AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZABGAAAAAACmpm51Pxn4S6hR8gC58iFDBwCY28Rccs6eQ6vSFsjSkG-hAAAAAAEMAACY28Rccs6eQ6vSFsjSkG-hAAHBGjswAAA=', 'to': 'editor@arpnewsletters.com', 'from': 'nivesh.nk1000@gmiail.com', 'subject': 'testing for the bounce email', 'body': 'Testing the email address to be extracted\xa0from bodynivesh.nk1000@gmiail.com', 'received_time': '2025-04-23T06:03:22Z', 'subscriber_email': '', 'bounced_email_source_id': 1}]    
print(send_bounced_email(bounced_emails_data))    