from scrappers.apps.images.base import SawFirst
import unittest

class TestSawfirst(unittest.TestCase):
    def setUp(self):
        url = 'https://www.sawfirst.com/adriana-lima-booty-in-bikini-on-the-beach-in-miami-2019-08-14.html/supermodel-adriana-lima-wears-a-tiny-string-bikini-as-she-hits-the-beach-in-miami-2'
        self.sawfirst = SawFirst(url, celibrity_name='Adrianna Lima')

if __name__ == "__main__":
    unittest.main()
