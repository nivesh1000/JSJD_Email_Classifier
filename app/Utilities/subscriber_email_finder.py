import re

def extract_emails_by_sender_type(emails, no_reply_variations):
    for email in emails:    
        from_address = email['from']
        to_address = email['to']

        body= email['body']
        if from_address.startswith(tuple(no_reply_variations)):
            email_pattern = (
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            )
            subscriber_emails = re.findall(
                email_pattern, body)
            filtered_subscriber_email=[subscriber_email for subscriber_email in subscriber_emails if subscriber_email not in [to_address, from_address]]

            email["subscriber_email"] = ", ".join(
                filtered_subscriber_email
            )
    return emails            