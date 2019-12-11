import argparse
import datetime
import re
from collections import OrderedDict, deque
from hashlib import sha256
from itertools import takewhile
from timeit import default_timer as timer
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from requests import Request, Session

from scrappers.scrappers.config.utilities import user_agent


class UrlField:
    """A validator class that validates the url in respect the base
    page that needs to be parsed
    """
    def __init__(self, url, validate_against:list):
        self.url = url
        self.country = None
        self.team = None

    def __setattr__(self, name, value):
        splitted_url = urlsplit(value)

        return super().__setattr__(name, value)

    def __str__(self):
        return self.url

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return '%s(url="%s")' % (self.__class__.__name__, self.url)

class FivbUrlField(UrlField):
    pass



        

class Base(type):
    def __new__(cls, name, bases, clsdict):
        if name != 'Volleyball':
            # Create the stack and include it in the
            # dictionnary of each created class
            urls = players = teams = deque
            clsdict.update({'urls': urls, 'players': players, 'teams': teams})
        return super().__new__(cls, name, bases, clsdict)

class Volleyball(metaclass=Base):
    # A manager for sending requests to
    # the internet and returning an html
    # object that can be parsed
    request_manager = RequestsManager()
    # A manager for writting data
    # to a given CSV file
    writer = WriteFile()

    def __init__(self, urls, filename=None, history=False):
        self.soups = self.request_manager.beautify(urls)

class TeamsPage(Volleyball):
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
        
    def parse(self, filename=None):
        """Parse a team's page by retriving all the urls on the
        page in order to be able to get the players
        """
        for soup in self.soups:
            # section#pools
            section = soup.find('section', id='pools')

            # <a></a>
            # ..
            # [<a></a>, ...]
            unparsed_links = section.find_all('a')

            parsed_links = None


class TeamPage(TeamsPage):
    def players(self, filename=None):
        super().parse(filename=filename)

class PlayerPage(Volleyball):
    pass

# url = 'http://u20.women.2019.volleyball.fivb.com/en/teams'
# page = TeamsPage([url])
# page.parse()


s = RequestsManager()
s.beautify('http://u20.women.2019.volleyball.fivb.com/en/teams')
