from setuptools import setup

setup(
    name = "scrappers",
    version = '1.2',
    author = "John Pendenque",
    author_email = "jhghank@gmail.com",
    description = "Wikipedia API for Python",
    license = "MIT",
    keywords = "scrappers scrapping",
    url = "https://github.com/scrappers/Wikipedia",
    install_requires = install_reqs,
    packages = ['scrappers'],
    long_description = local_file('README.rst').read(),
    classifiers = [
        'Development Status :: 1.2',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ]
)