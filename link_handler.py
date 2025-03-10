import re
with open("sample_body.txt", "r") as file:
    text = file.read()

def remove_links(text: str) -> str:
    pattern = r'\(https?://[^\)]+\)|https?://\S+'
    return re.sub(pattern, '', text)

print(remove_links(text))