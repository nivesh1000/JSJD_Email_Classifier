import unittest

from app.keyword_matcher import keywordmatcher
from app.keyword_matcher_ii import keywordmatcher as keywordmatcher_ii


class TestKeywordMatcher(unittest.TestCase):

    def test_exact_match(self):
        """Test when text and keyword are exactly the same."""
        self.assertTrue(keywordmatcher("Out of Office", "OUT OF OFFICE"))
        self.assertTrue(keywordmatcher_ii("Out of Office", "Out of Office"))

    def test_punctuation_word_match(self):
        """Test cases where keyword is isolated by non-alphanumeric characters."""
        self.assertTrue(keywordmatcher(
            "Automated Reply: I am out of office", "Automated Reply"))
        self.assertTrue(keywordmatcher(
            "i will be out of office!!!", "Out of Office"))
        self.assertTrue(keywordmatcher_ii(
            "Automated Reply: I am out of office", "Automated Reply"))
        self.assertTrue(keywordmatcher_ii(
            "i will be out of office!!!", "Out of Office"))

    def test_embedded_word_match(self):
        self.assertTrue(keywordmatcher("1234 hello 5678", "hello"))
        self.assertFalse(keywordmatcher("hello1234", "hello"))    
        
        self.assertTrue(keywordmatcher_ii("1234 hello 5678", "hello"))
        self.assertFalse(keywordmatcher_ii("hello1234", "hello"))

    def test_embedded_word_no_match(self):
        """Test cases where keyword is embedded within a word and shouldn't match."""
        self.assertFalse(keywordmatcher("testing", "test"))
        self.assertFalse(keywordmatcher("AUTOMATIC", "Auto"))

        self.assertFalse(keywordmatcher_ii("testing", "test"))
        self.assertFalse(keywordmatcher_ii("AUTOMATIC", "Auto"))

    def test_boundary_cases(self):
        """Test cases where the keyword is at the beginning or end."""
        self.assertTrue(keywordmatcher("test email", "test"))
        self.assertTrue(keywordmatcher("test email", "test"))
        self.assertTrue(keywordmatcher_ii("email test", "test"))
        self.assertTrue(keywordmatcher_ii("email test", "test"))

    def test_repeated_words(self):
        """Test cases with repeated words and spaces."""
        self.assertTrue(keywordmatcher("o ooo", "o"))
        self.assertTrue(keywordmatcher("o ooo", "o"))
        self.assertFalse(keywordmatcher_ii("oo o o oo", "ooo"))
        self.assertFalse(keywordmatcher_ii("oo o o oo", "ooo"))

    def test_number_separation(self):
        """Test cases with numbers separating words."""
        self.assertFalse(keywordmatcher_ii("hello123world", "world"))
        self.assertFalse(keywordmatcher_ii("hello123world", "world"))
        self.assertFalse(keywordmatcher_ii("hello123world", "hello"))
        self.assertFalse(keywordmatcher_ii("hello123world", "hello"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
