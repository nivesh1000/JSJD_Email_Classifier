import re

def extract_emails_by_sender_type(emails, no_reply_variations):
    for email in emails:    
        from_address = email['from']
        body= email['body']
        if from_address.startswith(tuple(no_reply_variations)):
            email_pattern = (
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            )
            subscriber_emails = re.findall(
                email_pattern, body)
            email["subscriber_email"] = ", ".join(
                subscriber_emails
            )
    return emails            