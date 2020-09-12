import csv
import datetime
import functools
import json
import logging
import os
import re
from collections import namedtuple
from pathlib import Path
from urllib import parse

from PIL.Image import Image

from scrappers.apps.config.logs import default


class ScrapperMixins:
    file_path = None
    raw_tags = []
    urls = []
    images_dir = None
    saved_images = []

    def __getitem__(self, index):
        return self.urls[index]

    def __len__(self):
        return len(self.urls)

    def __enter__(self):
        return self.urls

    def __exit__(self, exc_type, exc, exc_tb):
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}(links={self.__len__()})'

    def __str__(self):
        return str(self.urls)

    @functools.cached_property
    def _scrappers_dir(self, substitute=None):
        return os.path.join(self.images_dir, 'scrappers')

    @staticmethod
    def reconstruct_parent(tag):
        pass

    @functools.lru_cache(maxsize=5)
    def get_urls(self):
        return self.urls
        
    def replace_with_regex(self, url, regex, replace_with):
        return re.sub(regex, replace_with, url)

    def create_name(self, index):
        d = datetime.datetime.now().date()
        return f"{d.year}-{d.month}-{d.day}-{index}"
