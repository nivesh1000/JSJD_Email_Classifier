import threading
import time
import requests
from logger import EmailParser

logger = EmailParser.get_logger()

API_URL = "https://staging.jsjdmedia.com/api/emails/store"
MAX_RETRIES = 5
INITIAL_DELAY = 1
HEADERS = {"Content-Type": "application/json"}


def post_email_batch_to_api(classified_emails):
    """
    Send classified emails via POST request to the API.

    Args:
        classified_emails (dict): Dictionary containing classified email data.
    Returns:
        tuple: (bool, int, str) -> (success, status_code, error_message)
    """
    if not classified_emails.get("data"):
        logger.info("No classified emails to send.")
        return False, None, "No data to send"

    logger.info(f"Sending {len(classified_emails['data'])} classified emails to API...")
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            response = requests.post(API_URL, json=classified_emails, headers=HEADERS)
            status_code = response.status_code

            if status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = (
                    float(retry_after)
                    if retry_after
                    else INITIAL_DELAY * (2**retry_count)
                )
                logger.warning(
                    f"Rate limit exceeded. Retrying after {delay} seconds... ({retry_count + 1}/{MAX_RETRIES})"
                )
                time.sleep(delay)
                retry_count += 1
                continue

            response.raise_for_status()
            return True, status_code, None

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return False, status_code if "status_code" in locals() else None, str(e)


def send_request(classified_emails, index):
    """
    Sends email batch and logs the response.

    Args:
        classified_emails (dict): Email data to be sent.
        index (int): Request number.
    """
    success, status_code, error = post_email_batch_to_api(classified_emails)
    logger.info(
        f"Response {index}: Success={success}, Status Code={status_code}, Error={error}"
    )
    return success


# Sample email batch
fake_classified_emails = {
    "data": [
        {
            "email_id": "AAMkADZmMjNiMDJjLTUzNDItNDJiZS1iOTkxLTQ3NGFhOTE0OGEwZABGAAAAAACmpm51Pxn4S6hR8gC58iFDBwCY28Rccs6eQ6vSFsjSkG-hAAAAAAEMAACY28Rccs6eQ6vSFsjSkG-hAAGrhNFcAAA=",
            "to": "editor@arpnewsletters.com",
            "from": "mjones@associationrevenuepartners.com",
            "subject": "BOMA FW What's Happening | 3/20/25 was successfully sent",
            "body": "Need Help? 214.396.9936BOMA FW What's Happening | 3/20/25 was successfully sentTo see how your campaign is performing, view your Email Campaign Activity Report. Keep up the good work! Campaign DetailsCampaign Id76483449Account Id5670218 (BOMA Fort Worth)SentMarch 20, 2025 @ 2:03 PM UTCSubjectNew Mixed-Use Project Approved for Montgomery Street Antique Mall SiteTotal Recipients845Recipient ListsContacts added in the last 30 days, BOMA FW - SubscribersNeed Help?Contact ARP Newsletters Customer SupportToll Free: 214.396.9936International: 214.396.9936Email: mjones@associationrevenuepartners.comRegards,The ARP Newsletters Team  © 2025 Association Revenue Partners or its affiliates. All rights reserved. ARP Newsletters is a trademark or registered trademark of Association Revenue Partners or its affiliates.",
            "raw_body": '<html><head>\r\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head><body><table width="100%" border="0" cellpadding="0" cellspacing="8" style="background-color:#dedddd"><tbody><tr><td valign="top"><table width="600" border="0" align="center" cellpadding="0" cellspacing="0" id="templateContainer" style="background-color:#ffffff"><tbody><tr><td valign="top"><table width="100%" border="0" align="center" cellpadding="15" cellspacing="0" id="templateHeader"><tbody><tr><td><table width="250" border="0" align="left" cellpadding="0" cellspacing="0" id="headerLogo"><tbody><tr><td><img src="https://media.campaigner.com/org/1/theme/1/Campaigner-logo.png" border="0"></td></tr></tbody></table><table width="290" border="0" cellpadding="10" cellspacing="0" id="headerText"><tbody><tr><td align="right" class="headerText" style="font-family:Arial,Helvetica,sans-serif; font-size:12px; color:#666666"><span id="systemVariable" name="phoneNumber">Need Help? 214.396.9936</span></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td valign="top"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0" id="headerTitle"><tbody><tr><td align="center" style="font-family:Arial,Helvetica,sans-serif; font-size:20px; color:#ffffff; height:80px; background-color:#34495E">BOMA FW What\'s Happening | 3/20/25 was successfully sent</td></tr></tbody></table></td></tr><tr><td valign="top"><table width="600" border="0" cellpadding="15" cellspacing="0" id="templateBody"><tbody><tr><td valign="top"><table width="540" border="0" align="center" cellpadding="0" cellspacing="0" id="bodyContainer"><tbody><tr><td valign="top" align="center"><table width="311" border="0" align="center" cellpadding="8" id="bodyContainer"><tbody><tr><td align="center" valign="top" class="bodyText" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5"><strong>To see how your campaign is performing, view your Email Campaign Activity Report. Keep up the good work!</strong></td></tr><tr><td align="center"><table width="165" border="0" cellpadding="7" cellspacing="0" style="background-color:#3793D0"><tbody><tr><td align="center" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#fff"><a href="https://secure.campaigner.com/CSB/Reports/SendReports.aspx?cid=76483449" style="color:#ffffff; text-decoration:none">View Report</a></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td>&nbsp;</td></tr><tr><td valign="top" class="bodyText" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5"><span id="dynamicRow$1"><table cellpadding="3" cellspacing="1" border="0" width="100%" height="100%"><thead><tr><td width="26%" class="bodyText" style="font-family:Arial,Helvetica,sans-serif; font-size:15px; color:#4d4d4d; line-height:1.5"><strong>Campaign Details</strong></td></tr></thead><tbody class="dynamic" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5"><tr><td valign="top" style="background:#d9e9c4; font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">Campaign Id</td><td valign="top" style="background:#d9e9c4; font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">76483449</td></tr><tr><td valign="top" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">Account Id</td><td valign="top" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">5670218 (BOMA Fort Worth)</td></tr><tr><td valign="top" style="background:#d9e9c4; font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">Sent</td><td valign="top" style="background:#d9e9c4; font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">March 20, 2025 @ 2:03 PM UTC</td></tr><tr><td valign="top" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">Subject</td><td valign="top" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">New Mixed-Use Project Approved for Montgomery Street Antique Mall Site</td></tr><tr><td valign="top" style="background:#d9e9c4; font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">Total Recipients</td><td valign="top" style="background:#d9e9c4; font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">845</td></tr><tr><td valign="top" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">Recipient Lists</td><td valign="top" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5">Contacts added in the last 30 days, BOMA FW - Subscribers</td></tr></tbody></table></span><br><span style="font-size:14px"><strong>Need Help?</strong></span><br><span id="systemVariable" name="productName">Contact ARP Newsletters Customer Support</span><br><span id="systemVariable" name="tollFreeNumber"><strong>Toll Free</strong>: 214.396.9936</span><br><span id="systemVariable" name="phoneNumber"><strong>International</strong>: 214.396.9936</span><br><span id="systemVariable" name="csEmail"><strong>Email:</strong> mjones@associationrevenuepartners.com</span><br><br>Regards,<br><span class="bodyText" style="font-family:Arial,Helvetica,sans-serif; font-size:13px; color:#4d4d4d; line-height:1.5"><strong><span id="systemVariable" name="productName">The ARP Newsletters Team</span></strong><br><span id="systemVariable" name="csEmail"><a href="mailto:mjones@associationrevenuepartners.com">mjones@associationrevenuepartners.com</a></span></span><br><br></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td valign="top" style="background-color:#a6a6ab"><table width="600" border="0" cellpadding="0" cellspacing="0" id="templateFooter" style="background-color:#a6a6ab"><tbody><tr><td>&nbsp;</td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td valign="top" align="center"><table width="500" border="0" align="center" cellpadding="0" id="templateFooter"><tbody><tr><td>&nbsp;</td><td valign="top" align="center" style="font-family:Arial,Helvetica,sans-serif; font-size:11px; color:#4d4d4d">© 2025 <span id="systemVariable" name="companyName">Association Revenue Partners</span> or its affiliates. All rights reserved. <span id="systemVariable" name="productName">ARP Newsletters</span> is a trademark or registered trademark of <span id="systemVariable" name="companyName">Association Revenue Partners</span> or its affiliates.</td><td>&nbsp;</td></tr></tbody></table></td></tr><tr><td>&nbsp;</td></tr></tbody></table><meta name="viewport" content="width=device-width"><style type="text/css">\r\n<!--\r\n@media only screen and (min-device-width: 320px) and (max-width: 480px) {\r\nbody, table, td, p, a, li, blockquote\r\n\t{margin-left:0px;\r\n\tmargin-top:0px;\r\n\tmargin-right:0px;\r\n\tmargin-bottom:0px}\r\ntable[id="templateContainer"]\r\n\t{width:100%!important;\r\n\tmax-width:600px!important}\r\ntable[id="templateHeader"]\r\n\t{width:100%!important;\r\n\tmax-width:600px!important}\r\ntable[id="headerLogo"]\r\n\t{width:100%!important;\r\n\ttext-align:center!important}\r\ntable[id="headerText"]\r\n\t{width:100%!important;\r\n\ttext-align:center!important}\r\ntable[id="headerTitle"]\r\n\t{width:100%!important;\r\n\tmax-width:600px!important}\r\ntable[id="templateBody"]\r\n\t{width:100%!important;\r\n\tmax-width:600px!important}\r\ntable[id="bodyContainer"]\r\n\t{max-width:560px!important;\r\n\twidth:100%!important}\r\ntable[id="templateFooter"]\r\n\t{width:100%!important;\r\n\tmax-width:600px!important}\r\ntd[class="headerText"]\r\n\t{font-size:11px!important;\r\n\ttext-align:center!important}\r\ntd[class="bodySubTitle"]\r\n\t{font-size:18px!important;\r\n\tline-height:35px!important}\r\ntd[class="bodyText"]\r\n\t{font-size:14px!important;\r\n\tline-height:22px!important}\r\ndiv[class="overflow"]\r\n\t{max-width:155px!important}\r\n\r\n\t}\r\n-->\r\n</style></body></html>',
            "received_time": "2025-03-20T14:04:16Z",
            "subscriber_email": "",
            "group": [{"group_id": 12, "keyword_id": []}],
        }
    ]
}
threads = []
index = 1
while index < 1000:  # Infinite loop
    thread = threading.Thread(target=send_request, args=(fake_classified_emails, index))
    thread.start()
    threads.append(thread)
    time.sleep(0.1)  # Small delay to prevent overwhelming the system
    index += 1

for thread in threads:
    thread.join()
print("all sent success")
