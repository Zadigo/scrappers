import asyncio
import csv
import datetime
import json
import secrets
import sqlite3
from asyncio import Task
from timeit import default_timer as timer
from urllib.parse import urlparse
from collections import deque

from bs4 import BeautifulSoup
from requests import Request, Session

from scrappers.apps.config.http import user_agent
from scrappers.apps.config.http.utilities import UtilitiesMixin
from scrappers.apps.config.messages import Error, Info


class WriteFile:
    """A simple manager for writing data to files on the local
    storage of the computer or on AWS
    """
    aws_manager = None

    @staticmethod
    def auto_generate_name():
        current_date = datetime.datetime.timestamp()
        token = secrets.token_hex(nbytes=15)
        return ''.join([current_date, '_', token, '.csv'])        

    def to_csv(self, data, filename=None):
        if not filename:
            filename = self.auto_generate_name()

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            csv_file = csv.writer(f)
            csv_file.writerows(data)
    
    def to_json(self, data, filename=None):
        if not filename:
            filename = self.auto_generate_name()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    # def to_database(self, table_name, headers:list, db_name=None, **kwargs):
    #     create = f'CREATE {table_name} WITH {",".join(headers)}'
    #     insert = f'INSERT INTO {table_name} VALUES({",".join([])})'

    #     try:
    #         database = sqlite3.connect(db_name, timeout=4)
    #     except sqlite3.DatabaseError:
    #         return False

    #     with database as db:
    #         cursor = db.cursor()
    #         # If the table does not exist, then we need
    #         # to create it in the database
    #         cursor.execute(create)
    #         cursor.execute(insert)
    #         db.commit()

    def image(self, filename=None):
        pass

class RequestsManager(UtilitiesMixin):
    """Base manager used to send requests to the internet
    """
    session = Session()
    request_errors = []

    def __init__(self):
        # A dictionnary that stores links
        # after request error was received
        # self.request_errors = []
        pass

    def __call__(self, url):
        pass

    @classmethod
    def get(cls, *urls, **kwargs):
        """Sends a prepared request to the internet
        """
        responses = deque()
        with cls.session as new_session:
            for url in urls:
                start = timer()

                # *urls is a tuple of lists e.g. ([url]).
                # In order to get the url, we need to get
                # the first index of the list
                if isinstance(url, (tuple, list)):
                    url = url[0]

                response = new_session.send(cls.prepare(cls, url, **kwargs))
                end = timer()

                if response.status_code != 200:
                    cls.update(cls, url)
                else:
                    elapsed_time = end - start
                    print(Info("Request successful for %s in %ss" % (url, round(elapsed_time, 2))))
                    # return response.text
                    # return response.json()
                    responses.append(response)
        return responses

    def get_as_json(self, *urls):
        """Returns JSON data instead of the response object"""
        return {data for data in self.get(*urls)}

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

    def beautify(self, *urls):
        """Returns BeautifulSoup objects
        """
        yield BeautifulSoup(self.get(urls), 'html.parser')

    def beautify_single(self, url):
        """Returns a BeautifulSoup object
        """
        responses = self.get(url)
        if len(responses) > 0:
            return BeautifulSoup(responses[0].text, 'html.parser')
