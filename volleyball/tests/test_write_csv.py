import os
import re
import unittest

import requests

from base_volleyball import WriteCSV


class TestWriteCSV(unittest.TestCase):
    def setUp(self):
        self.write_csv = WriteCSV()

    def test_is_path(self):
        is_path = re.match(r'[a-zA-Z]\:(?:\\\w+)+', self.write_csv.create_new_file)
        self.assertTrue(is_path)

    def test_current_file(self):
        self.assertIsNone(self.write_csv.current_file)

if __name__ == "__main__":
    unittest.main()
