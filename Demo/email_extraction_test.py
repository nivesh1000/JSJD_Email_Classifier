import unittest
from email_extraction import extract_emails

class TestEmailExtraction(unittest.TestCase):

    def test_valid_emails(self):
        text = "Contact us at nivesh.nk@gmail.com or nivesh@cynoteck.com."
        expected_output = ["nivesh.nk@gmail.com", "nivesh@cynoteck.com"]
        self.assertEqual(extract_emails(text), expected_output)

    def test_no_emails(self):
        text = "No emails here, just some random text."
        expected_output = []
        self.assertEqual(extract_emails(text), expected_output)

    def test_emails_with_special_characters(self):
        text = "Emails like test.email.alex@leetcode.com and xax.io should not be found."
        expected_output = ["test.email.alex@leetcode.com"]
        self.assertEqual(extract_emails(text), expected_output)

    def test_multiline_emails(self):
        text = '''
        start@mail.com
        end@mail.com'''
        expected_output = ["start@mail.com", "end@mail.com"]
        self.assertEqual(extract_emails(text), expected_output)


    def test_emails_with_unicode_characters(self):
        text = "\ufeffnivesh@cynoteck.com‌ or \xa0support@domain.com\uFFFC"
        expected_output = ["nivesh@cynoteck.com", "support@domain.com"]
        self.assertEqual(extract_emails(text), expected_output)    



if __name__ == "__main__":
    unittest.main()
