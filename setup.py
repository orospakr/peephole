#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "Peephole",
    version = "0.3",
    packages = find_packages(),
    #    scripts = ['say_hello.py'],

    install_requires = ['pyusb>=0.4.1'],

    #     package_data = {
    #         # If any package contains *.txt or *.rst files, include them:
        #         '': ['*.txt', '*.rst'],
    #         # And include any *.msg files found in the 'hello' package, too:
        #         'hello': ['*.msg'],
    #     }

    entry_points = {
        'console_scripts': [
            'peephole = peephole.peepholed:main'
            ]
        },

    # metadata for upload to PyPI
    author = "Andrew Clunis",
    author_email = "andrew@orospakr.ca",
    description = "A simple D-Bus daemon that provides a simple API for accessing attached segmented/low resolution matrix LCD displays",
    license = "GPLv3",
    keywords = "lcd dbus driver abstraction",
    url = "http://www.orospakr.ca/"   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
    )
