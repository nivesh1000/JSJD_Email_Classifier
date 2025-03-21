import unittest
from anchortag_handler import normalize_by_removing_anchor_tag
import textwrap

multple_anchor_tag_text_before_removal="""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
        Visit our <a href='https://example.com'>website</a> for more info. 
        Nullam in <a href='https://example.org'>another site</a> too.
        Here's more text without links. 
        """
multple_anchor_tag_text_after_removal="""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
        Visit our  for more info. 
        Nullam in  too.
        Here's more text without links. 
        """

class TestAnchorTagRemoval(unittest.TestCase):

    def test_removal_of_nested_anchor_tags(self):
        text = "<div><a href='#'><b>Bold Link</b></a></div>"
        expected_output = "<div></div>"
        self.assertEqual(normalize_by_removing_anchor_tag(text), expected_output)

    def test_removal_of_anchor_tag_with_text_before_and_after(self):
        text = "Before <a href='#'>Link</a> After"
        expected_output = "Before  After"
        self.assertEqual(normalize_by_removing_anchor_tag(text), expected_output)

    def test_removal_of_multiple_anchor_tags(self):
        text = multple_anchor_tag_text_before_removal
        expected_output = multple_anchor_tag_text_after_removal
        self.assertEqual(normalize_by_removing_anchor_tag(text), expected_output)

    def test_no_anchor_tags(self):
        text = "No links here!"
        expected_output = "No links here!"
        self.assertEqual(normalize_by_removing_anchor_tag(text), expected_output)

    def test_removal_of_anchor_tag_with_arguments(self):
        text = "<a href='https://example.com?query=test&ref=123'>Query Link</a>"
        expected_output = ""
        self.assertEqual(normalize_by_removing_anchor_tag(text), expected_output)

    def test_removal_of_broken_anchor_tag(self):
        text = "Here is some text <a href='#'>Unclosed anchor"
        expected_output = "Here is some text "
        self.assertEqual(normalize_by_removing_anchor_tag(text), expected_output)

if __name__ == "__main__":
    unittest.main()
