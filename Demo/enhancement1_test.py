import unittest
from Demo.enhancement1 import extract_email_from_body # This function should now return a single email or None

class TestEmailExtraction(unittest.TestCase):

    def test_valid_emails(self):
        text = "Contact us at nivesh.nk@gmail.com or nivesh@cynoteck.com."
        expected_output = "nivesh.nk@gmail.com"
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_no_emails(self):
        text = "No emails here, just some random text."
        expected_output = None
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_emails_with_special_characters(self):
        text = "Emails like xax.io should not be found and test.email.alex@leetcode.com can be found."
        expected_output = "test.email.alex@leetcode.com"
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_multiline_emails(self):
        text = '''
        first@mail.com
        last@mail.com'''
        expected_output = "first@mail.com"
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_emails_with_unicode_characters(self):
        text = "\ufeffnivesh@cynoteck.com‌ or \xa0support@domain.com\uFFFC"
        expected_output = "nivesh@cynoteck.com"
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_email_at_beginning(self):
        text = "first@email.com is the contact, not second@email.com"
        expected_output = "first@email.com"
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_email_with_trailing_punctuation(self):
        text = "Please email: hello.world@domain.com! It's urgent."
        expected_output = "hello.world@domain.com"
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_email_inside_sentence_with_noise(self):
        text = "junk!!##nobody@somewhere.io##!! then person@domain.com"
        expected_output = "nobody@somewhere.io"
        self.assertEqual(extract_email_from_body(text), expected_output)

    def test_for_invaid_emails(self):
        text = "Contact at some@email or email@.com or @missing.com"
        expected_output = None
        self.assertEqual(extract_email_from_body(text), expected_output)


if __name__ == "__main__":
    unittest.main()
