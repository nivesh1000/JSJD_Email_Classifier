import os
import json
import requests
from logger import EmailParser
import time

logger = EmailParser.get_logger()


def is_email_in_deleted_folder(email_id: str,
                               access_token: str) -> bool:
    """
    Returns True if the message with the given email_id is in the
    user's Deleted Items folder, False otherwise.
    """
    # Known Deleted Items folder ID (set this to your actual ID)
    deleted_folder_id = "AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZAAuAAAAAACmpm51Pxn4S6hR8gC58iFDAQCY28Rccs6eQ6vSFsjSkG-hAAAAAAEKAAA="

    # Fetch only the parentFolderId of the message
    url = (
        f"https://graph.microsoft.com/v1.0/me/messages/{email_id}"
        "?$select=parentFolderId"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Prefer": 'IdType="ImmutableId"'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        # Message not found → treat as not in Deleted Items
        return False
    response.raise_for_status()
    data = response.json()

    return data.get("parentFolderId") == deleted_folder_id


def delete_emails(emails_to_remove, access_token, max_retries=5):
    """
    Delete a list of emails by their IDs, retrying up to max_retries on failure.

    Returns a dict with statusCode and body containing message, failed_emails, and emails_not_found.
    """
    failed_emails = []
    emails_not_found = []
    # print(emails_to_remove)
    # exit(0)

    if not emails_to_remove:
        return {"statusCode": 400, "body": json.dumps({"error": "No emails provided"})}

    if not access_token:
        return {"statusCode": 401, "body": json.dumps({"error": "No access token provided"})}

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        # Ensure immutable IDs if used elsewhere; optional here
        "Prefer": 'IdType="ImmutableId"'
    }

    # Ensure DELETE_BASE_URL is set
    try:
        base_url = os.environ["DELETE_BASE_URL"]
    except KeyError:
        logger.error("DELETE_BASE_URL environment variable not set")
        return {"statusCode": 500,
                "body": json.dumps({"error": "DELETE_BASE_URL environment variable not set"})}

    # Iterate through emails to remove
    for email_id in emails_to_remove:
        attempt = 0
        while attempt < max_retries:
            attempt += 1
            try:
                response = requests.delete(f"{base_url}/{email_id}", headers=headers)
                status = response.status_code

                # Not found or bad request -> no retry, record as not found
                if status == 404 or status == 400 or 500 <= status < 600:
                    if is_email_in_deleted_folder(email_id, access_token):
                        break

                    emails_not_found.append({"email": email_id, "error": response.text})
                    break

                if status == 403:
                    # Parse Graph error code
                    err = response.json().get("error", {}).get("code")
                    if err == "ErrorCannotDeleteObject":
                        logger.info(f"Email {email_id} already soft-deleted; skipping")
                        break

                # Success
                if status == 204:
                    break

                # Throttling or server error -> retry
                if status == 429:
                    # respect Retry-After if provided, else exponential backoff
                    retry_after = response.headers.get("Retry-After")
                    wait = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
                    logger.warning(f"Attempt {attempt} for {email_id} failed with {status}, retrying in {wait}s")
                    time.sleep(wait)
                    continue

                # Other client error -> record and stop retrying
                failed_emails.append({"email": email_id, "error": response.text})
                break

            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt} for {email_id} raised exception: {e}")
                # transient network error -> retry
                time.sleep(2 ** attempt)
                continue
        else:
            # Exhausted retries
            failed_emails.append({"email": email_id, "error": f"Failed after {max_retries} attempts"})

    # Determine overall status code and message
    total = len(emails_to_remove)
    not_found_count = len(emails_not_found)
    failed_count = len(failed_emails)
    print("failed_count", failed_count)
    print("not_found_count", not_found_count)
    if failed_count == 0 and not_found_count == 0:
        status_code = 200
        message = "Successfully deleted all emails"
        print(message)
    elif (failed_count + not_found_count) < total:
        status_code = 207
        message = "Some emails deleted successfully"
        print(message)
        print("failed_emails", failed_emails)
        print("emails_not_found", emails_not_found)
    else:
        status_code = 500
        message = "No emails deleted successfully"

    return {
        "statusCode": status_code,
        "body": json.dumps({
            "message": message,
            "failed_emails": failed_emails,
            "emails_not_found": emails_not_found,
        }),
    }

ACCESS_TOKEN='eyJ0eXAiOiJKV1QiLCJub25jZSI6ImYtUTZDaVhZTmlIdGp5TFVORFdpYV82cGgzcGNFb0dTanR2dElxcHdPOGsiLCJhbGciOiJSUzI1NiIsIng1dCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSIsImtpZCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9lMTViMjhlNS01MmU1LTRhN2ItOWJiMy1jOWQ5NGFhZTZlZTUvIiwiaWF0IjoxNzQ2NTE1MzkwLCJuYmYiOjE3NDY1MTUzOTAsImV4cCI6MTc0NjUxOTk1MSwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsicDEiXSwiYWlvIjoiQVdRQW0vOFpBQUFBaUxMK213RUMwd0NJRkR3ZlBmVnZnWXlKcTlpRExpTG5sWUJ0bElwS1pkOFh3M0dtRTNValFFeERyNEFsdDY0TnFNU0t1ZjFqRU0yc2tiY1g4bWtvREt1bFNKemVMWnBzREU5Ym9OWkFhNnh3MFc3cncvTkhWbUhJTGVuN3JSZE4iLCJhbXIiOlsicHdkIiwibWZhIl0sImFwcF9kaXNwbGF5bmFtZSI6IkpTSkRfRW1haWxfQXV0b21hdGlvbiIsImFwcGlkIjoiYjFkYzMwNDktOTQ3OS00ZDQyLTlkOTktNWE2Y2JmNDk2ODRmIiwiYXBwaWRhY3IiOiIwIiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiNDkuMjQ5LjE1Ni4yIiwibmFtZSI6IkFSUCBOZXdzbGV0dGVycyIsIm9pZCI6IjE5ODE2MWNkLTFiMDUtNGVlMS05ZGEyLTBhODMzNTIwYTg2MCIsInBsYXRmIjoiOCIsInB1aWQiOiIxMDAzMjAwMkIwNzMzNzQ3IiwicmgiOiIxLkFWRUE1U2hiNGVWU2UwcWJzOG5aU3E1dTVRTUFBQUFBQUFBQXdBQUFBQUFBQUFCUkFQMVJBQS4iLCJzY3AiOiJNYWlsLlJlYWRXcml0ZSBvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInNpZCI6IjAwMmVlMDE5LWQyOWEtZGUyZi02YmRjLTFmZDY1YmMyNjM4YiIsInNpZ25pbl9zdGF0ZSI6WyJrbXNpIl0sInN1YiI6IkNsOW5XT0pveTJPcS1CYVNLbXZacDd3SG9RVkRaUTFObTl5alI4VHJSQXciLCJ0ZW5hbnRfcmVnaW9uX3Njb3BlIjoiTkEiLCJ0aWQiOiJlMTViMjhlNS01MmU1LTRhN2ItOWJiMy1jOWQ5NGFhZTZlZTUiLCJ1bmlxdWVfbmFtZSI6ImVkaXRvckBhcnBuZXdzbGV0dGVycy5jb20iLCJ1cG4iOiJlZGl0b3JAYXJwbmV3c2xldHRlcnMuY29tIiwidXRpIjoibDBTWG9kaHZHa3l4RTQyemkyY1pBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19mdGQiOiIyQldfMGVLZThLT3ZIWTBiWF9mVHctZDJvaFRPaFRrRlMyX2VnMTBnYkc0QmRYTmxZWE4wTFdSemJYTSIsInhtc19pZHJlbCI6IjEgMzAiLCJ4bXNfc3QiOnsic3ViIjoidzAwRUo0R2pqN2V4a0RZOURqTUFwRkdWRm1iVnI0d2xJV0RsdVRoNG1ZOCJ9LCJ4bXNfdGNkdCI6MTU5MTkwNTUwM30.PU938aRIO0_nl5f-CqRCGlQUlnIV-y_mvFZmMI6zOF3_AGdsPJDCfVpsV4vCNrhIwh7eVrK1rRER17BqV-0QkiwO7rcx9wWQmSrgsH4i3C52_5S9SPPcs0G0wUgjlxjr2vnxEgrI5hDAeidSCu62IgknJZeSRIFJwy4ly1X1L74CV3mTG9JAhyhVtcRYTdV2tGCBNEY4u0FiQMXx-H3nOhdiDbR9RpRx078rdmFIweVXfjpavopeODo9CSC1AMzgRIKOe4P_dcMx7i7_Do7Bm3M4vpoDooWZTTltGc2ycUEI8x3BsgX7Wvk3mDBFrWvryXYQd0GlP5qOU40v3ERRdg'

emails_to_remove=["AAMkADUyNWJkNzc1LWUzOTYtNDA3NC05YzUxLWM4YjM5YzkxMzA4OQBGAAAAAAA8gPqitF6FSbY_38fmfSv5BwAh1pkWyVTVQ6n1J3WQcgRhAAAAAAEMAAAh1pkWyVTVQ6n1J3WQcgRhAAAHiDDPAAA43434343="]
print(delete_emails(emails_to_remove, ACCESS_TOKEN, max_retries=2))