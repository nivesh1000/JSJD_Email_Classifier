def keywordmatcher(text, keyword):
    """
    Function to match a keyword in email's part.
    """
    text = text.lower()
    keyword = keyword.lower()
    key_len = len(keyword)
    text_len = len(text)

    if keyword == text:
        return True

    for j in range(text_len - key_len + 1): 
        if keyword[0] == text[j]:
            if (j == 0 or not text[j-1].isalnum()) and (j+key_len == text_len or not text[j+key_len].isalnum()):
                return keyword == text[j:j+key_len]

    return False
