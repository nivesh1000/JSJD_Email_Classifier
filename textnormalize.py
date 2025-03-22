import unittest
from bs4 import BeautifulSoup
from unidecode import unidecode
import re

def text_normalization(text):
    # Parse the HTML content
    soup = BeautifulSoup(text, "html.parser")
    
    # Remove all <a> tags (links)
    for a_tag in soup.find_all("a"):
        a_tag.decompose()
    
    # Extract text while preserving original whitespace
    result = soup.get_text(separator=" ", strip=False)
    
    # Use unidecode to transliterate Unicode to ASCII
    result = unidecode(result)
    
    # Normalize multiple whitespace characters to single space
    result = " ".join(result.split())
    
    return result.strip()
    
    # return result.strip()

class TestTextNormalization(unittest.TestCase):
    def test_basic_text(self):
        """Test basic text without special characters"""
        input_text = "<p>Hello World</p>"
        expected = "Hello World"
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

    def test_non_breaking_space(self):
        """Test text with non-breaking space (\xa0)"""
        input_text = "<p>Hello\xa0World</p>"
        expected = "Hello World"
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

    def test_zero_width_space(self):
        """Test text with zero-width no-break space (\ufeff)"""
        input_text = "<p>\ufeffHello World</p>"
        expected = "Hello World"
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

    def test_mixed_unicode(self):
        """Test text with various Unicode characters"""
        input_text = "<p>Héllö\xa0Wôrld\u202fwith\u200bunicode\ufeff</p>"
        expected = "Hello World with unicode"
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

    def test_html_links(self):
        """Test text with HTML links that should be removed"""
        input_text = "<p>Hello <a href='test'>Link</a> World</p>"
        expected = "Hello World"
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

    def test_multiple_spaces(self):
        """Test text with multiple types of spaces"""
        input_text = "<p>Hello\xa0 \ufeff\u2003World</p>"
        expected = "Hello World"
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

    def test_empty_input(self):
        """Test empty input string"""
        input_text = ""
        expected = ""
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

    def test_complex_html(self):
        """Test complex HTML with Unicode and links"""
        input_text = """
            <div>
                <p>Héllö\xa0<a href='test'>link</a>\ufeffWôrld</p>
                <span>Another\u200bline</span>
            </div>
        """
        expected = "Hello World Another line"
        result = text_normalization(input_text)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()