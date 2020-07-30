import argparse
import random
import threading
from io import StringIO
from urllib import parse

import requests

IPS = [
    '173.82.78.187',
    '62.171.177.80',
]

PROXIES = {
    'http': random.choice(IPS)
}

RESPONSES = []

# PATHS = [
#     'dns-query',
#     'jmx-console',
#     'manager/html',
#     'administrator',
#     'joomla/administrator',
#     'cms/administrator',
#     'msd',
#     'mysqldumper',
#     'mysqldumper',
#     'mysql',
#     'sql',
#     'cgi-bin/php',
#     'cgi-bin/php5',
#     'phpmyadmin',
#     'phpMyAdmin',
#     'index.php',
#     'sqlite/main.php',
#     'SQLite/SQLiteManager-1.2.4/main.php',
#     'SQLiteManager-1.2.4/main.php',
#     'webdav',
#     'wp-login.php',
#     'wordpress/wp-login.php',
#     'wp/wp-login.php',
#     'blog/wp-login.php',
#     'manager/html',
#     'status?full=true',
#     'msd1.24stable',
#     'streaming/clients_live.php',
#     'system_api.php',
#     '?a=fetch&content=<php>die(@md5(HelloThinkCMF))</php>',
#     'solr/admin/info/system?wt=json',
#     'vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php',
#     'wp-includes/wlwmanifest.xml',
#     'cms/wp-includes/wlwmanifest.xml',
#     'dev/wp-includes/wlwmanifest.xml',
#     'backup/wp-includes/wlwmanifest.xml',
#     'old/wp-includes/wlwmanifest.xml',
#     'wordpress/wp-includes/wlwmanifest.xml',
#     'owa/auth/logon.aspx?url=https%3a%2f%2f1%2fecp%2f',
#     'TP/public/index.php',
#     'maximo/webclient/login/login.jsp?welcome=true',
#     'TP/public/index.php?s=captcha',
#     'TP/public/index.php?s=index/\x5Cthink\x5Capp/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1',
#     'index.php?s=/Index/\x5Cthink\x5Capp/invokefunction&function=call_user_func_array&vars[0]=md5&vars[1][]=HelloThinkPHP',
#     '?a=fetch&content=<php>die(@md5(HelloThinkCMF))</php>',
#     '?XDEBUG_SESSION_START=phpstorm'
# ]

PATHS = []

QUERIES = []

def writer(path, response=None):
    # stream = StringIO()
    # stream.mode = 'a'
    # stream.write('response.text')
    # with stream as s:
    #     print(s.readlines())
    with open('C:\\Users\\Pende\\Documents\\myapps\\scrappers\\requests.html', 'a', encoding='utf-8') as f:
        f.write(str(response.headers))
        f.write('\n')
    return True

def send_requests(url):
    def wrapper(path=None, query=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, proxies=PROXIES)
        except requests.exceptions.ProxyError:
            response = None
            print('PATH: %s - Proxy error on this path' % path)
        else:
            print('Réponse pour %s [%s]' % (url, response.status_code))

        if response:
            if response.status_code == 200:
                writer(query or path, response)
                RESPONSES.append((query or path, response))
            else:
                writer(query or path, response)
        else:
            RESPONSES.append((path, None))
    return wrapper

def main(url, from_paths=False):
    threads = []
    if from_paths:
        for path in PATHS:
            constructed_url = parse.urljoin(url, path)
            threads.append(threading.Thread(
                target=send_requests(constructed_url), args=[path])
            )
    else:
        for query in QUERIES:
            constructed_url = url + query
            threads.append(threading.Thread(target=send_requests(constructed_url), kwargs={'query': query}))

    for thread in threads:
        thread.start()
        if thread.is_alive():
            print('Requête envoyée pour %s @ %s' % (thread.name, url))
        else:
            print('Thread not started')
        thread.join()
    
    print('-'*20)
    print('LISTE DES RESPONSE')
    print('-'*20)
    print(RESPONSES)

if __name__ == "__main__":
    args = argparse.ArgumentParser(description='PHP Scanner')
    args.add_argument('-u', '--url', help='Website url', type=str)
    args.add_argument('-q', help='Query', required=False, type=str)
    args.add_argument('-qs', help='Queries', nargs='+', required=False, type=str)
    args.add_argument('-cli', help='Start scanning with CLI', required=False, type=bool)
    # args.add_argument('-sp', help='The path as a string', required=False, type=str)
    # args.add_argument('-lp', help='The query path', nargs='+', required=False, type=str)
    args.add_argument('-e', help='Whether to quote the query', required=False, type=bool)
    parsed_args = args.parse_args()

    url = parsed_args.url

    if parsed_args.qs:
        QUERIES += parsed_args.qs

    if parsed_args.q:
        query = None
        if parsed_args.q.startswith('?'):
            query = str(parsed_args.q).replace('?', '')
        QUERIES.append(f'?{query or parsed_args.q}')
    
    # if parsed_args.lp:
    #     PATHS += parsed_args.lp
    
    # if parsed_args.sp:
    #     params = parse.quote(str(parsed_args.sp))
    #     PATHS.append(f'?{parsed_args.q}={params}')

    if not url:
        raise requests.exceptions.URLRequired('No URL was provided.')
    if not url.startswith('http') \
            or not url.startswith('https'):
        raise requests.exceptions.MissingSchema('The url is not valid')

    print('PHP SCANNER')
    print('-'*20)
    main(url)

# %2e%2e%2f%2e%2e%2fvar%2e%2e%2f
# python -m test_php --url https://example.com -q file -sp ../../var
# python -m test_php --url https://ocarat.com/
