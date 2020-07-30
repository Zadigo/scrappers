import time
import requests
import random
from io import StringIO
from urllib import parse


# XSS

PATH = 'C:\\Users\\Pende\\Documents\\myapps\\scrappers\\requests.html'

PATHS = [
    '<>',
    '<a onmouseover="alert(1)" href="#">read this!</a>'
]

def encode_query(query, double_encode=False):
    if double_encode:
        return parse.quote(parse.quote(query, safe=''), safe='')
    return parse.quote(query, safe='')

def writer(func):
    def requester(url):
        stream = StringIO()
        stream.writelines(func(url))
        with open(PATH, 'w') as f:
            with stream as s:
                f.writelines(s.getvalue())
    return requester

@writer
def send_request(url, double_encode=False):
    # quoted_path = parse.quote(random.choice(PATHS))
    # quoted_path = double_encode_query(random.choice(PATH))
    # print(quoted_path)
    # constructed_url = parse.urljoin(url, quoted_path)
    response = requests.get(url)
    if response.status_code == 200:
        print('Sent to %s' % url)
    return response.text

# url = 'https://google-gruyere.appspot.com/640369502884033392325691596385426482673/../..'
# send_request(url)


import sqlite3

db = sqlite3.connect('test_db.sqlite')
cursor = db.cursor()
# sql = """CREATE TABLE users (id INTEGER, name TEXT, surname TEXT, password TEXT);"""
# sql = """
# INSERT INTO users (id, name, surname, password)
# VALUES('2', 'Kendall', 'Jenner', 'kendall');
# """
def select(name='Kendall'):
    sql = """
    SELECT * FROM users WHERE name='%s'
    """ % name
    print(sql.strip())
    try:
        return cursor.executescript(sql)
    except sqlite3.OperationalError as e:
        print(e.args)
        return []

# queryset = select(name="Eugenie'; SELECT * FROM users; --")

# queryset = cursor.execute(sql)
# print(list(queryset))
# # db.commit()
# db.close()

# print(list(queryset))


