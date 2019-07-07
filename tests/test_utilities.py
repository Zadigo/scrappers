import unittest

from scrappers.engine import utilities

class TestUtilities(unittest.TestCase):
    def test_new_filename(self):
        # ex. eugenie_bouchard_2019_7_1356e0.json
        result = utilities.new_filename('eugenie_bouchard')
        self.assertRegex(result, r'\w+\_\w+\_\d{4}\_\d+\_[a-z0-9]+\.\w+')
        self.assertRegex(result, r'eugenie\_bouchard\_\d{4}\_\d+\_[a-z0-9]+\.\w+')

if __name__ == "__main__":
    unittest.main()
