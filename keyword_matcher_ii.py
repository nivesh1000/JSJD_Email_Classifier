import re

def keywordmatcher(text: str, keyword: str) -> bool:
    return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
