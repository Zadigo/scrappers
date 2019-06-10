import pandas
import requests
import csv
import json

class Players(dict):
    def __init__(self):
        self.update(
            {
                "tournament": "Nations League",
                "records": []
            }
        )

    def append_record(self, player):
        self['records'].append(player)

    def __str__(self):
        return super().__str__()

url = 'https://raw.githubusercontent.com/Zadigo/open-data-party/master/volleyball/6_2019_56a988209e.csv'
response = requests.get(url)
values = list(response.iter_lines(chunk_size=1024))
values.pop(0)
players = Players()
for value in values:
    decoded_value = str(value, 'utf-8')
    name, url_profile, date_of_birth, \
        age, height, weight, spike, block = decoded_value.rsplit(',', 8)

    player_dict = {
        'name': name,
        'url_profile': url_profile,
        'date_of_birth': date_of_birth,
        'age': age,
        'height': height,
        'weight': weight,
        'spike': spike,
        'block': block
    }
    
    players.append_record(player_dict)
with open('C:\\Users\\Zadigo\\Documents\\Koding\\scrappers\\volleyball\\data\\6_2019_56a988209e.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, indent=4)
