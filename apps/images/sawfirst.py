import argparse
import re

from scrappers.apps.config.http.engine import RequestsManager

# from scrappers.scrappers.config.decorators import write_image
# from scrappers.scrappers.config.http.engine import Requestor
# from scrappers.scrappers.config.utilities import (create_request,
#                                                   prepare_for_s3,
#                                                   prepare_values, writer)


# class SawFirst(Requestor):
#     """This class is the base class to send requests
#     to the SawFirst website.

#     Description
#     -----------

#         It creates a requests and scraps all the images from a given page then
#         downloads the images on a local or cloud storage.

#     Parameters
#     ----------

#         celebrity: accepts a celebrity name to use in order to use
#         either in a file or some kind of request.

#         div_id: allows you to change the start searching point in
#         order to scrap the different images of the page.
#     """
#     def __init__(self, url, celebrity=None, div_id='gallery-1'):
#         soup = super().create_request(url)

#         # Get celebrity name
#         if not celebrity:
#             celebrity = re.match(r'([a-zA-Z\-]+)(?=\-\d{1,3})', url)
#             if celebrity:
#                 name = celebrity.group(1).replace('-', ' ')

#         urls = []

#         # div#gallery-1
#         gallery = soup.find('div', attrs={'id': div_id})

#         # dl
#         gallery_items = gallery.find_all('figure', attrs={'class': 'gallery-item'})

#         for gallery_item in gallery_items:
#             # img
#             image_url = gallery_item.find('img')['src']

#             # Get the url without the -130x70.jpg
#             clean_url = re.match(r'(.*(?=\-\d+x\d+\.(jpg)))', image_url)

#             if clean_url:
#                 # In order to get the real image and not the thumbnail,
#                 # we have to recompose the url from 
#                 # 'celebrity-1-130x170.jpg' to 'celebrity-1.jpg'
#                 composed_url = clean_url.group(1) + '.%s' % clean_url.group(2)
#                 urls.append(composed_url)

#         self.urls = urls
#         self.name = name
        
#     @prepare_values
#     def urls_to_file(self):
#         if self.urls:
#             return self.urls
#         return []

#     @prepare_for_s3
#     def to_s3_folder(self):
#         return self.urls
    
#     @write_image
#     def to_local(self, celebrity=None):
#         for url in self.urls:
#             return create_request(url, data=True)

class SawFirst(RequestsManager):
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
        soup = self.get_html(url)

        # Get celebrity name
        if not celebrity:
            celebrity = re.match(r'([a-zA-Z\-]+)(?=\-\d{1,3})', url)
            if celebrity:
                name = celebrity.group(1).replace('-', ' ')

        if not 'div_id' in kwargs:
            div_id = ''

        urls = []

        # div#gallery-1
        gallery = soup.find('div', attrs={'id': div_id})

        # dl
        gallery_items = gallery.find_all('figure', attrs={'class': 'gallery-item'})

        for gallery_item in gallery_items:
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

        self.urls = urls
        self.name = name