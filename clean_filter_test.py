from bs4 import BeautifulSoup
from unidecode import unidecode
import unittest
from filter import classify_emails
from get_filters import fetch_groups
import re   

filters_and_deletion_emails = fetch_groups()
filters= filters_and_deletion_emails["data"]["groups"]

def text_normalize(text):
    return re.sub(r'\s+', ' ', text)


def html_seperator_old(html,seperator):
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    for a_tag in soup.find_all("a"):
        a_tag.decompose()

    # Get the <body> tag; return empty string if none exists
    body = soup.body

    if not body:
        return ""
    text = body.get_text(seperator)


    normalized_text = text_normalize(unidecode(text).strip())

    
    return normalized_text


def html_seperator(html, separator='\n'):
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove all <a> tags
    for a_tag in soup.find_all("a"):
        a_tag.decompose()
    
    # Define inline tags to unwrap (no separator around these)
    inline_tags = [
        'a', 'abbr', 'b', 'bdi', 'bdo', 'big', 'button', 'cite', 'code', 'data', 
        'dfn', 'del', 'em', 'i', 'img', 'input', 'ins', 'kbd', 'label', 'mark', 
        'meter', 'q', 's', 'samp', 'select', 'small', 'span', 'strong', 'sub', 
        'sup', 'textarea', 'time', 'u', 'var', 'wbr'
    ]
    
    # Unwrap inline tags to keep their text inline
    for tag_name in inline_tags:
        for tag in soup.find_all(tag_name):
            tag.unwrap()
    
    # Get the <body> tag; return empty string if none exists
    body = soup.body
    if not body:
        return ""
    
    # Get text with separator between remaining tags
    text = body.get_text(separator)
    
    # Decode and strip leading/trailing whitespace
    clean_text = unidecode(text).strip()
    
    return clean_text

def use_filter(object,seperator):



    object[0]["body"]=html_seperator(object[0].get("body"),seperator)
    # print(repr(object[0]["body"]))
    return classify_emails(object,filters)[0]["group"]


class TestExtractTextWithBreaks(unittest.TestCase):

    def test_with_para_tag(self):
        object=[{
        "subject": "Hello",
        "body": '''
            <body>
                <p><b>test</b> p</p>
                <div>out of office</div>
            </body>
        '''
         }]
        result = use_filter(object," ")
        expected = [{'group_id': 10, 'keyword_id': [57]}, {'group_id': 11, 'keyword_id': [67]}]
        self.assertEqual(result, expected)

    def test_with_bold(self):
        object=[{
        "subject": "Hello",
        "body": '''
            <body>
                <p>test p</p>
                <div>out <b>of</b>  office</div>
            </body>
        '''
         }]
        result = use_filter(object," ")
        expected = [{'group_id': 11, 'keyword_id': [67]}]
        self.assertEqual(result, expected)        

    def test_with_seperate_div(self):
        object=[{
        "subject": "Hello",
        "body": '''
            <body>

                <div>test div</div>
                <span>out of office</span>                
                <div></div>
            </body>
        '''
         }]
        result = use_filter(object," ")
        expected = [{'group_id': 10, 'keyword_id': [57]}, {'group_id': 11, 'keyword_id': [67]}]
        self.assertEqual(result, expected)        




if __name__ == '__main__':
    unittest.main()        
