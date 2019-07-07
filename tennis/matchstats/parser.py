import datetime
import json
import os
import time

import requests
from bs4 import BeautifulSoup

from scrappers.engine.user_agent import get_rand_agent


class MatchStats:
    def __init__(self, player):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.html')

        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            # a.btn-stats
            links = soup.find_all('a', attrs={'class': 'btn-stats'})

            stat_urls = []
            for link in links:
                stat_urls.append(link['href'])

        headers = {
            'User-Agent': get_rand_agent()
        }

        stats = []
        for stat_url in stat_urls:
            response = requests.get(stat_url, headers=headers)
            stats.append(response.json())
            # time.sleep(1)

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.json')

        refactored_stats = {
            'current_date': datetime.datetime.now().timestamp(),
            'player': player,
            'records': stats
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(refactored_stats, f, indent=4)
