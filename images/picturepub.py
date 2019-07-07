import datetime
import os
import re
from collections import namedtuple
from pathlib import Path
from urllib import parse

import requests
from bs4 import BeautifulSoup

from scrappers.engine.utilities import prepare_values

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# def guess_celebrity(url):
#     celebrity = namedtuple('Celibrity', ['name'])
#     parsed_url = parse.urlparse(url)
#     unparsed_celebrity_name = re.search(r'\_?picturepub\-?([a-z\-]+)', parsed_url[2])
#     if unparsed_celebrity_name:
#         celebrity_name = unparsed_celebrity_name.group(1).split('-')
#         for i in range(len(celebrity_name)):
#             celebrity_name[i] = celebrity_name[i].lower().capitalize()
#     else:
#         return 'Anonymous'
#     return celebrity(' '.join(celebrity_name).strip())

# def prepare_values(func):
#     """A decorator that prepares a set of values for writting
#     in a CSV, TXT or JSON files
#     """
#     def prepare(self, celebrity=None):
#         current_date = datetime.datetime.now()
#         # Get values
#         values = func(self)
#         # Header [date, celibrity name]
#         values_wrapper = [
#             [f'{current_date}', f'{celebrity}']
#         ]
#         # [[date, celibrity name], values]
#         values_wrapper.append(values)

#         with open(os.path.join(BASE_PATH, 'test.txt'), 'w', encoding='utf-8') as f:
#             # Write [date, celibrity name]
#             f.writelines(values_wrapper[0])
#             f.writelines('\n')
            
#             # Write [[...], values]
#             for value in values_wrapper[1]:
#                 f.writelines(value)
#                 f.writelines('\n')
#         # NOTE: Return values. 
#         # Not really necessary
#         return values_wrapper
#     return prepare

class HTMLTemplate:
    """A class that holds the HTML file as an object
    in the class.
    """
    def __init__(self):
        # Basic path. Can be overriden
        # to indicate another file path
        # BUG: Cannot set self.path?
        self.path = os.path.join(BASE_PATH, 'html.html')

        # The opened HTML file. It is parsed
        # automatically. TODO: Check that the
        # file is a true HTML file.
        with open(self.path, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f, 'html.parser')

    @property
    def get_html_object(self):
        return self.soup

class PicturePub:
    html = HTMLTemplate()
    def __init__(self, tag=None, attrs=None):
        message = self.html.soup.find('div', attrs={'class': 'messageInfo'})
        links = message.find_all('a')
        image_urls = []
        for link in links:
            # Some links don't have a href
            # so protect the script from
            # breaking with a KeyError
            try:
                url = link['href']
                unparsed_url = parse.urlparse(url)
                if str(unparsed_url[2]).endswith('jpg') \
                    or str(unparsed_url[2]).endswith('jpeg'):
                    image_urls.append(url)
            except KeyError:
                pass
        self.image_urls = image_urls

class GetImages(Parser):
    @prepare_values
    def save(self):
        """Output values to a given file
        """
        return self.image_urls


class Requestor:
    def __init__(self, url=None):
        path = Path('C:\\Users\\Zadigo\\Pictures\\Test')
        response = requests.get('https://pixhost.to/show/268/107855908_picturepub-kimberley-garner-006.jpg', stream=True)
        with open(path, 'wb') as f:
            for block in response.iter_content(1024):
                if not response.ok:
                    print(response)

                if not block:
                    break
                f.write(block)

# Requestor()


# def cache_values(self):
#     def _cache(func):
#         values = self(func)
#         values.append('z')
#         return values
#     return _cache

# class X:
#     @cache_values
#     def save(self):
#         return ['a', 'c', 'e']

# print(X().save())
