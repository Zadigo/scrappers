"""This module references a variety of scrappers that can be used
to get data from the FiVB website. It is composed of three main
classes which allows a variety of different actions.

Description
-----------

The ParticipatingTeamsPage class allows you to parse the whole teams
that would be present on the main competition page. It references the
urls for the individual team's page of that specific section.

author: pendenquejohn@gmail.com
"""

import argparse
import csv
import datetime
import os
import pickle
import re
import secrets
import threading
import time
from collections import deque, namedtuple
from urllib.parse import splitquery, unquote, urlencode, urljoin, urlparse

import requests

from scrappers.scrappers.config.config import configuration
from scrappers.scrappers.config.http.engine import Requestor
from scrappers.scrappers.config.http.user_agent import get_rand_agent
from scrappers.scrappers.config.utilities import (position_to_number,
                                                  prepare_values)
from scrappers.scrappers.utils.mixins import Mixin
from scrappers.scrappers.volleyball.models import Player


class ParticipatingTeamsPage(Requestor, Mixin):
    """This analyzes the page referencing the teams and parses the
    different countries present on that page with their urls.

    This parser should not really be used individually unless you need
    the raw values for doing something else. It is preferable to use the
    `TeamPage()` class which will pull the teams and then get each individual
    player's data.

    You can also subclass this class if you wish to do something different.

    Parameters
    ----------

    `url` is the page referencing all participating teams.

    Result
    ------

        [
            (https://path/to/team, Dominican Republic),
            (...)
        ]
    """
    def __init__(self):
        self.teams = []

    def get_teams(self, url):
        soup = self.create_request(url)
        
        # section#pools
        section = soup.find('section', id='pools')
        
        # <a></a>
        unparsed_links = section.find_all('a')

        # TODO: If we send relative path to requests,
        # there could be an issue
        parsed_links = self.parse_links(unparsed_links)

        self.teams = parsed_links
        return parsed_links

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.teams)

    def parse_links(self, links, relative=False):
        """Parse the links on the page referencing the teams playing in
        the competition and return a `list` such as [(link, country), ...].

        If `relative` is true, the definition returns the path
        of the link instead of the full url.

        Result
        ------

            [
                (http://path/to/..., USA)
            ]
        """
        parsed_links = []

        # Delete the two first links which
        # do not really correspond to links
        # related to volleyball teams
        links.pop(0)
        links.pop(0)

        for link in links:
            if relative:
                href = link['href']
            else:
                # Add a trailing slash so that python
                # appends additional paths instead of
                # cutting it off
                href = urljoin(self.base_url, link['href'] + '/team_roster')
            country = self.clean_text(link.find('figcaption').text)
            parsed_links.append((href, country))
        return parsed_links

class IndivualTeamPage(ParticipatingTeamsPage):
    """Extract the data related to players on each team's page.

    Description
    -----------

    You can use this class directly as an item over which can be iterated
    for example to print to a file. You can also use its dedicated functions
    in order to print to a file of type CSV or  JSON.

    Parameters
    ----------

    `url` is the page referencing all participating teams to
    be parsed afterwards
    """
    
    def team_page(self):
        """Parse a specific volleyball team's page starting from a page
        referencing all the participating teams of the competition.
        By doing so, we are trying to gather all the attributes 
        of a given player.

        Result
        ------

           [
                Player(name=Bieke Kindt, ...),
                ...
           ]

           Each player is a namedtuple containing the attributes of the
           given player:
           
           player_name
           
           player_profile_link
           
           date_of_birth
            
            age
            
            height
            
            weight
            
            spike
            
            block
        """
        pass

    def unique_team_page(self, url):
        return self.parse_page(self.create_request(url))

    def parse_page(self, soup):
        print('-'*15)

        current_date = datetime.datetime.now()
        print('GET HTTP/1.1', str(current_date))

        players = []

        # <tr>...</tr>
        rows = soup.findAll('tr')

        # Pop <tr><th>...</th></tr>
        rows.pop(0)

        # <td>...</td>
        for row in rows:
            items = row.find_all('td')
            
            # ex. Eugénie Constanza
            player_name = items[1].find('a').text
            # /en/vnl/women/teams/bel-belgium/players/eugenie-constanza?id=71449
            player_profile_link = items[1].find('a')['href']
            # 02/03/2000
            date_of_birth = items[2].text
            age = self.get_age(date_of_birth)
            # 196 (cm)
            height = items[3].text
            # 45 (kg)
            weight = items[4].text
            # 306 (cm)
            spike = items[5].text
            # 315 (cm)
            block = items[6].text

            # Player object
            player = Player(player_name, player_profile_link, date_of_birth,
                        age, height, weight, spike, block)

            # IMPROVE: Refactor
            # Append player object to an
            # array that will then be passed to
            # the WriteCSV class
            players.append(player)
    
        return players

    @staticmethod
    def get_age(date_of_birth, adjusted=False):
        """Returns the player's current age.

        Parameters
        ----------

        `adjusted` allows to calculate an age based on the
        year the tournament was played as opposed to using
        the current year
        """
        current_year = datetime.datetime.now().year
        date = datetime.datetime.strptime(date_of_birth, '%d/%m/%Y')
        return current_year - date.year

    @staticmethod
    def convert_height(height):
        """Return height written in centimeters to feet.

        Description
        -----------

        193 centimeters becomes 6.3 (6'3")
        """
        return round(height / 30.48, 1)

    @prepare_values
    def to_file(self, file_type='csv'):
        """Use this definition directly to write
        the players to a given file.

        This definition calls directly the .etc function that
        retrieves the players on the team.
        """
        pass
    
    # @connect_to_database
    def to_database(self, database, **kwargs):
        """Write the values to a database of choice. The default
        database is SQLite.
        """
        if 'using' in kwargs:
            if kwargs['using'] == 'postgres':
                try:
                    import psycopg2
                except ImportError:
                    pass

                return psycopg2.connect

            else:
                import sqlite3
                return sqlite3.connect

class PlayerPage(Requestor, Mixin):
    links = []

    def from_json(self, path):
        import json

        json_file = json.load(self._opener(path)[0])

        for player in json_file['players']:            
            update_values = self.player_page(player['player_page'])
            player.update(update_values)
        
    def from_csv(self):
        pass

    def from_text(self):
        pass

    def _opener(self, path):
        opened_file = open(path, 'r', encoding='utf-8')
        return opened_file, opened_file.close

    def player_page(self, link):
        soup = self.create_request(link)

        # Construct image URL ...
        # section#playerDetails > img
        image_url = self.image_url(soup)

        # ... > ul.line-list > span.role + strong
        position = soup.find('section', id='playerCareer').find('ul') \
                        .findChild('li').find('strong').getText()
        
        update_values = [image_url, self.clean_text(position)]

        return update_values

    def from_file(self, file_type='csv', **kwargs):
        import csv
        import json

        if file_type == 'csv' and 'column' not in kwargs:
            # You have to indicate the column to use
            # in order to get the links to create the
            # different requests
            pass
        
        with open('', 'r', encoding='utf-8') as f:
            links = []
            opened_file = None

            if file_type == 'csv':
                opened_file = csv.reader(f)
                # Take out the headers
                opened_file.pop(0)

                for player in opened_file:
                    links.append(player[kwargs['column']])

            elif file_type == 'json':
                opened_file = json.load(f)

                for player in opened_file['players']:
                    links.append(player['player_page'])

            else:
                # Treat the file as a .txt
                # file that we can use
                opened_file = f.readlines()

            for link in links:
                soup = self.create_request(link)

                # Construct image URL ...
                # section#playerDetails > img
                image_url = self.image_url(soup)

                # ... > ul.line-list > span.role + strong
                position = soup.find('section', id='playerCareer').find('ul') \
                                .findChild('li').find('strong').getText()
                
                update_values = [image_url, self.clean_text(position)]

                print(update_values)

    def image_url(self, soup, height=1200, width=800):
        """Takes the existing image url present on the player's
        page and reconstructs it in order to generate a bigger one.

        Size is `1200 x 800` by default. 
        """
        # section#playerDetails > img
        image = soup.find('section', id='playerDetails').find('img')
        splitted_url = splitquery(image['src'])

        # Parse number & type in query
        number = re.search(r'No\=(\d+)', splitted_url[1]).group(1)
        action_type = re.search(r'type\=(\w+)(?=\&)', splitted_url[1]).group(1)
        
        # Create new query
        new_query = {
            'No': number,
            'type': action_type,
            'height': '1200',
            'width': '800'
        }
        params = urlencode(new_query)
        return splitted_url[0] + '?' + params

    # def transform_position(self, position):
    #     """Transform position from string to number. For instance,
    #     `middle blocker` becomes `3`.
    #     """
    #     positions = {
    #         'Middle blocker': 3,
    #         'Setter': 1,
    #         'Outside Hitter': 2,
    #         'Middle Blocker': 3,
    #         'Universal': 4,
    #         'Libero': 6
    #     }

    #     try:
    #         position_number = positions[position]
    #     except KeyError:
    #         pass
    #     return position_number
