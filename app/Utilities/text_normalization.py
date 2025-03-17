from bs4 import BeautifulSoup
from logger import get_logger

logger = get_logger()

def body_normalization(emails):
    for email in emails:
        body = (BeautifulSoup(email['body'], "html.parser"))
        for a_tag in body.find_all("a"):
            a_tag.decompose()
        clean_body = body.get_text().strip().replace("\xa0", " ").replace("\u200c", " ")
        email["body"]=clean_body
    logger.info("Email batch body normalized successfully!!")
    return emails
