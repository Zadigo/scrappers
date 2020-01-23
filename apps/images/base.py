import asyncio
import re
from asyncio import tasks
from collections import namedtuple

from scrappers.apps.config.http.utilities import asynchronous_requests
from scrappers.apps.config.http.managers import RequestsManager
from scrappers.apps.config.http.aws import TransferManager

class ImagesScrapper:
    """A base class for all image scrappers
    """
    urls = []

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        urls = namedtuple('Images', ['links'])
        return str(urls(self.urls))

    def __getitem__(self, index):
        return self.urls[index]

    def __enter__(self):
        return self.urls

    def init_kwargs(self, **kwargs):
        """Initializes the keyword arguments making sure that
        everything is present and that the applications can proceed
        without any difficulties
        """
        if 'celebrity_name' not in kwargs:
            if 'url' in kwargs:
                name = self.guess_celebrity(kwargs['url'])
                kwargs['celebrity_name'] = name
            else:
                kwargs['celebrity_name'] = ''
        else:
            pass

        if 'div_id' not in kwargs:
            # Initialize the div_id with a default iD
            # that the website uses. This can be
            # overrided in case there has been a change
            kwargs['div_id'] = 'gallery-1'
        else:
            if kwargs['div_id'] == '' or kwargs['div_id'] is None:
                kwargs['div_id'] = 'gallery-1'

        return kwargs

    @classmethod
    def download_images(cls, images):
        """A special definition that sends requests using the scrapped
        urls in order to download or upload the images to a host
        """
        return asynchronous_requests(cls.urls)

    @staticmethod
    def guess_celebrity(url, pattern=None):
        celebrity = re.match(r'([a-zA-Z\-]+)(?=\-\d{1,3})', url)
        if celebrity:
            name = celebrity.group(1).replace('-', ' ')
            return name
        return ''

    def upload_to_aws(self, data):
        """Upload a given image to AWS S3 bucket"""
        pass

class SawFirst(RequestsManager, ImagesScrapper):
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
    def __init__(self, url, **kwargs):
        kwargs = super().init_kwargs(url=url, **kwargs)
        # Get the HTML elements of the page
        soup = self.beautify_single(url)
        
        urls = []

        # div#gallery-1
        gallery = soup.find('div', attrs={'id': kwargs['div_id']})

        # dl
        gallery_items = gallery.find_all('figure', attrs={'class': 'gallery-item'})

        for gallery_item in gallery_items:
            if not gallery_item.is_empty_element:
                # img
                image_url = gallery_item.find('img')['src']

                # Get the url without the -130x70.jpg
                clean_url = re.match(r'(.*(?=\-\d+x\d+\.(jpg)))', image_url)

                if clean_url:
                    # In order to get the real image and not the thumbnail,
                    # we have to recompose the url from 
                    # 'celebrity-1-130x170.jpg' to 'celebrity-1.jpg'
                    composed_url = clean_url.group(1) + '.%s' % clean_url.group(2)
                    urls.append(composed_url)
            else:
                pass

        self.urls = urls
        self.name = kwargs['celebrity_name']

class PicturePub(RequestsManager, ImagesScrapper):
    def __init__(self, url, **kwargs):
        soup = self.beautify_single(url)

# url = 'https://www.sawfirst.com/christine-mcguinness-booty-in-tights-leaving-the-gym-in-cheshire-2019-12-23.html'
# manager = SawFirst(url)
# print(manager.name)