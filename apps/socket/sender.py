#!/bin/bash

import configparser
import os
import socket
import sqlite3
import time
import threading
from argparse import ArgumentParser
from collections import OrderedDict
import datetime

DEBUG = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def sanitize(data):
    if isinstance(data, bytes):
        decoded_data = data.decode('utf-8')
    return decoded_data


def cached(func):
    return func()


def logger(**kwargs):
    def writer(name='log', filename=None, mode='w'):
        if not filename:
            try:
                filename = lazy_settings['default'][name]
            except:
                pass
            else:
                filename = os.path.join(BASE_DIR, filename)
        with open(filename, mode=mode, encoding='utf-8') as f:
            current_date = datetime.datetime.now().date()
            f.write(f'RCV: {current_date} -- ')
    return writer


def configuration(**kwargs):
    settings = OrderedDict()
    config_file = configparser.ConfigParser()
    config_file.read(os.path.join(BASE_DIR, 'settings.ini'), encoding='utf-8')

    default_options = config_file.options('default')
    for option in default_options:
        settings.update({option: config_file.get('default', option)})
    
    if config_file.has_section('database'):
        settings.update({'database': config_file['database']['name']})

    settings['logger'] = logger()

    # settings = settings.update(**kwargs)
    return settings

lazy_settings = configuration()


def database(func):
    try:
        db_path = os.path.join(BASE_DIR, lazy_settings.get('database'))
    except AttributeError:
        print(('Could not find database from settings.'
        ' Using default database name.'))
        db_path = 'socket_db.sqlite'
    else:
        connection = sqlite3.connect(db_path)
        if connection:
            cursor = connection.cursor

            cursor().execute(
                """
                CREATE TABLE
                IF NOT EXISTS recvdata
                (data TEXT);
                """
            )
            connection.commit()
    
    def wrapper(port=None, **kwargs):
        func(db=connection, cursor=cursor)
        # thread = threading.Thread(target=func, 
        #             kwargs={'db': connection, 'cursor': cursor})
        # thread.start()
        # if thread.is_alive():
        #     return connection, cursor
        # return False
    return wrapper


@database
def sender(**kwargs):
    print('Starting IPAX 2000.')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if DEBUG:
        hostname = lazy_settings['host']
    else:
        hostname = socket.gethostname()
    
    s.bind((hostname, 65432))
    s.listen()
    # s.setblocking(False)

    conn, addr = s.accept()

    if 'db' not in kwargs \
            and 'cursor' not in kwargs:
        print('Sender started without a database backed.')

    db = kwargs['db']
    cursor = kwargs['cursor']
    logger = lazy_settings['logger']

    with conn as c:
        data = c.recv(1024)

        try:
            cursor().execute(
                f"""
                INSERT INTO recvdata (data)
                VALUES('{sanitize(data)}');
                """
            )
            db.commit()
        except sqlite3.OperationalError as e:
            # DO LOG
            print(e)
        else:
            db.commit()
            logger()

# if __name__ == "__main__":
#     parser = ArgumentParser(description='Wel to IPAX 2000')
#     parser.add_argument('-p', '--port', help='Port', type=int, required=False)
#     args = parser.parse_args()
#     sender()


