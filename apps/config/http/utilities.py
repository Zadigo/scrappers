import requests
import asyncio
from asyncio import tasks
from scrappers.apps.config.http import user_agent

class UtilitiesMixin:
    @staticmethod
    def clean(value):
        return str(value).strip()

    @classmethod
    def full_clean(cls, value):
        return cls.clean(value).lower()

    def flatten(self, value):
        accents = {
            'é': 'e',
            'è': 'e',
            'ë': 'e',
            'ê': 'e',
            'ï': 'i',
            'î': 'i',
            'ù': 'u'
        }
        value = self.full_clean(value)
        for letter in accents:
            if letter in accents:
                letter = accents[letter]
                word = word + letter
        return word
    
def asynchronous_requests(urls, return_data=None, using=None):
    def manager():
        async def send_request(url):
            return requests.get(url, headers={'User-Agent': user_agent.get_rand_agent()})

        async def main():
            for url in urls:
                response = await send_request(url)
                if return_data:
                    for block in response.iter_content(1024):
                        if not response.ok:
                            return
                        if not block:
                            break
                        return block
                    # return response.content

        return asyncio.run(main())
    return manager

from scrappers.apps.config.http.aws import TransferManager

bucket_name = 'mybusinesses'
access_key = 'AKIAZP4QDMZRKNE6VASE'
secret_key = '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'
region_name = 'eu-west-3'

urls = ['https://www.sawfirst.com/wp-content/uploads/2019/12/Christine-McGuinness-Ass-1.jpg']
t = TransferManager(bucket_name, access_key, secret_key, region_name)
t.upload(asynchronous_requests(urls, return_data=True)(), 'nawoka/products', 'image/jpg')