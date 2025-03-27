from bs4 import BeautifulSoup
from unidecode import unidecode
import textwrap
import unittest

def extract_text_with_breaks(html):
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    for a_tag in soup.find_all("a"):
        a_tag.decompose()

    # Get the <body> tag; return empty string if none exists
    body = soup.body
    if not body:
        return ""
    text = body.get_text(' ')
    
    return unidecode(text).strip()



class TestExtractTextWithBreaks(unittest.TestCase):

    def test_with_p_tag(self):
        html = textwrap.dedent("""\
            <body>
                <p>Hello</p>
                <div>World</div>
            </body>
        """)
        result = extract_text_with_breaks(html)
        expected = "Hello \n World"
        self.assertEqual(result, expected)

    def test_nested_tags(self):
        html = textwrap.dedent("""\
            <body>
                <div>Hello<span>my</span>friend</div>
            </body>
        """)
        result = extract_text_with_breaks(html)
        expected = "Hello my friend"
        self.assertEqual(result, expected)

    def test_empty_body(self):
        html = "<html></html>"  # No <body> tag
        result = extract_text_with_breaks(html)
        expected = ""
        self.assertEqual(result, expected)

    def test_whitespace_only(self):
        html = textwrap.dedent("""\
            <body>
                <p>  </p>
                <div>Text</div>
            </body>
        """)
        result = extract_text_with_breaks(html)
        expected = "Text"  # Whitespace-only line is stripped
        self.assertEqual(result, expected)

    def test_multiple_spaces(self):
        html = textwrap.dedent("""\
            <body>
                <p>  Hi  there  </p>
                <div>Bye   now</div>
            </body>
        """)
        result = extract_text_with_breaks(html)
        expected = "Hi  there   \n Bye   now"
        self.assertEqual(result, expected)

    def test_multilines(self):
        html = textwrap.dedent("""\
            <body>
                <h1>Title</h1>
                <p>This is a <span>long</span> paragraph</p>
                <div>End</div>
            </body>
        """)
        result = extract_text_with_breaks(html)
        expected = "Title \n This is a  long  paragraph \n End"
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()