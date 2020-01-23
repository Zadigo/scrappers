import datetime
import json
import os
import time
import re

import requests
from bs4 import BeautifulSoup

from scrappers.apps.config.http.managers import RequestsManager
from scrappers.apps.config.http.user_agent import get_rand_agent


class MatchStats(RequestsManager):
    """A scrapper that analyses a Matchstats player page and finds
    all the JSON items in order to grab the statistics of a player.
    """
    def statistics(self, player, check_links=False):
        # e.g. eugenie_bouchard.json
        file_name = '%s_stats.json' % player.replace(' ', '_').lower()

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.html')

        stat_urls = []
        failed_urls = []
        # Opens the file to analyze the different
        # links and send the requests afterwards
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            # a.btn-stats
            links = soup.find_all('a', attrs={'class': 'btn-stats'})

            pattern = r'https?\:\/\/matchstat\.com\/tennis\/match\-stats\/w\/(\d+)'

            for link in links:
                href = link['href']
                # Only just append the urls in which
                # we are interested by matching the
                # above pattern -- this is done for
                # security purposes
                is_match = re.match(pattern, href)
                if is_match:
                    stat_urls.append(href)
                else:
                    failed_urls.append(link)

        responses = super().get(*stat_urls)

        stats = []
        for response in responses:
            stats.append(response.json())

        # stats = []
        # for stat_url in stat_urls:
        #     response = super().get(stat_url)
        #     stats.append(response.json)

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)

        # Refactor all stats that we
        # received to something that
        # would be more readable
        refactored_stats = {
            'current_date': datetime.datetime.now().timestamp(),
            'player': player,
            'records': stats
        }
        self.write_stats(output_path, refactored_stats)

    @staticmethod
    def write_stats(output_path, stats):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4)

stats = MatchStats()
# stats.statistics('Eugenie Bouchard')
item = stats.get_as_json('https://matchstat.com/tennis/match-stats/w/8782422')
print(item)
print(stats.request_errors)