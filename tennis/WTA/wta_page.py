"""Module created to parse the HTML of a WTA's player page
and extract all the statistics related to their matches to
a JSON file.
"""

import argparse
import collections
import datetime
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = os.environ.get('')


class Tournament(dict):
    """Object representing the details of a WTA tournament
    """
    def __init__(self, tour_id, tournament, date, level, surface, rank, seed):
        self.update(
            {
                "id": tour_id,
                'tournament': self.parse_tour_name(tournament, tour_or_country=True),
                'country': self.parse_tour_name(tournament),
                'date': self.normalize_date(date),
                'level': self.normalize(level),
                'surface': self.normalize(surface),
                'rank': self.parse_integer_regex(rank),
                'seed': self.parse_integer_regex(seed)
            }
        )
    
    @staticmethod
    def normalize(value):
        if not value:
            return None
        return value.strip().lower().capitalize()

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

    @staticmethod
    def parse_integer_regex(value):
        if not value:
            return None
        # ex. \n              18
        # ex. \nSeed Entry: \n  18
        is_match = re.match(r'\s+(\[?\d+\]?)', str(value))
        if is_match:
            return int(str(is_match.group(1)).strip())
        else:
            # Case where the number is [4]
            try_pattern = re.match(r'\[?(\d+)\]?', str(value))
            if try_pattern:
                return int(str(try_pattern.group(1)).strip())
        return None

class TournamentMatch(Tournament):
    """Object representing the details of a WTA tournament
    tennis match.
    """
    def __init__(self, match_round, result, score, rank, seed):
        score = self.normalize(score)
        match_round = self.normalize(match_round)
        rank = self.parse_integer_regex(rank)
        seed = self.parse_integer_regex(seed)

        self.update(
            {
                'match_round': match_round,
                'result': result,
                'score': score,
                'sets_played': self.sets_played(score),
                'first_set': self.first_set(score, result),
                'rank': rank,
                'seed': seed,
                'opponent_details': []
            }
        )
    
    @staticmethod
    def first_set(score, result):
        """Determine if the first set was won or lost
        """
        if result == 'L':
            # 6-2 6-3
            # 7-5 6-3
            # 7-6(6) 6-4
            is_match = re.search(r'^((?:6|7)\-?\d+)', score)
            if is_match:
                return 'lost'
            else:
                # 2-6 6-3
                # 5-7 6-3
                # 6-7(6) 6-4
                is_match = re.search(r'^(\d+\-(?:6|7))', score)
                if is_match:
                    return 'win'
        elif result == 'W':
            is_match = re.search(r'^((?:6|7)\-?\d+)', score)
            if is_match:
                return 'won'
            else:
                is_match = re.search(r'^(\d+\-(?:6|7))', score)
                if is_match:
                    return 'lost'

    @staticmethod
    def sets_played(score):
        patterns = [
            # 6-2 6-3
            # 7-5 6-3
            # 7-6(4) 7-6(4)
            r'^\d+\-\d+\(?\d?\)?\s+\d+\-\d+\(?\d?\)?$',
            # 6-7(6) 6-4 6-4
            # 6-4 3-6 7-5
            # 6-4 3-6 7-5
            # 7-6(4) 6-7(4) 7-6(4)
            r'^\d+\-\d+\(?\d?\)?\s+\d+\-\d+\(?\d?\)?\s+\d+\-\d+\(?\d?\)?$'
        ]
        for pattern in patterns:
            is_match = re.match(pattern, score)
            if is_match:
                pattern_index = patterns.index(pattern)
                if pattern_index == 0:
                    number_of_sets = 'two'
                else:
                    number_of_sets = 'three'
                break
            else:
                number_of_sets = 'two'
        
        return number_of_sets

class Player(TournamentMatch):
    def __init__(self, name, country, url_path):
        self.update(
            {
                'name': self.normalize(name),
                'country': country,
                'url_path': url_path,
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
            tour_id = 1

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

                # div.row-item
                tour_infos = section.find('div', attrs={'class': 'last-row'}) \
                                        .find_all('div', attrs={'class': 'row-item'})
                # ex. 15
                rank = tour_infos[2].text
                # ex. 6
                seed = tour_infos[3].text

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

                    # td.opponent
                    opponent_row = row.find('td', attrs={'class': 'opponent'})

                    # <a href="">...</a>
                    opponent_details = opponent_row.findChild('a')
                    # Use REGEX to parse that row since
                    # there are lots of \s and \n e.g
                    # \n
                    # [Q] Carmen\n
                    #                  Klaschka (GER)
                    # Get a group such as ('Carmen', 'Klaschka', 'GER')
                    parsed_text = re.search(r'^\n?(?:\[(\d+|\w+)\]\s+)?(\w+)\n?\s+(\w+)\s+(?:\((\w+)\))', opponent_row.text)
                    try:
                        # If no match, protect
                        # ex. Carmen Klaschka
                        opponent_name = ' '.join([parsed_text.group(2), parsed_text.group(3)])
                        # ex. CAN
                        opponent_country = parsed_text.group(4)
                    except AttributeError:
                        opponent_name = None
                        opponent_country = None
                    
                    try:
                        # ex. /players/player/311649/title/carmen-klaschka
                        profile_url_path = opponent_details['href']
                    except TypeError:
                        profile_url_path = None

                    opponent = Player(opponent_name, opponent_country, profile_url_path)

                    # [{match A}, {...}]
                    tournament_match = TournamentMatch(match_round, result, score, rank, opponent_seed)
                    tournament_match.update({'opponent_details': opponent})
                    matches.append(tournament_match)

                # [{tournament A}, ...]
                tournament = Tournament(tour_id, tournament, tour_date, level, surface, rank, seed)
                # [{tournament A, matches: []}, ...]
                tournament.update({'matches': matches})
                tournaments.append(tournament)
                # IMPORTANT: We have to reset the matches cache
                # otherwise the other matches from the other sections
                # will append resulting in tournaments having all the
                # same matches
                matches = []

                # Update ID
                tour_id = tour_id + 1

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
#     args = argparse.ArgumentParser()
#     args.add_argument('--path', help='Relative path to a file or file name')
#     parsed_args = args.parse_args()
ParsePage()
