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
import sys
import threading
import time
from collections import deque, namedtuple
from urllib.parse import splitquery, unquote, urlencode, urljoin, urlparse

import requests

from scrappers.apps.config.http.managers import RequestsManager


def prepare_values(func):
    """A decorator that takes a list of values and writes
    them to a file of your choice"""
    def write(self, file_name, fieldnames:list=None):
        with open(file_name, 'w',  newline='', encoding='utf-8') as f:
            values = func(self)

            csv_writer = csv.DictWriter(f, values[0])
            csv_writer.writeheader()

            for player in values[1]:
                csv_writer.writerow(player)
        return True
    return write

class Mixins:
    base_url = None

    @classmethod
    def as_class(cls, url, **kwargs):
        """Recreates the class"""
        parsed_url = urlparse(url)
        klass = cls()
        klass.base_url = f'{parsed_url[0]}://{parsed_url[1]}'
        return klass

    @staticmethod
    def clean_text(text):
        return text.strip()

class Player(dict):
    """A wrapper that represents a player"""
    def __init__(self, name, link, date_of_birth,
                        height, weight, spike, block, **kwargs):
        if 'adjust_to_year' in kwargs:
            adjust_to_year = kwargs.pop('adjust_to_year')

        self.player = {
            'name': name,
            'link': link,
            'date_of_birth': date_of_birth,
            'age': self.get_age(date_of_birth),
            'height': height,
            'weight': weight,
            'spike': spike,
            'block': block
        }
        self.update({**self.player, **kwargs})

    def __str__(self):
        return str(self.player)

    def __getitem__(self, key):
        try:
            return self.player[key]
        except KeyError:
            return {'error': {'title': 'Key error', 'message': ''}}

    def sanitize_values(self):
        """Clean the values"""
        return {key: value.strip() for key, value in self.player.items()}

    @staticmethod
    def get_age(date_of_birth, adjust_to_year:int=None):
        """Takes the date of birth of a player and calculates
        his age

        Parameters
        ----------

            date_of_birth: date of birth of the player such as 1/1/1987

            adjusted: adjust the age relative to the year when the competition was played
        """
        current_year = datetime.datetime.now().year
        date = datetime.datetime.strptime(date_of_birth, '%d/%m/%Y')
        return adjust_to_year - date.year if adjust_to_year else current_year - date.year

    @staticmethod
    def convert_height(height:int):
        """Convert a player's height from centimeters to feet"""
        return round(height / 30.48, 1)

class ParticipatingTeamsPage(RequestsManager):
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
    errors = []

    def __init__(self):
        self.mixins = Mixins.as_class(url)

    def get_teams(self, url, section, attrs:dict):
    # def get_teams(self, url, section, attrs:dict):
        """
        Parameters
        ----------

            section_to_parse: is a dict containing the attributes
            of the section to parse e.g. {class: section_to_parse}
        """

        if not url.endswith('/teams'):
            self.errors.append({'error': {'title': 'Incorrect url', 'message': ''}})
            sys.exit(0)

        soup = self.beautify_single(url)
        
        # section#pools
        section = soup.find(section, attrs=attrs)

        if not section:
            self.errors.append({'error': {'title': '', 'message': ''}})
            sys.exit(0)
        
        # <a></a>
        unparsed_links = section.find_all('a')

        # TODO: If we send relative path to requests,
        # there could be an issue
        parsed_links = self.parse_links(unparsed_links)

        return parsed_links

    # def __repr__(self):
    #     return f'{self.__class__.__name__}(n={len(self.team_roster_urls)})'

    def __unicode__(self):
        return self.__str__()

    # def __str__(self):
    #     return str(self.team_roster_urls)

    # def __enter__(self):
    #     return self.team_roster_urls

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
                href = urljoin(self.mixins.base_url, link['href'] + '/team_roster')
            country = self.mixins.clean_text(link.find('figcaption').text)
            parsed_links.append((href, country))
        return parsed_links

class IndividualTeamPage(ParticipatingTeamsPage):
    # def __call__(self, url):
    #     return self.page(url)

    def __init__(self, url, section, attrs, limit:int=0):
        """Parse a specific volleyball team's page. By doing so,
        we are trying to gather all the statistics of the players.
        """
        super().__init__()

        print('-'*15)

        if limit != 0:
            limit_value = limit
        else:
            limit_value = 0

        team_roster_urls = self.get_teams(url, section, attrs)

        url_errors = html_pages = []

        # Iterator that requests the page
        # for each individual team
        for i, team_roster_url in enumerate(team_roster_urls):
            # .../en/teams/.../team_roster
            current_date = datetime.datetime.now()

            print('GET HTTP/1.1', str(current_date), team_roster_url[0])

            html_page = self.beautify_single(team_roster_url)

            if not html_page.is_empty_element:
                # section#roster
                html_page = html_page.find('section', attrs={'id': 'roster'})
                html_pages.append(html_page)

                if limit_value != 0:
                    if i == limit_value:
                        break
            else:
                url_errors.append(team_roster_url)
                self.errors.append({'error': {'title': 'Request errors', 'message': url_errors}})

        players = []

        # Iterator that iterates over the
        # HTML objects that we received
        for html_page in html_pages:
            # <tr>...</tr>
            rows = html_page.find_all('tr')

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
                            height, weight, spike, block)

                # Append player object to an
                # array that will then be passed to
                # the WriteCSV class
                players.append(player)
                
        # Although we are not calculating the age directly here,
        # we have to include it in the header in order to prevent errors
        self.header = ['name', 'link', 'date_of_birth', 'age',
                            'height', 'weight', 'spike', 'block']
        self.players = players

    @prepare_values
    def to_file(self):
        return self.header, self.players

class IndividualPlayerPage(RequestsManager, Mixins):
    """Parse a player's profile page. Use this class to add
    extra information on an existing player profile.
    """
    def __init__(self, url, limit:int=0):
        self.soup = self.beautify_single(url)

        # Construct image URL ...
        # section#playerDetails > img
        image_url = self.image_url()

        # ... > ul.line-list > span.role + strong
        position = self.soup.find('section', id='playerCareer').find('ul') \
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
            'height': height,
            'width': width
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

url = 'http://japan2018.fivb.com/en/competition/teams'
i = IndividualTeamPage(url, 'ul', {'class': 'team-list'}, limit=0)
i.to_file('japan_2018.csv', [])

# if __name__ == "__main__":
#     args = argparse.ArgumentParser(description='Get players from the FIVB website')
#     args.add_argument('-s', '--scrapper')
#     args.add_argument('-u', '--url')
#     parsed_args = args.parse_args()

#     if parsed_args.url:
#         page = IndividualTeamPage(parsed_args.url, 'ul', {'class': 'team-list'}, limit=0)
#         page.to_file('japan_2018.csv')

