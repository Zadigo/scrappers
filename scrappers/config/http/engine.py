"""This module regroups a series of classes used by scrappers
in order to send requests to the web or dowload data or images.
"""

from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from scrappers.scrappers.config.http import user_agent


class Requestor:
    """Base class to send requests to the web.

    Parameters
    ----------

    `url` to use in order to send the request

    `headers` to include in the request. `User-Agent` is generated
    by default.
    """
    def create_request(self, url, **headers):
        """Creates a request and returns the soup version
        of the response. The returned object is the HTML
        parse of the page.
        """
        base_headers = {
            'User-Agent': user_agent.get_rand_agent()
        }

        if headers:
            base_headers.update(headers)

        # ENHANCEMENT: Test that the url follows the
        # pattern /??/teams

        # Get URL's different parts
        # and construct the base url
        splitted_url = urlparse(url)
        self.base_url = f'{splitted_url[0]}://{splitted_url[1]}'

        try:
            response = requests.get(url, headers=base_headers)
        except requests.HTTPError:
            pass
        else:
            self.response = response
            return self.create_soup(response)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            self.response
        )

    @staticmethod
    def create_soup(response):
        return BeautifulSoup(response.text, 'html.parser')

class DownloadImage:
    """This class can download [an] images to the computer's
    images path folder.

    Parameters
    ----------
    
    The `url` should end with a .jpg/.jpeg/.png extension
    """
    # def __init__(self, url):
    #     base_headers = {
    #         'User-Agent': get_rand_agent()
    #     }

    #     if not url.endswith('jpg') or \
    #         not url.endswith('jpeg') or \
    #             not url.endswith('png'):
    #         raise TypeError()

    #     try:
    #         response = requests.get(url, headers=base_headers)
    #     except requests.HTTPError:
    #         pass
        
    #     # Path to output image
    #     path = Path('C:\\Users\\Zadigo\\Pictures\\Test')
    #     with open(path, 'wb') as f:
    #         for block in response.iter_content(1024):
    #             if not response.ok:
    #                 print('[FAILED]', response)

    #             if not block:
    #                 break
    #             f.write(block)

    def _download_image(self, response):
        # Path to output image
        path = Path('C:\\Users\\Zadigo\\Pictures\\Test')
        with open(path, 'wb') as f:
            for block in response.iter_content(1024):
                if not response.ok:
                    print('[FAILED]', response)

                if not block:
                    break
                f.write(block)

    def _send_request(self, url):
        base_headers = {
            'User-Agent': get_rand_agent()
        }

        if not url.endswith('jpg') or \
            not url.endswith('jpeg') or \
                not url.endswith('png'):
            raise TypeError()

        try:
            response = requests.get(url, headers=base_headers)
        except requests.HTTPError:
            pass

        return response

    def from_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            urls = f.readlines()
            for url in urls:
                self._download_image(self._send_request(url))

    def from_url(self, url):
        self._send_request(url)
