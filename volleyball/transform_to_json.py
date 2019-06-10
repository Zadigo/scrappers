import argparse
import csv
import json
import os

import pandas
import requests


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

class CreateJson:
    """
    `url` is the absolute url to the csv file to read.

    `filename` is the new file name to use.

    `klass` is the player class object that wraps the
    data to write in the JSON file.
    """
    def __init__(self, url, filename, klass=Players()):
        # Create request
        response = requests.get(url)

        # Read values
        values = list(response.iter_lines(chunk_size=1024))
        # Pop headers
        values.pop(0)

        # Instance of the player's
        # object in order to create
        # a given player
        # players = Players()
        # klass_dict = klass.__dict__
        # Check if `.append_record` is
        # present and call it
        # if 'append_record' in klass_dict:
        #     klass_dict['append_record']()

        for value in values:
            decoded_value = str(value, 'utf-8')
            name, url_profile, date_of_birth, \
                age, height, weight, spike, block = decoded_value.rsplit(',', 8)
            
            # Player data to append
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

            # Create players json object
            # e.g. { 'tournament': '...', 'records': [ {...} ] }
            klass.append_record(player_dict)

        # ENHANCEMENT: Do not raise error?
        if not filename.endswith('json'):
            raise NameError
        
        # Create path to write JSON file
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                    filename)

        # Now create the json file with the new object
        # 'C:\\Users\\Zadigo\\Documents\\Koding\\scrappers\\volleyball\\data\\6_2019_56a988209e.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(klass, f, indent=4)

CreateJson('https://raw.githubusercontent.com/Zadigo/open-data-party/master/volleyball/6_2019_56a988209e.csv','test.json')

# url = 'https://raw.githubusercontent.com/Zadigo/open-data-party/master/volleyball/6_2019_56a988209e.csv'
# response = requests.get(url)
# values = list(response.iter_lines(chunk_size=1024))
# values.pop(0)
# players = Players()
# for value in values:
#     decoded_value = str(value, 'utf-8')
#     name, url_profile, date_of_birth, \
#         age, height, weight, spike, block = decoded_value.rsplit(',', 8)

#     player_dict = {
#         'name': name,
#         'url_profile': url_profile,
#         'date_of_birth': date_of_birth,
#         'age': age,
#         'height': height,
#         'weight': weight,
#         'spike': spike,
#         'block': block
#     }
    
#     players.append_record(player_dict)


# with open('C:\\Users\\Zadigo\\Documents\\Koding\\scrappers\\volleyball\\data\\6_2019_56a988209e.json', 'w', encoding='utf-8') as f:
#     json.dump(players, f, indent=4)

# if __name__ == "__main__":
#     args = argparse.ArgumentParser(description='Create JSON player file')
#     args.add_argument('--url')
#     args.add_argument('--filename')
#     parsed_args = args.parse_args()

#     CreateJson(parsed_args.url, parsed_args.filename)
