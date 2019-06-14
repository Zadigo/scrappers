import os
from bs4 import BeautifulSoup
import requests
import json
import datetime
import time
import collections
import re
import argparse

class Tournament(dict):
    """Object representing the details of a WTA tournament
    """
    def __init__(self, tournament, date, level, surface, rank, seed):
        self.update(
            {
                'tournament': self.parse_tour_name(tournament),
                'country': self.parse_tour_name(tournament, tour_or_country=True),
                'date': self.normalize_date(date),
                'level': self.normalize(level),
                'surface': self.normalize(surface),
                'rank': rank,
                'seed': seed
            }
        )
    
    @staticmethod
    def normalize(value):
        if not value:
            return None
        return value.strip().lower()

    @staticmethod
    def normalize_date(d):
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December']
        is_valid = re.match(r'^([A-Z]\w+)\s+(\d+)\S\s+(\d+)', d)
        if is_valid:
            day = is_valid.group(2)
            month = is_valid.group(1).strip()
            year = is_valid.group(3)
            month_index = months.index(month) + 1
            formatted_date = f'{year}-{month_index}-{day}'
        return formatted_date

    def parse_tour_name(self, tour_name, tour_or_country=False):
        tournament, country = tour_name.split(',', 1)
        if tour_or_country:
            return self.normalize(tournament)
        else:
            return self.normalize(country)

    @staticmethod
    def parse_integer(value):
        if not value:
            return None
        return int(value)

class TournamentMatch(Tournament):
    """Object representing the details of a WTA tournament
    tennis match.
    """
    def __init__(self, match_round, result, score, rank, opponent_seed):
        self.update(
            {
                'match_round': match_round,
                'result': result,
                'score': self.normalize(score),
                'rank': self.normalize(rank),
                'opponent_seed': self.normalize(opponent_seed)
            }
        )

class ParsePage:
    """Parse the WTA's player matches' page to extract
    the statistics. The top level `div` should be
    `div.horizontal-tabs` containing all the sections for
    the matches (or relevant statistics)
    """
    def __init__(self):
        # Path to the file to parse
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html.html')
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

            # div.data-player-matches
            sections = soup.find_all('div', attrs={'class': 'data-player-matches'})

            tournaments=[]
            matches = []

            for section in sections:
                # ex. WATERLOO , CANADA
                tournament = section.find('span', attrs={'class': 'tour-name'}).text

                # span.tour-detail
                tour_details = section.find_all('span', attrs={'class': 'tour-detail'})
                # ex. October 20, 2008
                tour_date = tour_details[0].text
                # ex. ITF, Tier I...
                level = tour_details[1].text
                # ex. Clay
                surface = tour_details[2].text

                # tour_infos = section.find_all('span', attrs={'class': 'tour-info'})
                # print(tour_infos)

                # tbody
                matches_table_row = section.find('tbody').find_all('tr')
                for row in matches_table_row:
                    # ex. Round 16
                    match_round = row.find('td', attrs={'class': 'round'}).text
                    # ex. L
                    result = row.find('td', attrs={'class': 'result'}).text
                    try:
                        # IMPORTANT: These values can be null or incorrect
                        # and can then through attribute errors on normalization
                        # so we have to protect against that
                        # ex. [3]
                        opponent_seed = row.find('div', attrs={'class': 'opponent-seed'}).text
                        # ex. 45
                        rank = row.find('td', attrs={'class': 'rank'}).text
                    except AttributeError:
                        opponent_seed = None
                        rank = None
                    # ex. 6-1 6-1
                    score = row.find('td', attrs={'class': 'score'}).text
                    # [{match A}, {...}]
                    matches.append(TournamentMatch(match_round, result, score, rank, opponent_seed))

                # [{tournament A}, ...]
                tournament = Tournament(tournament, tour_date, level, surface, 14, 14)
                # [{tournament A, matches: []}, ...]
                tournament.update({'matches': matches})
                tournaments.append(tournament)
                # IMPORTANT: We have to reset the matches cache
                # otherwise the other matches from the other sections
                # will append resulting in tournaments having all the
                # same matches
                matches = []

            # Construct a dict wrapper
            # for convenience
            refactored_stats = {
                'records': tournaments
            }

            # Path to output file
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matches.json')

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(refactored_stats, f, indent=4)

# if __name__ == "__main__":
#     WtaPage()

ParsePage()