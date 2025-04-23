from bs4 import BeautifulSoup
def normalize_by_removing_anchor_tag(text=None):
    if not text:
        with open('sample_emails.text', 'r', encoding='utf-8') as file:
            text = file.read()
    soup = BeautifulSoup(text, "html.parser")
    # print(soup.get_text())
    # Find and decompose all anchor tags (removes both the tag and its content)
    # for a_tag in soup.find_all("a"):
    #     a_tag.decompose()

    [a_tag.decompose() for a_tag in soup.find_all("a")]  

    return str(soup)
# print(normalize_by_removing_anchor_tag("Before <a href='#'>Link</a> After"))