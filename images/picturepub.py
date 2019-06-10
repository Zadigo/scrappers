from bs4 import BeautifulSoup
import re
from urllib import parse
import os
import datetime
import requests
from pathlib import Path

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def prepare_values(func):
    """Prepare a set of values for writting
    in a CSV, TXT or JSON files
    """
    def _prepare(self, celebrity=None):
        current_date = datetime.datetime.now()
        values = func(self)
        wrapper = [
            [f'{current_date}', f'{celebrity}']
        ]
        wrapper.append(values)
        with open(os.path.join(BASE_PATH, 'test.txt'), 'w', encoding='utf-8') as f:
            f.writelines(wrapper[0])
            f.writelines('\n')
            for value in wrapper[1]:
                f.writelines(value)
                f.writelines('\n')
        return wrapper
    return _prepare

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

class Parser:
    html = HTMLTemplate()
    def __init__(self, tag=None, attrs=None):
        message = self.html.soup.find('div', class_='messageInfo')
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
    def _save(self):
        """Output values to a file
        """
        return self.image_urls

# print(GetImages()._save())

class Requestor:
    def __init__(self):
        path = Path('C:\\Users\\Zadigo\\Pictures')
        response = requests.get('https://pixhost.to/show/268/107855908_picturepub-kimberley-garner-006.jpg', stream=True)
        with open(path, 'wb') as f:
            for block in response.iter_content(1024):
                if not response.ok:
                    print(response)

                if not block:
                    break
                f.write(block)

Requestor()


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
