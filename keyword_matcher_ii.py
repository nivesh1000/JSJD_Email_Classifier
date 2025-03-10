import regex

def keywordmatcher(text: str, keyword: str) -> bool:
    return bool(regex.search(r'\b' + regex.escape(keyword) + r'\b', text, regex.IGNORECASE))
