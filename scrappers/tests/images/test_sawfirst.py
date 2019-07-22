from scrappers.scrappers.images.sawfirst import SawFirst
import unittest

class TestSawfirst(unittest.TestCase):
    def setUp(self):
        self.sawfirst = SawFirst('http://', 'Selena Gomez')

    def test_output_result(self):
        # self.sawfirst.soup
        pass