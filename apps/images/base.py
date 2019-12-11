import asyncio
import re
from asyncio import tasks

from scrappers.apps.config.http.engine import RequestsManager


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

class PicturePub(RequestsManager):
    def __init__(self, url, **kwargs):
        self.urls = []

async def run_app(url, app=None, **kwargs):
    if app == 'sawfirst':
        await SawFirst(url, **kwargs).urls

    elif app == 'picturepub':
        await PicturePub(url, **kwargs).urls

def create():
    asyncio.run(run_app)



async def google():
    return 'Fast'

async def part():
    return 'Paris'

async def test():
    await google()
    await part()

asyncio.run(test())
