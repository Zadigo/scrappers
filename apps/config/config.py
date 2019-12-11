import configparser
import os
import re
import secrets
from hashlib import sha256

from scrappers.scrappers.config.config import AWS, TransferManager

environment = os.environ

class Configuration:
    """This is the base configuration class used to set the
    different configuration options for scrappers.

    This class should not be used directly unless you wish to
    overwrite some of its functionalities.

    Instead use its instance `configuration` in `scrappers.config.config`.
    """
    def __init__(self):
        # Base path of 
        # the file being called
        self.base_path = os.path.abspath(__file__)

        # User homedrive
        self.homedrive = '%s\\Users\\%s\\Documents' % (
            environment.get('HOMEDRIVE'),
            environment.get('USERNAME')
        )

        # Output paths
        self.output_paths = [
            {
                'default': {
                    'path': os.path.join(self.homedrive, 'scrapper_data')
                }
            }
        ]

        # Amazon S3
        self.bucket = TransferManager

    def __unicode__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return self.__unicode__()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setattr__(self, name, value):
        if name == 'output_paths':
            if not isinstance(value, list):
                raise TypeError()
                # if not isinstance(value, dict):
                #     print('The path should be a valid dictionnary')
                #     raise TypeError()

                # if not 'path' in value:
                #     print('Path was not found in dictionnary')
                #     raise KeyError()

        # if name == 'bucket':
        #     value = self.bucket_is_callable(value)

        return super().__setattr__(name, value)

    @property
    def default_output_dir(self):
        """Returns the default output directory for writting
        files for the scrappers
        """
        output_paths_count = len(self.output_paths)
        if output_paths_count > 0:
            if 'default' in self.output_paths[0]:
                return self.output_paths[0]['default']['path']
            return None
        return None

configuration = Configuration()




class Settings:
    def __init__(self, filename=None, versionize=False):
        # Determines whether you want to keep track
        # of the different versions of the settings file
        self.versionize = versionize

        current_path = os.path.abspath(os.path.dirname(__file__))
        if not filename:
            filename = 'config.ini'

        settings_file_path = os.path.join(current_path, filename)

        self.config_file = configparser.ConfigParser()
        self.settings = self.config_file.read(settings_file_path)

        # Pre-fill the settings file with
        # the base variables
        self.pre_populate(default_settings_file=filename)

    def update(self, section, key, value):
        """Update a specific parameter of the file
        """
        return self.config_file.set(section, key, value)

    def version(self):
        """A definition that takes care of updating the
        version of the settings file
        """
        token = secrets.token_hex(nbytes=15)
        current_version = self.__getitem__('default__version')
        if not current_version:
            current_version = '1.0'
            left, right = current_version.split('.')
            if right.__gt__(9):
                current_version = left + 1
            else:
                current_version = right + 1
            return '.'.join([left, right]), token

    def pre_populate(self, **kwargs):
        # Set the default settings file path
        # in case the user has changed it
        if 'default_settings_file' in kwargs:
            self.config_file.set('paths', 'default_settings_file', kwargs['default_settings_file'])

        # Set the base working directory
        self.config_file.set('paths', 'base_path', os.getcwd())

        # Finally, if we have kwargs, write them
        # to the settings files
        if kwargs:
            for key, value in kwargs.items():
                if not 'section' in kwargs:
                    # If no section is specified,
                    # just use the default instead
                    # of raising an error
                    section = 'DEFAULT'
                self.config_file.set(section, key, value)

        with open(kwargs['default_settings_file'], 'w') as f:
            self.config_file.write(f)

        return self.to_dict

    @property
    def to_dict(self):
        """Get the dictionnary version of the settings as an OrderedDict
        """
        return self.config_file.__dict__['_sections']

    @staticmethod
    def query(item:dict, q):
        """A defintion that transforms a query of type *section__attribute*
        to a readable element for retrieving data from a dict
        """
        if not '__' in q:
            return q
        section, attribute = q.split('__')
        return item[section][attribute]
        
    def __getitem__(self, key):
        try:
            value = self.query(self.to_dict, key)
        except KeyError:
            value = None
        return value

    @classmethod
    def hash_value(cls, raw_value):
        return sha256(raw_value.encode('utf-8')).hexdigest()

    @classmethod
    def hash_and_compare(cls, raw_value, hashed_value):
        return cls.hash_value(raw_value) == hashed_value

settings = Settings()
