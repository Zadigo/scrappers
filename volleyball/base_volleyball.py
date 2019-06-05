import argparse
import csv
import datetime
import secrets
import pickle
import os
import re
import threading
import time
from collections import deque, namedtuple
from urllib.parse import unquote, urlencode, urljoin, urlparse, splitquery

import requests
from bs4 import BeautifulSoup

from user_agent import get_rand_agent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')

URLS = {
    'players': 'http://%s.fivb.com/en/competition/teams/%s/players',
    'nations_league': 'https://www.volleyball.world/en/vnl/women/teams'
}

DATA_DIRS = {
    'player_csv': os.path.join(BASE_DIR, 'data')
}

# TODO: Erase countries -- unnecessary at this stage
# COUNTRIES = ['arg-argentina', 'aze-azerbaijan', 'bra-brazil',
#             'bul-bulgaria', 'cmr-cameroon', 'can-canada',
#             'chn-china', 'cub-cuba', 'dom-dominican%20republic',
#             'ger-germany', 'ita-italy', 'jpn-japan', 'kaz-kazakhstan',
#             'ken-kenya', 'kor-korea', 'mex-mexico',
#             'ned-netherlands', 'pur-puerto%20rico', 'rus-russia',
#             'srb-serbia', 'tha-thailand', 'tto-trinidad%20%20tobago',
#             'tur-turkey', 'usa-usa']

# ENHANCEMENT: Subclass a list instead
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

    def _write(self, player=None):
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
            csv_file = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
        """Create a request and return a list
        containing the response and it's BeautifulSoup
        object for further actions.
        """
        # Get URL's different parts
        # and construct the base url
        splitted_url = urlparse(url)
        self.base_url = f'{splitted_url[0]}://{splitted_url[1]}'

        try:
            response = requests.get(url, user_agent)
        except requests.HTTPError:
            raise
        else:
            if response.status_code == 200:
                return [response, self.create_soup(response)]
            return None

    @staticmethod
    def create_soup(response):
        return BeautifulSoup(response.text, 'html.parser')

    # def get_countries(self, path):
    #     """Return the countries with their paths
    #     present on a team's page.
    #     '/en/vnl/women/teams/dom-dominican%20republic'
    #     """
    #     relative_link = unquote(path)
    #     country = re.search(r'\w+\-(\w+\s?\w+)', relative_link)
    #     if country:
    #         return (country.group(1).capitalize(), path)
    #     return None

    def parse_links(self, links):
        parsed_links = []
        for link in links:
            parsed_links.append((link.href, link.text))
        return parsed_links

    def clean_text(self, text):
        return text.strip()

class TeamsPage(Requestor):
    def __init__(self, create_file=False):
        self.write_player = WriteCSV()

        # Create a new file to write to
        if create_file:
            self.write_player.create_new_file()

        response = self.create_request('https://www.volleyball.world/en/vnl/women/teams')
        soup = response[1]

        # section#pools
        section = soup.find('section', id='pools')
        
        # <a></a>
        unparsed_links = section.find_all('a')
        parsed_links = self.parse_links(unparsed_links)
        
        self.teams = parsed_links


    def parse_links(self, links, relative=False):
        """Parse the links on the teams page.
        Returns a `list` such as [(link, country), ...]
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
        print('-'*15)
        responses = []
        for team in self.get_teams:
            team_roster_url = urljoin(team[0], 'team_roster')
            current_date = datetime.datetime.now()
            print('GET HTTP/1.1', str(current_date), team_roster_url)
            response = self.create_request(team_roster_url)

            # section#roster
            response[1] = response[1].find('section', id='roster')
            responses.append(response)

        # [(response, sections#roster), ...]
        for response in responses:
            # <tr>...</tr>
            rows = response[1].find_all('tr')

            # Pop <tr><th>...</th></tr>
            rows.pop(0)

            # <td>...</td>
            for row in rows:
                items = row.find_all('td')
                
                # Eugénie Constanza
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

                self.write_player._write(player=player)

        self.write_player._write

    @staticmethod
    def get_age(date_of_birth):
        current_year = datetime.datetime.now().year
        date = datetime.datetime.strptime(date_of_birth, '%d/%m/%Y')
        return current_year - date.year

    @staticmethod
    def convert_height(height):
        pass

class PlayerPage(Requestor):
    def __init__(self, url):
        response = self.create_request('https://www.volleyball.world/en/vnl/women/teams/ita-italy/players/cristina-chirichella?id=71297')
        soup = response[1]

        # .. IMAGE

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
        new_link = splitted_url[0] + '?' + params

        # .. POSITION

        # ... > ul.line-list > span.role + strong
        position = soup.find('section', id='playerCareer').find('ul')\
                    .findChild('li').find('strong').getText()
        
        update_values = [new_link, self.clean_text(position)]
        print(update_values)

# if __name__ == "__main__":
#     args = argparse.ArgumentParser(description='Volleyball page parser')
#     # args.add_argument('-o', '--output')
#     # args.add_argument('-f', '--filename')
#     # args.add_argument('-g', '--gethtml')
#     args.add_argument('method', help='Call teams_page, player_page or team_page')
#     parsed_args = args.parse_args()
# # 
#     if parsed_args.method == 'team_page':
#         url = input('Enter the FiVB volleyball team page: ')
#         print(url)
#         # TeamPage(create_file=True).get_team_page()
    
# first_thread = threading.Thread(target=Requestor.create_request, args=(Requestor, 'https://www.volleyball.world/en/vnl/women/teams'))
# second_thread = threading.Thread(target=TeamPage.__init__, args=(TeamPage,))
# first_thread.start()
# second_thread.start()
