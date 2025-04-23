import unittest

from Demo.keyword_matcher import keywordmatcher

class TestKeywordMatcher(unittest.TestCase):

    def test_exact_match(self):
        """Test when text and keyword are exactly the same."""
        self.assertTrue(keywordmatcher("Out of Office", "OUT OF OFFICE"))

    def test_isolated_word_match(self):
        """Test cases where keyword is isolated by non-alphanumeric characters."""
        self.assertTrue(keywordmatcher("Automated Reply: I am out of office", "Automated Reply"))
        self.assertTrue(keywordmatcher("i will be out of office!!!", "Out of Office"))
        self.assertTrue(keywordmatcher("1234 hello 5678", "hello"))

    def test_embedded_word_no_match(self):
        """Test cases where keyword is embedded within a word and shouldn't match."""
        self.assertFalse(keywordmatcher("testing", "test"))
        self.assertFalse(keywordmatcher("AUTOMATIC", "Auto"))

    def test_boundary_cases(self):
        """Test cases where the keyword is at the beginning or end."""
        self.assertTrue(keywordmatcher("test email", "test"))
        self.assertTrue(keywordmatcher("email test", "test"))

    def test_repeated_words(self):
        """Test cases with repeated words and spaces."""
        self.assertTrue(keywordmatcher("o ooo", "o"))
        self.assertFalse(keywordmatcher("oo o o oo", "ooo"))

    def test_number_separation(self):
        """Test cases with numbers separating words."""
        self.assertFalse(keywordmatcher("hello123world", "world"))
        self.assertFalse(keywordmatcher("url=http%3A%2F%2F unsubscribe .", "unsubscribe"))




if __name__ == '__main__':
    unittest.main()
