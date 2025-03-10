def clean_text(text: str) -> str:
    """
    Function to clean the text.
    """

    if not text:
        return ""

    # Remove punctuations
    text = text.strip(".,?!:;")
    return text


def keywordmatcher(text: str, keyword: str) -> bool:
    """
    Function to match a keyword in email's part.
    """

    if not (text and keyword):
        return False

    text = [clean_text(word) for word in text.lower().split()]
    keyword = [clean_text(word) for word in keyword.lower().split()]
    key_len = len(keyword)
    text_len = len(text)

    if key_len > text_len:
        return False

    for i in range(text_len - key_len + 1):
        if text[i: i + key_len] == keyword:
            return True

    return False
