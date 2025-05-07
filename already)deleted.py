import requests

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



ACCESS_TOKEN='eyJ0eXAiOiJKV1QiLCJub25jZSI6Ik9wMURuRlQweHFZdnIxZGdBWEkybm5yZ0d3eHpTRXVKX0NiQlZUOFNrMXMiLCJhbGciOiJSUzI1NiIsIng1dCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSIsImtpZCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9lMTViMjhlNS01MmU1LTRhN2ItOWJiMy1jOWQ5NGFhZTZlZTUvIiwiaWF0IjoxNzQ2NDg5Njg5LCJuYmYiOjE3NDY0ODk2ODksImV4cCI6MTc0NjQ5NDE0NSwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsicDEiXSwiYWlvIjoiQVdRQW0vOFpBQUFBVUlvdmRNdmRucEpBcmRIL1dObUZEQzgyRGZwUVBKVTRpS3JQTmUrUGJYSlhBb3N2ZmhqMEVFZVJ4aCtpSFBJMW92ZUxLemJ6ZzJxQzF6dEs3Y3M2QndraFBmU0hQV2NmaVBMWlc3c3lEcldSZGxSWXhOc0pMMTFTSlRIcFpJd1AiLCJhbXIiOlsicHdkIiwibWZhIl0sImFwcF9kaXNwbGF5bmFtZSI6IkpTSkRfRW1haWxfQXV0b21hdGlvbiIsImFwcGlkIjoiYjFkYzMwNDktOTQ3OS00ZDQyLTlkOTktNWE2Y2JmNDk2ODRmIiwiYXBwaWRhY3IiOiIwIiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiMjQwNToyMDE6NjgwNDpiYTk4OjUzMTU6OWZhYTpkNGE2OjQxOTgiLCJuYW1lIjoiQVJQIE5ld3NsZXR0ZXJzIiwib2lkIjoiMTk4MTYxY2QtMWIwNS00ZWUxLTlkYTItMGE4MzM1MjBhODYwIiwicGxhdGYiOiI4IiwicHVpZCI6IjEwMDMyMDAyQjA3MzM3NDciLCJyaCI6IjEuQVZFQTVTaGI0ZVZTZTBxYnM4blpTcTV1NVFNQUFBQUFBQUFBd0FBQUFBQUFBQUJSQVAxUkFBLiIsInNjcCI6Ik1haWwuUmVhZFdyaXRlIG9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiMDAyZWUwMTktZDI5YS1kZTJmLTZiZGMtMWZkNjViYzI2MzhiIiwic2lnbmluX3N0YXRlIjpbImttc2kiXSwic3ViIjoiQ2w5bldPSm95Mk9xLUJhU0ttdlpwN3dIb1FWRFpRMU5tOXlqUjhUclJBdyIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJOQSIsInRpZCI6ImUxNWIyOGU1LTUyZTUtNGE3Yi05YmIzLWM5ZDk0YWFlNmVlNSIsInVuaXF1ZV9uYW1lIjoiZWRpdG9yQGFycG5ld3NsZXR0ZXJzLmNvbSIsInVwbiI6ImVkaXRvckBhcnBuZXdzbGV0dGVycy5jb20iLCJ1dGkiOiI2cHJkaTIzU1JrT3dGRTBBbUZHU0FBIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXSwieG1zX2Z0ZCI6InR4dVl4RF9wb1IwZ0drT092NEs3Ui01M0JFY0x6RWFTaktvOEpNOUhFVm9CZFhOM1pYTjBNeTFrYzIxeiIsInhtc19pZHJlbCI6IjI4IDEiLCJ4bXNfc3QiOnsic3ViIjoidzAwRUo0R2pqN2V4a0RZOURqTUFwRkdWRm1iVnI0d2xJV0RsdVRoNG1ZOCJ9LCJ4bXNfdGNkdCI6MTU5MTkwNTUwM30.KVEZSZrPcHdgFvDTjhbhM_UXIV7OWebmqjiKBLqk2T2mTjKe6_ssbqmLGUx9EMk0_-9Reg5-fz25QQBs615bkrJWoAZQbZfCI2M43fcptOn8f7R21ZA92V_MG-UOSNJE5mtXlq3TPt4vaLkypwZpfTaF3seyDXHfsKuvMLgcrPMzbsfcPSSJYnidEeIopfiQxYadRJ7btNjKqC9puwe79ai5LwHiBOtQJuBJA0nkwy7AsUa3MzWLpMeol0zk9CxHOYlSdBgJfvxCZkt1dRXJqzo6XLDM_tM1bG3iaYcuwxCSsTuDAEfF-aZfGcjrayvNkcuypzCSY5rbowFKPnx0BA'



email_id='AAkALgAAAAAAHYQDEapmEc2byACqAC-EWg0AmNvEXHLOnkOr0hbI0pBv4QAByFHCJQAA'

print(is_email_in_deleted_folder(email_id, ACCESS_TOKEN))
