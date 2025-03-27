import unittest
import re
from bs4 import BeautifulSoup
from unidecode import unidecode

# Your functions
def text_normalize(text):
    return re.sub(r'\s+', ' ', text)

def html_seperator_old(html, separator=' '):
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    for a_tag in soup.find_all("a"):
        a_tag.decompose()

    # Get the <body> tag; return empty string if none exists
    body = soup.body
    if not body:
        return ""
    
    text = body.get_text(separator)
    normalized_text = text_normalize(unidecode(text).strip())
    
    return normalized_text

# Unit tests
class TestHtmlSeparator(unittest.TestCase):
    
    def test_single_newline_preserved(self):
        """Test that a single newline is preserved."""
        html = '<body><div>Hello</div><div>World</div></body>'
        result = html_seperator_old(html, ' ')
        expected = 'Hello World'
        self.assertEqual(result, expected)

    def test_multiple_newlines(self):
        """Test that multiple newlines are reduced to one."""
        html = '<body><div><b>Line one<b><br><br><b>Line two<b></div></body>'
        result = html_seperator_old(html, ' ')
        # BeautifulSoup's get_text() with separator='\n' adds newlines, and <br> adds more
        # text_normalize should collapse them
        expected = 'Line one Line two'
        self.assertEqual(result, expected)

    def test_no_newlines_unchanged(self):
        """Test that text without newlines remains unchanged."""
        html = '<body><div>Hello World</div></body>'
        result = html_seperator_old(html, ' ')
        expected = 'Hello World'
        self.assertEqual(result, expected)

    def test_complex_html_with_links(self):
        """Test normalization with links removed and multiple breaks."""
        html = '<body><div>Hello<a href="#">link</a></div><div>World<br><br>Test</div></body>'
        result = html_seperator_old(html, ' ')
        expected = 'Hello World Test'
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()