import csv
import datetime
import json
import os
import re
import secrets
from collections import namedtuple
from urllib import parse

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

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
    celebrity = namedtuple('Celibrity', ['name'])
    # ('', '/path/')
    parsed_url = parse.urlparse(url)
    unparsed_celebrity_name = re.search(pattern, parsed_url[2])
    if unparsed_celebrity_name:
        celebrity_name = unparsed_celebrity_name.group(1).split('-')
        for i in range(len(celebrity_name)):
            celebrity_name[i] = celebrity_name[i].lower().capitalize()
    else:
        return 'Anonymous'
    return celebrity(' '.join(celebrity_name).strip())


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