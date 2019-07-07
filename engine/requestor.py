import requests
from bs4 import BeautifulSoup
from pathlib import Path

from scrappers.engine.user_agent import get_rand_agent

class Requestor:
    def __init__(self, url, **headers):
        base_headers = {
            'User-Agent': get_rand_agent()
        }

        if headers:
            base_headers.update(headers)

        try:
            response = requests.get(url, headers=base_headers)
        except requests.HTTPError:
            pass
        else:
            if response.status_code == 200:
                self.response = response
                self.soup = BeautifulSoup(response.text, 'html.parser')

    def __repr__(self):
        return '%s(%s, %s)' % (
            self.__class__.__name__,
            self.response,
            'soup'
        )

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