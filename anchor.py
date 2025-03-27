raw_body = '''/home/cynoteckdell/Documents/JSJD_Email_Classifier/get_filters.txt'''
from bs4 import BeautifulSoup

body = (
    BeautifulSoup(
        raw_body, "html.parser")
)

for a_tag in body.find_all("a"):
    a_tag.decompose()

# Extract cleaned text
space_free_body = body.get_text().strip()
print(space_free_body)