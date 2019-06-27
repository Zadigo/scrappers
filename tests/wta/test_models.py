import unittest
from tennis.wta.models import Player, Tournament, TournamentMatch

class TestModels(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_player(self):
        self.assertDictEqual(Player('Eugénie Bouchard', 'CAN', '/'), 
                    {'name': 'Eugénie Bouchard', 'country': 'CAN', 'url_path': '/'})
    
    def test_tournament(self):
        tournament = Tournament(1, 'Australian Open', '2019-01-22', 'GS', 'Hard', 1, 1)
        self.assertDictEqual(tournament, {'name': 'Eugénie Bouchard', 'country': 'CAN', 'url_path': '/'})


if __name__ == "__main__":
    unittest.main()
