import csv
import datetime
import json
import os
import re
import secrets
from collections import namedtuple
from urllib import parse

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

environment = os.environ

HOME_DRIVE = '%s\\Users\\%s\\Documents' % (
    environment.get('HOMEDRIVE'),
    environment.get('USERNAME')
)

OUTPUT_DIR = 'WTA_Data'

# def file_opener(func):
#     def opener(values, path, mode='r'):
#         f = open(path, mode, encoding='utf-8')
#         func(values, f, indent=4)
#         return True
#     return opener

def writer(values, filename='', extension='txt'):
    """A utility that is used to output data to a file
    """
    def values_iterator():
        for value in values:
            return value + '\n'

    filename = filename + '.%s' % extension
    with open(filename, 'w') as f:
        if extension == 'txt':
            for value in values:
                f.writelines(value)
                f.writelines('\n')
        elif extension == 'csv':
            csv_file = csv.writer(f)
            csv_file.writerow(values_iterator())

def guess_celebrity(url, pattern):
    """Get the celebrity's name from the url,
    using a regex pattern
    """
    celebrity = namedtuple('Celibrity', ['name', 'name_with_dash'])
    # ('', '/path/')
    parsed_url = parse.urlparse(url)
    unparsed_celebrity_name = re.search(pattern, parsed_url[2])
    if unparsed_celebrity_name:
        celebrity_name = unparsed_celebrity_name.group(0).split('-')
        for i in range(len(celebrity_name)):
            celebrity_name[i] = celebrity_name[i].lower()
    else:
        return 'Anonymous'

    normal = ' '.join(celebrity_name).strip().capitalize()
    dash = '-'.join(celebrity_name).strip()

    return celebrity(normal, dash)


def prepare_values(func):
    """A decorator for a class function that prepares 
    a set of values for writting in a CSV, TXT or JSON file

    Example
    -------

        class Test:
            @prepare_values
            def save(self):
                return values
    """
    def prepare(self, celebrity=None):
        current_date = datetime.datetime.now()
        # Get values
        values = func(self)
        # Header [date, celibrity name]
        values_wrapper = [
            [f'{current_date}', f'{celebrity}']
        ]
        # [[date, celibrity name], values]
        values_wrapper.append(values)

        with open(os.path.join(BASE_PATH, 'test.txt'), 'w', encoding='utf-8') as f:
            # Write [date, celibrity name]
            f.writelines(values_wrapper[0])
            f.writelines('\n')
             
            # Write [[...], values]
            for value in values_wrapper[1]:
                f.writelines(value)
                f.writelines('\n')
        # NOTE: Return values. 
        # Not really necessary
        return values_wrapper
    return prepare

# @file_opener
# def write_to_json(path):
#     # json.dump(refactored_stats, f, indent=4)
#     return json.dumps
# write_to_json

def check_path(folder_or_file):
    """Checks if the path exists and creates the required files.
    
    The `folder_or_file` parameter should be a folder or file name that
    is checked in the HOMEDRIVE user path.
    """
    path = os.path.join(HOME_DRIVE, folder_or_file)
    path_exists = os.path.exists(path)
    if not path_exists:
        user_input = input('The path (%s) does not exist. '
                                'Do you wish to create it? (Y/N) ' % folder_or_file)

        if user_input == 'Y':
            # Create
            os.makedirs(path)
            print('Created!')
            return path
        elif user_input == 'N':
            quit
        else:
            quit
    else:
        return path

def new_filename(name):
    """Create a new file name: `name_2019_05_AVSOIV`
    """    
    current_date = datetime.datetime.now()
    token = secrets.token_hex(3)
    return f'{name.lower()}_{current_date.year}_{current_date.month}_{token}.json'


# class EnrichPlayer:
#     """
#     """
#     def __init__(self, player_name):
#         try:
#             from googlesearch import search, search_images
#         except ImportError:
#             raise

#         # response = search(player_name, stop=5, pause=2)
#         response = search_images(player_name, stop=5, pause=2, extra_params={'biw':1024,'bih':768})
#         print(list(response))

def number_to_position(func):
    def convert(self, position):
        if not isinstance(position, int):
            raise TypeError
        
        positions = ['S', 'OH', 'MB']

        s=()

        if position == 1:
            s[0] == position
            s[1] == positions[0]
        return s
    return convert

class A:
    @number_to_position
    def position(self):
        pass
