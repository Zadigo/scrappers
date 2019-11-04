import unittest

from scrappers.scrappers.config.utilities import new_filename, prepare_values


class TestUtilities(unittest.TestCase):
    def test_new_filename(self):
        # ex. eugenie_bouchard_2019_7_1356e0.json
        result = new_filename('eugenie_bouchard')
        self.assertRegex(result, r'\w+\_\w+\_\d{4}\_\d+\_[a-z0-9]+\.\w+')
        self.assertRegex(result, r'eugenie\_bouchard\_\d{4}\_\d+\_[a-z0-9]+\.\w+')

    def test_decorator(self):
        class Test:
            @prepare_values
            def save(self):
                values = ['a', 'b', 'c']
                return values
        
        # prepare(self, celibrity=None)
        self.assertEqual(Test().save.__name__, 'prepare')

if __name__ == "__main__":
    unittest.main()
