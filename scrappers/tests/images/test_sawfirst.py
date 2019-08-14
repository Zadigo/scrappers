from scrappers.scrappers.images.sawfirst import SawFirst
import unittest

class TestSawfirst(unittest.TestCase):
    def setUp(self):
        url = 'https://www.sawfirst.com/adriana-lima-booty-in-bikini-on-the-beach-in-miami-2019-08-14.html/supermodel-adriana-lima-wears-a-tiny-string-bikini-as-she-hits-the-beach-in-miami-2'
        self.sawfirst = SawFirst(url, 'Adrianna Lima')

    # def test_output_url(self):
    #     self.assertRegex(self.sawfirst.urls[0], r'https?:\/\/w.*\.com\w.*')

    def test_output_urls(self):
        self.assertIsInstance(self.sawfirst.urls, list)

if __name__ == "__main__":
    unittest.main()
