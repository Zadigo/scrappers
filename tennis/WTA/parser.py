"""Module created to parse the HTML of a WTA's player page
and extract all the statistics related to their matches to
a given JSON file.

This application was created as way to automate and speed up
the process of gathering data from matches played by WTA players.

John PENDENQUE @ 2019
"""

import argparse
import collections
import datetime
import json
import os
import re
import secrets
import time

import requests
from bs4 import BeautifulSoup

from tennis.wta.models import Player, Tournament, TournamentMatch

environment = os.environ

HOME_DRIVE = '%s\\Users\\%s\\Documents' % (
    environment.get('HOMEDRIVE'),
    environment.get('USERNAME')
)

OUTPUT_DIR = 'WTA_Data'

def check_path(folder_or_file):
    """Checks if the path exists and creates the required files.
    
    The `folder_or_file` parameter should be a folder or file name that
    is checked in the HOMEDRIVE user path.
    """
    path = os.path.join(HOME_DRIVE, folder_or_file)
    path_exists = os.path.exists(path)
    if not path_exists:
        user_input = input('The path (%s) does not exist. '
                                'Do you wish to create it? (Y/N) ' % folder_or_file)

        if user_input == 'Y':
            # Create
            os.makedirs(path)
            print('Created!')
            return path
        elif user_input == 'N':
            quit
        else:
            quit
    else:
        return path

def new_filename(name):
    """Create a new file name: `name_2019_05_AVSOIV`
    """    
    current_date = datetime.datetime.now()
    token = secrets.token_hex(3)
    return f'{name.lower()}_{current_date.year}_{current_date.month}_{token}.json'

class ParsePage:
    """Parse the WTA's player matches' page to extract
    the statistics.
    
    The top level `div`, if extracted, should be
    `div.horizontal-tabs` containing all the sections for
    the matches (or relevant statistics). For example:

        <html>
            <body>
                <div class="horizontal-tabs">
                    ...
                </div>
            </body>
        </html>
    """
    def __init__(self, page_name=None, output_dir=OUTPUT_DIR):
        # Path to the file to parse -- Check the path
        # and return it if it exists
        # path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html.html')
        path = os.path.join(check_path(OUTPUT_DIR), page_name)
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # div.data-player-matches
            sections = soup.find_all('div', attrs={'class': 'data-player-matches'})

            tournaments = []
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
                        # and can then throw attribute errors on normalization
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
                        # If no match, protect!
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

                    # Create the opponent
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

            # TODO: Use OUTPUT_DIR instead
            # path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matches.json')
            output_path = os.path.join(HOME_DRIVE, OUTPUT_DIR, new_filename('eugenie_bouchard'))

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(refactored_stats, f, indent=4)
                print('Created file! (%s)' % output_path)

# class GetPlayer:
#     def __init__(self):
#         try:
#             response = requests.get('https://www.wtatennis.com/players/player/314206/title/petra-kvitova-0', headers=headers)
#         except requests.exceptions.HTTPError():
#             raise
#         else:
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.text, 'html.parser')

#         # Height
#         height = soup.find('div', attrs={'class': 'field--name-field-height'})\
#                     .find('div', attrs={'class': 'field__item'}).text

#         # Date of birth
#         date_of_birth = soup.find('span', attrs={'class': 'date-display-single'}).text

#         # Playing hand
#         playing_hand = soup.find('div', attrs={'class': 'field--name-field-playhand'})\
#                             .find('div', attrs={'class': 'field__item'}).text
