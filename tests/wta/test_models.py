import unittest
from tennis.wta.models import Player, Tournament, TournamentMatch

# python -m unittest wta.test_models.TestModels.test_normalization

# class TestModels(unittest.TestCase):
#     def setUp(self):
#         self.tournament = Tournament(1, 'Australian Open', 'January 1, 2019', 'GS', 'Hard', 1, 1)
    
#     def test_player(self):
#         self.assertDictEqual(Player('Eugénie Bouchard', 'CAN', '/'), 
#                     {'name': 'Eugénie Bouchard', 'country': 'CAN', 'url_path': '/'})

class TestTournament(unittest.TestCase):
    def setUp(self):
        self.tournament = Tournament
    
    # def test_tournament(self):
    #     self.assertDictEqual(self.tournament, {'name': 'Eugénie Bouchard', 'country': 'CAN', 'url_path': '/'})

    def test_normalization(self):
        self.assertEqual(self.tournament.normalize('eugenie bouchard'), 'Eugenie Bouchard')

    def test_normalize_date(self):
        self.assertEqual(self.tournament.normalize_date('January 1, 2019'), '2019-1-1')

    def test_parse_integer_regex(self):
        self.assertEqual(self.tournament.parse_integer_regex("          14"), 14)

class TestTournamentMatch(unittest.TestCase):
    def setUp(self):
        self.tournament_match = TournamentMatch

    def test_sets_played(self):
        self.assertEqual(self.tournament_match.sets_played('6-1 6-1'), 'two')
        self.assertEqual(self.tournament_match.sets_played('6-1 4-6 6-1'), 'three')
        self.assertEqual(self.tournament_match.sets_played('7-6(2) 7-6(3)'), 'two')
        self.assertEqual(self.tournament_match.sets_played('7-6(4) 6-7(4) 7-6(4)'), 'three')
        self.assertEqual(self.tournament_match.sets_played('7-6(4) 6-7(4) 6-4'), 'three')

    def test_first_set(self):
        self.assertEqual(self.tournament_match.first_set('6-1 6-1', 'W'), 'won')
        self.assertEqual(self.tournament_match.first_set('6-1 6-1', 'L'), 'lost')

        self.assertEqual(self.tournament_match.first_set('1-6 6-1 6-1', 'W'), 'lost')
        self.assertEqual(self.tournament_match.first_set('1-6 6-1 6-1', 'L'), 'won')

        # self.assertEqual(self.tournament_match.first_set('6-7(4) 6-1 6-1', 'W'), 'lost')
        # self.assertEqual(self.tournament_match.first_set('6-7(4) 6-1 6-1', 'L'), 'won')

if __name__ == "__main__":
    unittest.main()
