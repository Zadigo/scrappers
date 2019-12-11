"""This module regroups a series of classes used by scrappers
in order to send requests to the web or dowload data or images.
"""

import timeit
from collections import deque
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests import Request, Session

from scrappers.apps.config.http import user_agent
from scrappers.apps.config.messages import Info

# class Requestor:
#     """Base class to send requests to the web.

#     Parameters
#     ----------

#     `url` to use in order to send the request

#     `headers` to include in the request. `User-Agent` is generated
#     by default.
#     """
#     def create_request(self, url, **headers):
#         """Creates a request and returns the soup version
#         of the response. The returned object is the HTML
#         parse of the page.
#         """
#         base_headers = {
#             'User-Agent': user_agent.get_rand_agent()
#         }

#         if headers:
#             base_headers.update(headers)

#         # ENHANCEMENT: Test that the url follows the
#         # pattern /??/teams

#         # Get URL's different parts
#         # and construct the base url
#         splitted_url = urlparse(url)
#         self.base_url = f'{splitted_url[0]}://{splitted_url[1]}'

#         try:
#             response = requests.get(url, headers=base_headers)
#         except requests.HTTPError:
#             pass
#         else:
#             self.response = response
#             return self.create_soup(response)

#     def __repr__(self):
#         return '%s(%s)' % (
#             self.__class__.__name__,
#             self.response
#         )

#     @staticmethod
#     def create_soup(response):
#         return BeautifulSoup(response.text, 'html.parser')

# class DownloadImage:
#     """This class can download [an] images to the computer's
#     images path folder.

#     Parameters
#     ----------
    
#     The `url` should end with a .jpg/.jpeg/.png extension
#     """
#     # def __init__(self, url):
#     #     base_headers = {
#     #         'User-Agent': get_rand_agent()
#     #     }

#     #     if not url.endswith('jpg') or \
#     #         not url.endswith('jpeg') or \
#     #             not url.endswith('png'):
#     #         raise TypeError()

#     #     try:
#     #         response = requests.get(url, headers=base_headers)
#     #     except requests.HTTPError:
#     #         pass
        
#     #     # Path to output image
#     #     path = Path('C:\\Users\\Zadigo\\Pictures\\Test')
#     #     with open(path, 'wb') as f:
#     #         for block in response.iter_content(1024):
#     #             if not response.ok:
#     #                 print('[FAILED]', response)

#     #             if not block:
#     #                 break
#     #             f.write(block)

#     def _download_image(self, response):
#         # Path to output image
#         path = Path('C:\\Users\\Zadigo\\Pictures\\Test')
#         with open(path, 'wb') as f:
#             for block in response.iter_content(1024):
#                 if not response.ok:
#                     print('[FAILED]', response)

#                 if not block:
#                     break
#                 f.write(block)

#     def _send_request(self, url):
#         base_headers = {
#             'User-Agent': get_rand_agent()
#         }

#         if not url.endswith('jpg') or \
#             not url.endswith('jpeg') or \
#                 not url.endswith('png'):
#             raise TypeError()

#         try:
#             response = requests.get(url, headers=base_headers)
#         except requests.HTTPError:
#             pass

#         return response

#     def from_file(self, path):
#         with open(path, 'r', encoding='utf-8') as f:
#             urls = f.readlines()
#             for url in urls:
#                 self._download_image(self._send_request(url))

#     def from_url(self, url):
#         self._send_request(url)


class Stack:
    def __init__(self):
        self.stack = {'errors': []}

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return self.stack

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):
        return self.stack[index]

    def append(self, value):
        return self.stack['errors'].append(value)

    def delete(self, key):
        return self.stack[key].pop(self.stack[key][1:])

    def last(self, key):
        return self.stack[key][1:]

    def first(self, key):
        return self.stack[key][:1]

class Manager:
    response = None
    responses = []

    @property
    def content(self):
        return self.response.content

    def download_image(self, new_name=None):
        path = Path('C:\\Users\\Zadigo\\Pictures\\Test')

        with open(path, 'wb') as f:
            for block in self.response.iter_content(1024):
                if not self.response.ok:
                    print('[FAILED]', self.response)

                if not block:
                    break

                f.write(block)

    def download_images(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            urls = f.readlines()

    def to_aws(self):
        return
    
    @classmethod
    def as_handle(cls, response=None):
        instance = cls()
        instance.response = response
        return instance

class RequestsManager:
    session = Session()
    stack = Stack()
    is_image = False
    
    @classmethod
    def prepare(cls, *urls, **headers):
        base_headers = {
            'User-Agent': user_agent.get_rand_agent()
        }
        if headers:
            base_headers = {**base_headers, **headers}

        for url in urls:
            request = Request(method='GET', url=url, headers=base_headers)
            prepared_request = cls.session.prepare_request(request)
            yield prepared_request

    def get(self, *urls, **headers):
        """Get a complete response for a given url
        """
        with self.session as new_session:
            for prepared_request in self.prepare(urls):
                start = timeit.Timer()
                response = new_session.send(prepared_request)
                end = timeit.Timer()

                if response.status_code != 200:
                    self.stack.append(prepared_request.url)
                else:
                    elapsed_time = end - start
                    print(Info("Request successful for %s in %s" % (prepared_request.url, elapsed_time)))
                    responses = yield response

        setattr(self.manager, 'responses', responses)
        return responses

    def get_html(self, *urls, **headers):
        """Same as get() but returns a BeautifulSoup object of the page
        """
        responses = list(self.get(*urls, **headers))

        if list(responses) == 1:
            return BeautifulSoup(responses[0], 'html.parser')
        else:
            for response in responses:
                yield BeautifulSoup(response.text, 'html.parser')

    manager = Manager().as_handle()

r = RequestsManager()
s = r.get('http://www.example.com')
print(list(s))
