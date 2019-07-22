from setuptools import setup
import os

def install_requires():
    base_path = os.path.abspath(__file__)
    with open(os.path.join(base_path, 'requirements.txt'), 'r', encoding='utf-8') as f:
        f.readlines()

def local_file():
    base_path = os.path.abspath(__file__)
    with open(os.path.join(base_path, 'README.rst'), 'r', encoding='utf-8') as f:
        f.read()

setup(
    name = "scrappers",
    version = '1.2',
    author = "John Pendenque",
    author_email = "pendenquejohn@gmail.com",
    description = "Scrappers API for Python",
    license = "MIT",
    keywords = "scrappers scrapping",
    url = "https://github.com/scrappers/Wikipedia",
    install_requires = install_requires(),
    packages = ['scrappers'],
    long_description = local_file(),
    classifiers = [
        'Development Status :: 1.2',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ]
)