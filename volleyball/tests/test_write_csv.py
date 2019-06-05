import unittest
from base_volleyball import WriteCSV
import requests
import re

class TestWriteCSV(unittest.TestCase):
    def setUp(self):
        self.write_csv = WriteCSV()

    def test_is_path(self):
        is_path = re.match(r'[a-zA-Z]\:(?:\\\w+)+', self.write_csv.create_new_file)
        self.assertTrue(is_path)

if __name__ == "__main__":
    unittest.main()