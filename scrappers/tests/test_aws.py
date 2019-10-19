from scrappers.engine.aws import image_size_creator, create_object_url, unique_path_creator
import unittest

class TestUtilities(unittest.TestCase):
    def test_image_size_creator(self):
        result = image_size_creator('test/banners.jpg')

        self.assertIsInstance(result, dict)
        self.assertEqual(result['small'], 'test/banners-small.jpg')
        self.assertEqual(result['medium'], 'test/banners-medium.jpg')
        self.assertEqual(result['large'], 'test/banners-large.jpg')

        # Content type
        self.assertEqual(type(result['contenttype']), tuple)
        # self.assertListEqual(result['contenttype'], ('image/jpeg', None))
        self.assertTrue(result['contenttype'][0] == 'image/jpeg')

    def test_object_url(self):
        result = create_object_url('test/banners', 'france', 'banners')
        self.assertEqual(result, 'https://s3.france.amazonaws.com/banners/test/banners')

    def test_unique_path_creator(self):
        result = unique_path_creator('banners', 'test.jpeg', rename=False)
        
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['object_name'], list)

        self.assertListEqual(result['object_name'], ['test', ('image/jpeg', None)])

        self.assertRegex(result['object_path'], r'banners\/[a-z0-9]+\/test\.jpeg')