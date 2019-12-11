import unittest

from scrappers.scrappers.config.config import Configuration, configuration


class TestInstance(unittest.TestCase):
    def setUp(self):
        self.configuration = configuration

    def test_is_dict(self):
        self.assertIsInstance(configuration, dict)

    def test_top_level_dir(self):
        self.assertEqual(self.configuration['base_path'], 'C:\\Users\\Zadigo\\Documents\\Apps\\scrappers')

if __name__ == "__main__":
    unittest.main()
