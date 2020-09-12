import argparse
import importlib

class Manager:
    apps = []
    def __init__(self, *, app_list=[]):
        module = importlib.import_module('scrappers.apps.images.base', package='scrappers')
        module_dict = module.__dict__
        for key, value in module_dict.items():
            if callable(value) and not key.startswith('__'):
                if key in app_list:
                    self.apps.append((value.app_name, value))

    def get(self):
        pass
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a scrapper for downloading images')
    manager = Manager(
        app_list=['ImageDownloader']
    )
    choices = [app[1].app_name for app in manager.apps]
    parser.add_argument('--scrapper', '-s', required=True, choices=choices)
    parser.add_argument('--url', '-u', required=True, type=str, help='The url to request from')
    args = parser.parse_args()
