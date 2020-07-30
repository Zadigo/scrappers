import datetime
import json
import queue
import secrets
import threading
from collections import deque
from timeit import default_timer as timer
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from requests import Request, Session

from scrappers.apps.config.http import user_agent
# from scrappers.apps.config.http.utilities import UtilitiesMixin
from scrappers.apps.config.messages import Error, Info


class RequestsManager:
    """Base manager used to send requests to the internet
    """
    session = Session()
    request_errors = []

    @classmethod
    def get(cls, urls:list, **kwargs):
        threads = []
        responses = []

        with cls.session as new_session:
            def new_session_wrapper(request):
                response = new_session.send(request)
                if response.status_code == 200:
                    # TODO: Apparently the deque()
                    # mutates. Maybe we need to create
                    # and instance in the method
                    responses.append(response)
                else:
                    cls.update(cls, url)

            for index, url in enumerate(urls):
                if isinstance(url, (tuple, list)):
                    url = url[0]
                    if not url.startswith('http'):
                        raise ValueError(f'Url should start with http or https. In the case where you are using a tuple, the url should be at position 0. Received: {url[0]}')
                thread = threading.Thread(
                    target=new_session_wrapper,
                    args=[cls.prepare(cls, url, **kwargs)]
                )
                threads.append(thread)

                if 'limit_to' in kwargs:
                    limit_to = kwargs['limit_to']
                    has_reached_limit = all([index == limit_to, limit_to > 0])
                    if has_reached_limit:
                        break

            if threads:
                for thread in threads:
                    thread.start()
                    if thread.is_alive():
                        print('GET HTTP/1.1', '--')
                thread.join()
        if len(urls) == 1:
            return responses[0]
        return responses

    def prepare(self, url, **headers):
        """This definition prepares a request to send to the web.
        This definition was structured so that the prepared request
        can be modified until the last moment.
        """
        base_headers = {
            'User-Agent': user_agent.get_rand_agent()
        }
        if headers:
            base_headers = {**base_headers, **headers}

        request = Request(method='GET', url=url, headers=headers)
        prepared_request = self.session.prepare_request(request)
        return prepared_request

    def update(self, url, **kwargs):
        """Updates the request error stack
        """
        return self.request_errors.append((url, Error('The request with "%s" was not successful' % url)))

    def beautify(self, urls:list, **kwargs):
        """Returns BeautifulSoup objects
        """
        soups = []
        responses = self.get(urls, **kwargs)
        for response in responses:
            soups.append(BeautifulSoup(response.text, 'html.parser'))
        return soups

    def beautify_single(self, url):
        """Returns a BeautifulSoup object
        """
        response = self.get([url])
        return BeautifulSoup(response.text, 'html.parser')
