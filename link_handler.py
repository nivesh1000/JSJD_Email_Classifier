import re
text = '''
https://example.com .
https://example.org text...... (https://example.net ).
Here are some links: https://example.com/page1  https://example.org/page2  http://example.net?query=test .
This is text https://example.com/(page)/id=123.
'''
pattern = r'https?://\S+'

# Remove all links
clean_body = re.sub(pattern, '', text)
print(clean_body)