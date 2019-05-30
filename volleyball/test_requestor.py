import unittest
import base_volleyball
import requests
import re

class RequestorTest(unittest.TestCase):
    def setUp(self):
        self.requestor = base_volleyball.Requestor()
        self.response = self.requestor.create_request('https://www.volleyball.world/en/vnl/women/teams')

    def test_response_is_correct(self):
        self.assertIs(self.response.__class__, list)
        self.assertEqual(len(self.response), 2)
        self.assertEqual(self.response[0].status_code, 200)

    def base_url_is_correct(self):
        # Respects https://www.volleyball.world
        is_correct = re.match(r'https?\:\/\/www\.\w+\.\w+', self.requestor.base_url)
        # self.assertEqual(is_correct)
        test_response = requests.get(self.requestor.base_url)
        self.assertEqual(test_response.status_code, 200)

    def test_text_is_stripped(self):
        self.assertEqual(self.requestor.clean_text(' Pauline '), 'Pauline')

if __name__ == "__main__":
    unittest.main()