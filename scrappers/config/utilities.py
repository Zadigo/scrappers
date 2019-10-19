import csv
import datetime
import json
import os
import re
import secrets
from collections import namedtuple
from urllib import parse
from requests import Session, Request, Response
from scrappers.scrappers.config.http._aws import TransferManager
from mimetypes import guess_type
from scrappers.scrappers.config.http import user_agent

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

def image_cache(func):
    """A simple cache decorator that saves the 
    images locally in order to prevent having
    get them back while running the application
    """
    def _cache(*args):
        cache = []
        for item in func():
            cache.append(item)
        return cache
    return _cache()

def writer(values, filename='', extension='txt'):
    """A utility used to output data to a file
    """
    filename = filename + '.%s' % extension
    with open(filename, 'w', newline='') as f:
        if extension == 'txt':
            for value in values:
                f.writelines(value)
                f.writelines('\n')
        elif extension == 'csv':
            csv_file = csv.writer(f)
            for value in values:
                csv_file.writerow(value)

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
    def prepare(self, celebrity=None, *headers):
        current_date = datetime.datetime.now()
        # Get values
        values = func(self)
        # Header [date, celibrity name]
        values_wrapper = [
            [f'{current_date}', f'{celebrity}']
        ]
        # values_wrapper = [
        #     [header for header in headers]
        # ]
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
    is checked in the `HOMEDRIVE` of the user.

    Output
    ------

        E:\\path\\to\\use
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
    """Create a new file name such as `name_2019_05_AVSOIV`
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

def position_to_number(func):
    """Decorator that transforms volleyball positions
    into numerical positions.

    Description
    -----------

    The usal positions on a volleyball court are:

        4    3    2
        -----------
        5    6    1

        Setter -> 1
        Outside Hitter -> 2
        Middle Blocker -> 3
        Universal -> 4
        Libero -> 6
    """
    def convert(self, position):
        if not isinstance(position, int):
            raise TypeError
        
        positions = ['Setter', 'Outside Hitter', 'Middle Blocker']

        if position == 'Universal':
            return 4
        
        if position in positions:
            return positions.index(position) + 1
                
        return None
    return convert

def create_request(url, data=False):
    """A reusable method to create requests

    Description
    -----------

    This definition was created in order to customize the
    headers and various different elements of the requests
    method
    """
    session = Session()

    headers = {
        'User-Agent': user_agent.get_rand_agent()
    }

    print('[REQUEST]: GET 1/1: %s' % url)

    request = Request('GET', url, headers)
    prepared_request = request.prepare()
    response = session.send(prepared_request)
    # return '[%s]' % response.status_code

    if data:
        return response.content
        
    return response

def prepare_for_s3(func):
    def read_and_transfer(self, manager=TransferManager, **kwargs):
        """Use this function to read an image from and url in order
        to upload it to an Amazon S3 bucket.

        Parameters
        ----------

        The `manager` parameter accepts a class that structures a logic
        that can be used to upload an image to a bucket of your choice.

        The default bucket is the AWS S3.

        The class should be structured such as an `upload` function could
        be used to upload the content:

            class YourClass:
                def __init__(self):
                    pass

                def upload(self):
                    pass

        The `kwargs` are any additional pieces of information
        (access key, secret key...) that can be used to successfully connect
        to your bucket or cloud. Note that generally, these services often require
        an access key and/or secret key and are checked by default.
        """

        @image_cache
        def images():
            return func(self)

        if not callable(manager) and not isinstance(manager, type):
            pass

        Klass_dict = manager.__dict__

        print(Klass_dict)

        if 'upload' in Klass_dict:
            try:
                access_key = kwargs['access_key']
                secret_key = kwargs['secret_key']
                region = kwargs['region']
                bucket = kwargs['bucket']
            except KeyError:
                pass
            else:
                # Create and instance of the class
                Klass = manager(access_key, secret_key, region, bucket)
        else:
            pass            

        for url in images:
            print('[IMAGE]: uploading - %s' % url)
            response = create_request(url)
            # image_content = response.iter_content(chunk_size=1024)

            try:
                name = re.match(r'(?:\/\d+\/\d+\/)((?:\w+\-?\w+\-?)+\.\w+)', url)
            except:
                pass
            else:
                contenttype = guess_type(name)

            Klass.upload(response.content, '/', contenttype[0])
        
        return True
    return read_and_transfer
