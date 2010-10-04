#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Getopts template

When a script has many command line options, use this.

TODO: perhaps better way to handle global variables, options, etc

"""


import urllib
import urllib2

# Make some effort to be backwards compatible with 2.5
try: 
    import json
except ImportError: 
    import simplejson as json


__version__ = 'alpha'


class Simplenote:
    """The core Simplenote class"""
    def __init__(self, email, password):
        self.base_url = 'https://simple-note.appspot.com/api2/'
        self.email = email
        self.password = password
    
    def login(self):
        pass
    
    def note(self):
        pass
    
    def delete(self):
        pass
