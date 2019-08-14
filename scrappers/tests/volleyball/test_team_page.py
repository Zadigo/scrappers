import unittest
from collections import namedtuple
from scrappers.scrappers.volleyball.volleyball import IndivualTeamPage

class TestTeamPage(unittest.TestCase):
    def setUp(self):
        self.teampage = IndivualTeamPage()

    def test_can_get_teampage(self):
        url = 'https://www.volleyball.world/en/vnl/women/teams/dom-dominican%20republic/team_roster'
        players = self.teampage.unique_team_page(url)

        self.assertIsInstance(players, list)
        # self.assertIsInstance(players[0], namedtuple)

    def test_get_age(self):
        age = self.teampage.get_age('01/05/2000')

        self.assertEqual(age, 19)

    def test_convert_height(self):
        # 193 is 6'3"
        self.assertEqual(self.teampage.convert_height(193), 6.3)

if __name__ == "__main__":
    unittest.main()