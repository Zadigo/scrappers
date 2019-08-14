import re
import unittest

from scrappers.scrappers.volleyball.volleyball import ParticipatingTeamsPage	


class TestTeamsPage(unittest.TestCase):
    def setUp(self):
        teams_page = ParticipatingTeamsPage()
        self.teams = teams_page.get_teams('http://u20.women.2017.volleyball.fivb.com/en/teams')

    def test_is_array(self):
        self.assertIsInstance(self.teams, list, msg='Is not an array')

    def test_has_tuple(self):
        self.assertIsInstance(self.teams[0], tuple)

    def test_tuple_is_two(self):
        self.assertEqual(len(self.teams[0]), 2)

    def test_tuple_has_valid_link(self):
        self.assertRegex(self.teams[0][0], r'https?\:\/\/(?:\w+\.)+com(?:\/\w+\-?\w+)+\/?')

if __name__ == "__main__":
    unittest.main()
