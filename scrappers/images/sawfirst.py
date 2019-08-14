import re

from scrappers.scrappers.config.http.engine import Requestor
from scrappers.scrappers.config.utilities import writer
from scrappers.scrappers.config.utilities import prepare_values, prepare_for_s3


class SawFirst(Requestor):
    """This class is the base class to send requests
    to the SawFirst website.

    Description
    -----------

    It creates a requests and scraps all the images from a given page then
    downloads the images on a local or cloud storage.

    Parameters
    ----------

    The `celebrity` parameter accepts a celibrity name to use in order to use
    either in a file or some kind of request.

    The `div_id` parameter allows you to change the start searching point in
    order to scrap the different images of the page.
    """
    def __init__(self, url, celebrity=None, div_id='gallery-1'):
        soup = super().create_request(url)

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
        
    # @prepare_values
    # def to_file(self):
    #     if self.urls:
    #         return self.urls
    #     return []

    @prepare_for_s3
    def to_s3_folder(self):
        return self.urls
    
    # def to_local(self):
    #     pass

url = 'https://www.sawfirst.com/adriana-lima-booty-in-bikini-on-the-beach-in-miami-2019-08-14.html/supermodel-adriana-lima-wears-a-tiny-string-bikini-as-she-hits-the-beach-in-miami-2'
s = SawFirst(url)
s.to_s3_folder(access_key='s', secret_key='s', region='s', bucket='s')