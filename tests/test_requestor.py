import unittest

from bs4 import BeautifulSoup

from scrappers.engine.requestor import Requestor


class TestRequestor(unittest.TestCase):
    def setUp(self):
        self.requestor = Requestor('http://www.example.com')

    def test_successful_connection(self):
        self.assertEqual(self.requestor.response.status_code, 200)
    
    def test_soup_object(self):
        # Assert soup is a BeautifulSoup object
        self.assertTrue(isinstance(self.requestor.soup, BeautifulSoup))

if __name__ == "__main__":
    unittest.main()
