from setuptools import setup
import os

BASE_PATH = os.path.abspath(__file__)

def install_requires():
    with open(os.path.join(BASE_PATH, 'requirements.txt'), 'r', encoding='utf-8') as f:
        f.readlines()

def local_file():
    with open(os.path.join(BASE_PATH, 'README.rst'), 'r', encoding='utf-8') as f:
        f.read()

setup(
    name = 'scrappers',
    version = '1.1',
    author = "John Pendenque",
    author_email = "pendenquejohn@gmail.com",
    description = "Various scrappers API for Python",
    license = "MIT",
    keywords = "scrappers scrapping",
    url = "https://github.com/scrappers/Wikipedia",
    install_requires = install_requires(),
    packages = ['scrappers'],
    long_description = local_file(),
    classifiers = [
        'Development Status :: 1.1',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ]
)