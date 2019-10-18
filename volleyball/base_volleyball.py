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
from bs4 import BeautifulSoup

from volleyball.user_agent import get_rand_agent



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')

DATA_DIRS = {
    'player_csv': os.path.join(BASE_DIR, 'data')
}

# ENHANCEMENT: Subclass a list instead?
class Player(namedtuple('Player', ['name', 'link', 'date_of_birth',
                         'age', 'height', 'weight', 'spike', 'block'])):
    """Player class used to create a volleyball player
    """
    __slots__ = ()

class WriteCSV:
    """Use this class to write a CSV file containing
    the data obtained from the website.
    """
    current_file = None

    def _write(self, players=[]):
        """Write a volleyball player.
        """
        if self.current_file is None:
            self.current_file = self.create_new_file

            try:
                # Create file and/or
                # necessary directories
                os.makedirs(os.path.dirname(self.current_file))
            except FileExistsError:
                pass

        with open(self.current_file, mode='a', encoding='utf-8', newline='') as f:
            print('Writing players...')
            csv_file = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for player in players:
                csv_file.writerow(player)       

    @property
    def create_new_file(self):
        """Return a new CSV file path such as `month_year_token`.
        """
        current_date = datetime.datetime.now().date()
        token = secrets.token_hex(5)
        filename = f'{current_date.month}_{current_date.year}_{token}.csv'
        return os.path.join(DATA_DIR, filename)

class Requestor:
    def create_request(self, url, user_agent=get_rand_agent(), **kwargs):
        """Create a request and return a list containing the response 
        and it's BeautifulSoup object for further actions.

        Description
        -----------

            [
                response, BeautifulSoup()
            ]
        """
        # Get URL's different parts
        # and construct the base url
        splitted_url = urlparse(url)
        self.base_url = f'{splitted_url[0]}://{splitted_url[1]}'

        try:
            response = requests.get(url, user_agent)
        except requests.ConnectionError:
            raise
        else:
            if response.status_code == 200:
                return [response, self.create_soup(response)]
            return None

    @staticmethod
    def create_soup(response):
        """Create an return a BeautifulSoup object
        """
        return BeautifulSoup(response.text, 'html.parser')

    def parse_links(self, links):
        parsed_links = []
        for link in links:
            parsed_links.append((link.href, link.text))
        return parsed_links

    def clean_text(self, text):
        """Return a text stripped from the trailing and
        starting spaces
        """
        return text.strip()

class TeamsPage(Requestor, WriteCSV):
    """This analyzes the page referencing all the teams and parses the
    different countries present on that page with their urls.
    """
    def __init__(self, url=None, file_name=None):
        if file_name:
            self.current_file = file_name

        # ENHANCEMENT: Test that the url follows the
        # pattern /??/teams
        response = self.create_request(url)
        soup = response[1]

        # section#pools
        section = soup.find('section', id='pools')
        
        # <a></a>
        unparsed_links = section.find_all('a')

        # TODO: If we send relative path to requests,
        # there could be an issue
        parsed_links = self.parse_links(unparsed_links)
        
        self.teams = parsed_links

    def parse_links(self, links, relative=False):
        """Parse the links on the teams page and returns a 
        `list` such as [(link, country), ...].

        Description
        -----------

            [
                (url, country),
                (...)
            ]
        
        Parameters
        ----------

            If *relative* is true, the definition returns the path
            of the link instead of the full url
        """
        parsed_links = []

        # Delete the two first links
        links.pop(0)
        links.pop(0)

        for link in links:
            if relative:
                href = link['href']
            else:
                # Add a trailing slash so that python
                # appends additional paths instead of
                # cutting it off
                href = urljoin(self.base_url, link['href'] + '/')
            country = self.clean_text(link.find('figcaption').text)
            parsed_links.append((href, country))

        return parsed_links

    @property
    def get_teams(self):
        return self.teams

class TeamPage(TeamsPage):
    def get_team_page(self):
        """Parse a specific volleyball team's page. By doing so,
        we are trying to gather all the statistics of the players.
        """
        print('-'*15)
        responses = []
        # t = 0
        for team in self.get_teams:
            team_roster_url = urljoin(team[0], 'team_roster')
            current_date = datetime.datetime.now()
            print('GET HTTP/1.1', str(current_date), team_roster_url)
            response = self.create_request(team_roster_url)

            # section#roster
            response[1] = response[1].find('section', id='roster')
            responses.append(response)

            # if t == 2:
            #     break

            # t += 1

        players = []

        # [(response, sections#roster), ...]
        for response in responses:
            # <tr>...</tr>
            rows = response[1].find_all('tr')

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

                # Append player object to an
                # array that will then be passed to
                # the WriteCSV class
                players.append(player)

        # TODO: Delete
        self._write(players)

    @staticmethod
    def get_age(date_of_birth, adjusted=False):
        current_year = datetime.datetime.now().year
        date = datetime.datetime.strptime(date_of_birth, '%d/%m/%Y')
        return current_year - date.year

    @staticmethod
    def convert_height(height):
        pass

class PlayerPage(Requestor):
    """Parse a player's profile page. Use this class to add
    extra information on an existing player profile.
    """
    def __init__(self, url):
        response = self.create_request(url)
        self.soup = soup = response[1]

        # Construct image URL ...
        # section#playerDetails > img
        image_url = self.image_url()

        # ... > ul.line-list > span.role + strong
        position = soup.find('section', id='playerCareer').find('ul') \
                        .findChild('li').find('strong').getText()
        
        update_values = [image_url, self.clean_text(position)]

        print(update_values)

    def image_url(self, height=1200, width=800):
        """Takes the existing image url present on the player's
        page and reconstructs it in order to generate a bigger one.

        Size is `1200 x 800` by default. 
        """
        # section#playerDetails > img
        image = self.soup.find('section', id='playerDetails').find('img')
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

    def transform_position(self, position):
        """Transform position from string to number.
        
        Description
        -----------

            For instance, *middle blocker* becomes *3*.
        """
        positions = {
            'Middle blocker': 3
        }

        try:
            position_number = positions[position]
        except KeyError:
            pass
        return position_number
