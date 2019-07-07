import unittest

from scrappers.engine import user_agent

class TestRequestor(unittest.TestCase):
    def test_agents_list(self):
        self.assertIsInstance(user_agent.AGENTS_LIST, list)
        self.assertGreater(len(user_agent.AGENTS_LIST), 0)

    def test_rand_agent(self):
        self.assertIsNotNone(user_agent.get_rand_agent())

    def test_agent(self):
        self.assertIsNotNone(user_agent.get_user_agent(0))

    def test_unique_agent(self):
        self.assertIsInstance(user_agent.get_rand_unique_agent, str)

    def test_cache_decorator(self):
        def test_agent():
            return 'Mozilla 1.1'

        result = user_agent.cached_agents(test_agent)
        
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'Mozilla 1.1')
    

if __name__ == "__main__":
    unittest.main()
