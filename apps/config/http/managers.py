import csv
import datetime
import json
import secrets
import sqlite3
from timeit import default_timer as timer

from bs4 import BeautifulSoup
from requests import Request, Session

from scrappers.apps.config.http.utilities import UtilitiesMixin


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

    def to_database(self, table_name, headers:list, db_name=None, **kwargs):
        create = f'CREATE {table_name} WITH {",".join(headers)}'
        insert = f'INSERT INTO {table_name} VALUES({",".join([])})'

        try:
            database = sqlite3.connect(db_name, timeout=4)
        except sqlite3.DatabaseError:
            return False

        with database as db:
            cursor = db.cursor()
            # If the table does not exist, then we need
            # to create it in the database
            cursor.execute(create)
            cursor.execute(insert)
            db.commit()

    def image(self, filename=None):
        pass

class RequestsManager(UtilitiesMixin):
    """Base manager used to send requests to the internet
    """
    session = Session()

    def __init__(self):
        # A dictionnary that stores links
        # after a request error was received
        self.request_errors = []

    def __call__(self, url):
        pass

    @classmethod
    def get(cls, *urls, **kwargs):
        """Sends a prepared request to the internet
        """
        with cls.session as new_session:
            for url in urls:
                start = timer()
                response = new_session.send(cls.prepare(cls, url, **kwargs))
                end = timer()

                if response.status_code != 200:
                    cls.update(cls, url)
                    return response
                else:
                    elapsed_time = end - start
                    print(Info("Request successful for %s in %s" % (url, elapsed_time)))
                    return response.text

    def prepare(self, url, **kwargs):
        """This definition prepares a request to send to the web.
        This definition was structured so that the prepared request
        can be modified until the last moment.
        """
        headers = {
            'User-Agent': user_agent.get_rand_agent()
        }
        request = Request(method='GET', url=url, headers=headers)
        prepared_request = self.session.prepare_request(request)
        return prepared_request

    def beautify(self, *urls, **kwargs):
        """Returns BeautifulSoup objects
        """
        yield BeautifulSoup(self.get(urls), 'html.parser')

    def beautify_single(self, url, **kwargs):
        """Returns a BeautifulSoup object
        """
        # Transform the single url into a list
        # so that we can iterate over it
        return BeautifulSoup(self.get([url]), 'html.parser')

    def update(self, url, **kwargs):
        """Updates the request error stack
        """
        return self.request_errors.append((url, Error('The request with "%s" was not successful' % url)))
