import unittest

from bs4 import BeautifulSoup

from scrappers.scrappers.config.http.engine import Requestor


class TestRequestor(unittest.TestCase):
    def setUp(self):
        requestor = Requestor()
        self.soup = requestor.create_request('http://www.example.com')

    def test_soup_object(self):
        # Assert soup is a BeautifulSoup object
        self.assertTrue(isinstance(self.soup, BeautifulSoup))

    def test_soup_is_functionnal(self):
        self.assertEqual(self.soup.find('title').text, 'Example Domain')

if __name__ == "__main__":
    unittest.main()
