import re



def extract_emails(body):
    email_pattern = r'[a-zA-Z0-9-._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, body)