import setuptools
from os import path
from setuptools import setup
import os

root = path.abspath(path.dirname(__file__))

def read_files(filename):
    with open(path.join(root, filename), 'r', encoding='utf-8') as f:
        return f.read()


def install_requires():
    with open(os.path.join(root, 'requirements.txt'), 'r', encoding='utf-8') as f:
        f.readlines()


classifiers = [
    'Development Status :: 2 - Pre-Alpha',

    'Programming Language :: Python :: 3',

    'License :: OSI Approved :: MIT License',

    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',

    # 'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Software Development :: Libraries',
]


setup(
    name = 'scrappers',
    version=exec(open(path.join(root, 'version.py')).read()),
    author = 'John Pendenque',
    author_email = 'pendenquejohn@gmail.com',
    description = 'Various scrappers API for Python',
    license = 'MIT',
    long_description=read_files('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/Zadigo/scrappers',
    keywords = 'scrappers scrapping',
    install_requires = install_requires(),
    packages = ['scrappers'],
    classifiers = classifiers
)
