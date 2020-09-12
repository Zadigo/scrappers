"""This module regroups a series of classes used by scrappers
in order to send requests to the web or dowload data or images.
"""

import functools
import os
import re
import threading
import timeit
from collections import deque
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests import Request, Session

from scrappers.apps.config.http import user_agent
from scrappers.apps.config.logs import default
from scrappers.apps.config.messages import Info


class Stack:
    def __init__(self):
        self.stack = {'errors': []}

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return str(self.stack)

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


class RequestsManager:
    session = Session()
    stack = Stack()
    is_image = False
    proxies = {}

    def __setattr__(self, name, value):
        if name == 'proxies':
            if not isinstance(value, dict):
                raise TypeError(f"'proxies' should be of type dict. Got {type(self.proxies)}")
        super().__setattr__(name, value)
    
    @classmethod
    def prepare(cls, urls:list, **headers):
        """A definition that prepares a list of urls to be
        sent to the web.

        Result
        ------

            [ prepared_request, ... ]
        """
        base_headers = {
            'User-Agent': user_agent.get_rand_agent()
        }
        if headers:
            base_headers = {**base_headers, **headers}

        for url in urls:
            # If by any means the url is a tuple
            # or a list, then try to get the first
            # item -- this is useful because when
            # passing the *urls args, sometimes, the
            # we get ((..., ...)) instead of (..., ...) 
            # and which can break the application
            if isinstance(url, (tuple, list)):
                first_value = 0
                url = url[first_value]
                first_value = first_value + 1
            
            request = Request(method='GET', url=url, headers=base_headers)
            prepared_request = cls.session.prepare_request(request)
            yield prepared_request

    def threaded_get(self, *urls, **headers):
        responses = []

        logger = default(self.__class__.__name__)

        def wrapper(new_session, request, responses:list, proxies:dict):
            try:
                response = new_session.send(
                    request, 
                    stream=True, 
                    proxies=proxies, 
                    timeout=5
                )
            except Exception as e:
                logger.error(e)
                self.stack.append(e.args)
            else:
                if response.status_code == 200:
                    responses.append(response)
                    logger.warning('Sent request for')
                else:
                    pass

        threads = []

        with self.session as new_session:
            prepared_requests = self.prepare(list(urls))
            for prepared_request in prepared_requests:
                params = {
                    'new_session': new_session,
                    'request': prepared_request,
                    'responses': responses,
                    'proxies': self.proxies
                }
                threads.append(threading.Thread(target=wrapper, kwargs=params))

        for thread in threads:
            thread.start()
            if thread.is_alive():
                thread.join()
        return responses
        
    def get(self, *urls, **headers):
        """Get a complete response for a given url
        """
        with self.session as new_session:
            prepared_requests = self.prepare(list(urls))
            for prepared_request in prepared_requests:
                # start = timeit.Timer()
                other_params = {}
                if self.proxies:
                    other_params.update({'proxies': self.proxies})
                response = new_session.send(prepared_request, stream=True, **other_params)
                # end = timeit.Timer()

                if response.status_code != 200:
                    self.stack.append(prepared_request.url)
                else:
                    # elapsed_time = end - start
                    elapsed_time = 0
                    print(Info("Request successful for %s in %s" % (prepared_request.url, elapsed_time)))
                    responses = yield response

        return responses

    def get_html(self, *urls, **headers):
        """Same as get() but returns a BeautifulSoup object of the page
        """
        # responses = list(self.get(*urls, **headers))
        responses = list(self.threaded_get(*urls, **headers))

        if len(responses) == 1:
            return BeautifulSoup(responses[0], 'html.parser')
        else:
            for response in responses:
                yield BeautifulSoup(response.text, 'html.parser')

    def lazy_request(self, path):
        if os.path.exists(path):
            if path.endswith('.html'):
                with open(path, 'r') as html:
                    return BeautifulSoup(html, 'html.parser')
            else:
                TypeError(f'File should be of type HTML but got ""')
        else:
            FileNotFoundError('The file you are trying to parse does not exist')
