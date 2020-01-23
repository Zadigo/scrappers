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

# from scrappers.scrappers.config.config import configuration
# from scrappers.scrappers.config.utilities import check_path, new_filename
# from scrappers.scrappers.tennis.wta.models import (Player, Tournament,
#                                                    TournamentMatch)

# environment = os.environ

# HOME_DRIVE = '%s\\Users\\%s\\Documents' % (
#     environment.get('HOMEDRIVE'),
#     environment.get('USERNAME')
# )

OUTPUT_DIR = 'WTA_Data'

# TODO: Erase
# def check_path(folder_or_file):
#     """Checks if the path exists and creates the required files.
    
#     The `folder_or_file` parameter should be a folder or file name that
#     is checked in the HOMEDRIVE user path.
#     """
#     path = os.path.join(HOME_DRIVE, folder_or_file)
#     path_exists = os.path.exists(path)
#     if not path_exists:
#         user_input = input('The path (%s) does not exist. '
#                                 'Do you wish to create it? (Y/N) ' % folder_or_file)

#         if user_input == 'Y':
#             # Create
#             os.makedirs(path)
#             print('Created!')
#             return path
#         elif user_input == 'N':
#             quit
#         else:
#             quit
#     else:
#         return path

# def new_filename(name):
#     """Create a new file name: `name_2019_05_AVSOIV`
#     """    
#     current_date = datetime.datetime.now()
#     token = secrets.token_hex(3)
#     return f'{name.lower()}_{current_date.year}_{current_date.month}_{token}.json'


# from scrappers.apps.config.utilities import check_path
from scrappers.apps.tennis.wta.models import Player, Tournament, TournamentMatch

class ParsePage:
    """Parse the WTA's player matches' page to extract the statistics. 
    This class requires the source page to be downloaded or copy/pasted 
    on the local storage of the computer in `.html` file.
    
    The top level `div`, if extracted, should be `div.horizontal-tabs` containing 
    all the sections for the matches (or relevant statistics):

        html
            body
                div class="horizontal-tabs"
                    ...
                ddiv
            body
        html

    Parameters
    ----------

        page_name:

        output_dir: 
    """
    def __init__(self, page_name=None, output_dir=OUTPUT_DIR, class_attr='player-matches__content'):
        # FIXME: When the user enters the filename 'test' as
        # opposed to 'test.html', raises a FileNotFoundError
        
        # Path to the file to parse -- Check the path
        # and return it if it exists
        # path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html.html')
        # path = os.path.join(check_path(OUTPUT_DIR), page_name)
        path = 'C:\\Users\\Pende\\Documents\\myapps\\scrappers\\apps\\tennis\\wta\\test.html'
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Isolate the section that contains
            # all the matches for a given player
            # div.player-matches__content
            matches_section = soup.find('div', attrs={'class': class_attr})
            
            # Isolate each tennis match
            # div.player-matches__tournament-header
            sections = matches_section.find_all('div', attrs={'class': 'player-matches__tournament'})

            tournaments = []
            matches = []
            tour_id = 1

            for section in sections:
                # Work with the header
                header = section.find('div', attrs={'class': 'player-matches__tournament-header'})

                try:
                    # It appears that the link does not always contain
                    # a title, in which case, we have to get the name
                    # directly from the link text
                    link_for_tournament = header.find('a', attrs={'class': 'player-matches__tournament-title-link'})
                    # ex. Oracle Challenger Series
                    tournament_name = link_for_tournament['title']
                except:
                    tournament_name = None

                # ex. HOUSTON, USA, TX
                tournament_location = header.find('span', attrs={'class': 'player-matches__tournament-location'}).text
                # ex. Nov 10-Nov 17, 2019
                tournament_date = header.find('span', attrs={'class': 'player-matches__tournament-date'}).text

                # Tournament details
                tour_details = header.find_all('div', attrs={'class': 'player-matches__tournament-meta-item'})
                level = tour_details[0].find(attrs={'class': 'player-matches__tournament-meta-value'}).text
                surface = tour_details[2].find(attrs={'class': 'player-matches__tournament-meta-value'}).text

                matches_table_body = section.find('table', attrs={'class': 'player-matches__matches-table'}).find('tbody')
                rows = matches_table_body.find_all('tr')

                for row in rows:
                    # ex. Round 16
                    match_round = row.find('td', attrs={'class': 'player-matches__match-cell--round'}).text

                    opponent = row.find('div', attrs={'class': 'player-matches__match-opponent'})
                    # Path to profile
                    link_for_opponent = opponent.find('a')
                    path_to_profile = link_for_opponent['href']
                    # ex. Eugenie Bouchard
                    opponent_name = link_for_opponent['title']
                    # ex. CAN
                    opponent_country = opponent.find('span', attrs={'class': 'player-matches__match-opponent-country'}).text
                    # ex. W or L
                    result = row.find('td', attrs={'class': 'player-matches__match-cell--winloss'}).text
                    
                    try:
                        # ex. 3
                        opponent_rank = row.find('td', attrs={'class': 'player-matches__match-cell--opp-rank'}).text
                        # IMPORTANT: These values can be null or incorrect
                        # and can then throw attribute errors on normalization
                        # so we have to protect against that
                        # ex. [3]
                        opponent_seed = row.find('div', attrs={'class': 'player-matches__match-opponent-seed'}).text
                    except AttributeError:
                        # Opponent rank is often
                        # provided so we protect it
                        # just in case
                        if not opponent_rank:
                            opponent_rank = None
                        opponent_seed = None

                    # ex. 6-1 6-1
                    score = row.find('td', attrs={'class': 'player-matches__match-cell--score'}).text

                    # Create the opponent
                    opponent = Player(opponent_name, opponent_country, path_to_profile)
                    # [{match A}, {...}]
                    tournament_match = TournamentMatch(match_round, result, score, opponent_rank, opponent_seed)
                    tournament_match.update({'opponent_details': opponent})
                    matches.append(tournament_match)

                footer = section.find('div', attrs={'class': 'player-matches__tournament-footer'})
                meta_values = footer.find_all('span', attrs={'class': 'player-matches__tournament-meta-value'})
                # ex. 1
                player_rank = meta_values[0].text

                try:
                    # When the seed is present in the tags,
                    # we have four values instead of 3.
                    # If it's 4, we know the tag is in the
                    # list of tags
                    if len(meta_values) == 4:
                        # ex. 1
                        player_seed = meta_values[1].text
                    else:
                        player_seed = None
                except:
                    player_seed = None

                # [{tournament A}, ...]
                tournament = Tournament(tour_id, tournament_name, tournament_date, level, surface, player_rank, player_seed, tournament_location=tournament_location)
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

            # Construct output path
            # output_path = os.path.join(configuration.homedrive, OUTPUT_DIR, new_filename('eugenie_bouchard'))
            output_path = 'C:\\Users\\Pende\\Documents\\myapps\\scrappers\\apps\\tennis\\wta\\test.json'

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

# p = ParsePage()

import requests

response = requests.get('https://www.google.com/maps?q=Paris')
print(response.content)
