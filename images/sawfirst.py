import re

from scrappers.engine.requestor import Requestor
from scrappers.engine.utilities import writer


class SawFirst(Requestor):
    def __init__(self, url, celebrity=None):
        super().__init__(url)

        urls = []

        # div#gallery-1
        gallery = self.soup.find('div', attrs={'id': 'gallery-1'})

        # dl
        gallery_items = gallery.find_all('dl', attrs={'class': 'gallery-item'})

        for gallery_item in gallery_items:
            # img
            image_url = gallery_item.find('img')['src']
            # Get the url without the -130x70.jpg
            clean_url = re.match(r'(.*(?=\-\d+x\d+\.(jpg)))', image_url)
            if clean_url:
                composed_url = clean_url.group(1) + '.%s' % clean_url.group(2)
                urls.append(composed_url)
        
        # Write file
        writer(urls, celebrity)
