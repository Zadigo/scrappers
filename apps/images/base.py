import argparse
import csv
import json
import os
import re
import zipfile
from collections import OrderedDict
from functools import lru_cache

from PIL import Image

from scrappers.apps.config.http.engine import RequestsManager
from scrappers.apps.config.logs import default
from scrappers.apps.images.mixins import ScrapperMixins


class ImageDownloader(ScrapperMixins, RequestsManager):
    """This class is the base class to send requests
    to the SawFirst website.

    Description
    -----------

        It creates a requests and scraps all the images from a given page then
        downloads the images on a local or cloud storage.

    Parameters
    ----------

        celebrity_name: accepts a celebrity name to use in order to use
        either in a file or some kind of request.

        div_id: allows you to change the start searching point in
        order to scrap the different images of the page.

        headers: add additional headers to the request
    """
    memory = OrderedDict(csv=[], json=[], html=[])

    def __init__(self, current_file, url=None, 
                 html_path=None, download_dir=None):
        self.current_dir = os.path.dirname(current_file)
        self.logger = default(
            self.__class__.__name__, 
            logfile_name=os.path.join(self.current_dir, 'scrappers.log')
        )
        self.url = url
        self.html_path = html_path

        path, _, files = list(os.walk(os.path.dirname(current_file)))[0]

        self.memory.update({'path': path})
        for item in files:
            self._sort_files(item)

        state = self._construct_download_dir(download_dir=download_dir)
        if not state:
            raise FileExistsError('Could not create or find a download directory for your application')

    def _sort_files(self, item, base_path=None):
        if '.':
            _, extension = item.split('.', 1)
            try:
                self.memory[extension].append(item)
            except KeyError:
                pass
        else:
            return False

    @lru_cache(maxsize=1)
    def load_images(self):
        loaded_images = []
        base, _, images = list(os.walk(self._scrappers_dir))[0]
        for image in images:
            full_path = os.path.join(base, image)
            if full_path.endswith('jpg'):
                loaded_images.append(
                    (
                        full_path,
                        Image.open(full_path)
                    )
                )
        return loaded_images


    @lru_cache(maxsize=1)
    def load(self, filename, run_request=False, limit=0):
        extension, _, full_path  = self.lookup(filename, just_path=False)
        with open(full_path, 'r') as f:
            if extension == 'csv':
                reader = csv.reader(f)
                self.urls = list(reader)
                self.urls.pop(0)
                self.urls = [url[1] for url in self.urls]

            if extension == 'json':
                data = json.load(f)
                for item in data['gallery']:
                    self.urls.append(item['link'])

        if run_request:
            self._download_images(limit=limit)
        return self.urls

    def save_gallery(self, filename, depth=3, f=None):
        """
        Save the links and their parents in an HTML file
        """        
        sample_tag = self.raw_tags[0]
        parents = sample_tag.find_parents()
        
        if f is not None:
            parent = None
            for item in parents:
                parent = item.parent()[0]
                if 'class' in parent.attrs or 'id' in parent.attrs:
                    for _, values in parent.attrs.items():
                        if f in values:
                            parent = item
                            break
        else:
            parent = parents[depth]
            
        with open(os.path.join(self.current_dir, filename), 'w') as f:
            f.write(str(parent))

    def save_links(self, filename=None, file_type='csv',
                   headers=[], with_index=False):
        if filename is not None:
            filename = f'{filename}.{file_type}'

        full_path = os.path.join(self.current_dir, filename)            

        with open(full_path, 'w', newline='') as f:
            if file_type == 'csv':
                writer = csv.writer(f)
                if with_index:
                    if not 'index' in headers:
                        headers.insert(0, 'index')
                    new_urls = [[index, url]
                                for index, url in enumerate(self.urls)]
                else:
                    new_urls = [[url] for url in self.urls]
                if headers:
                    new_urls.insert(0, headers)
                writer.writerows(new_urls)
                print(f'Saved {len(self.urls)} images in {full_path}')

            if file_type == 'json':
                base = {
                    'gallery': []
                }
                for index, link in enumerate(self.urls):
                    base['gallery'].append(
                        {'index': index, 'link': link}
                    )
                json.dump(base, f, indent=4)

    def _construct_download_dir(self, download_dir=None, using=None):
        if download_dir is None:
            path = os.path.join(
                os.environ.get('HOMEDRIVE'),
                os.environ.get('HOMEPATH')
            )
            images_dir = os.path.join(path, 'Pictures')
            self.logger.info(f'Created download directory in {path}')
            self.images_dir = images_dir
            return True
        else:
            if using is not None:
                pass
            else:
                self.images_dir = download_dir
            return True
        return False

    def lookup(self, filename, just_path=False):
        """
        Result
        ------

            (key, filename.ext, /path/to/file.ext)
        """
        if '.' not in filename:
            raise ValueError('Please specify a file with an extension')

        found = False

        for key, values in self.memory.items():
            if filename in values:
                found = True
                break
        
        if found:
            full_path = os.path.join(self.memory['path'], values[values.index(filename)])
            self.html_path = full_path
            if just_path:
                return full_path
            return (key, values[values.index(filename)], full_path)
        else:
            return found

    def _download_images(self, limit=0):
        # responses = self.get(self.urls)
        responses = self.threaded_get(*self.urls)
        path_exists = os.path.exists(self._scrappers_dir)
        if not path_exists:
            os.mkdir(self._scrappers_dir)

        for index, response in enumerate(responses, start=1):
            if limit != 0:
                if index == limit:
                    break
            if response.status_code == 200:
                new_name = self.create_name(index)
                full_path = os.path.join(self._scrappers_dir, f'{new_name}.jpg')
                with open(full_path, 'wb') as f:
                    for data in response.iter_content(chunk_size=1024):
                        if not data:
                            break
                        f.write(data)
                        self.saved_images.append(full_path)
                        # self.saved_images.append(
                        #     Image.load(os.path.join(self._scrappers_dir, name))
                        # )

        self.logger.warning(f'downloaded {len(self.urls)} images to {self._scrappers_dir}')
    
    def build(self, f, limit=0, regex=None, replace_with=None, pop_value:int=None, zip_files=False):
        if self.html_path is not None:
            soup = self.lazy_request(path=self.html_path)
        
        if self.url is not None:
            soup = self.get_html(*(self.url))

        if self.html_path is None and self.url is None:
            raise ValueError('You need to provide either a URL or an HTML path to use for parsing the images. You can also use the .lookup() method.')
        
        try:
            images = soup.find_all('img')
        except Exception:
            raise
        else:
            for image in images:
                url = image['src']
                if f in url and url.endswith('jpg'):
                    self.raw_tags.append(image)
                    if regex:
                        if replace_with is None:
                            replace_with = '.jpg'
                        self.urls.append(
                            self.replace_with_regex(url, regex, replace_with)
                        )
                    else:
                        self.urls.append(url)
            if pop_value is not None:
                self.urls.pop(pop_value)
            print(f'Found {len(self.urls)} images')
            # self._download_images(limit=limit)

        if zip_files is not None:
            images = self.load_images()
            with zipfile.ZipFile(os.path.join(self._scrappers_dir, 'images.zip'), mode='w') as z:
                for image in images:
                    with open(image[0], 'rb') as img:
                        z.write(img.read())
