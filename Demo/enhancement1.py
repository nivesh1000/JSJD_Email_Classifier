import re

def extract_email_from_body(body):
    """
    Extracts the first email address found in the body of the email.
    """
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, body)
    return match.group(0) if match else None