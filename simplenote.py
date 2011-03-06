#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Simplenote

Python interface to simplenote.

Licensed under MIT license. Read COPYING for information.

Usage:
from simplenote import Simplenote
sn = Simplenote(email, password)
sn.login()
index = sn.index(length)  # length can be anywhere from 1-100
for note_meta in index['data']:
    note = sn.note(note_meta['key'])
    print note['content']

"""


import urllib
import urllib2
import base64
import sys
from subprocess import Popen, PIPE
# Make some effort to be backwards compatible with 2.5
try: 
    import json
except ImportError: 
    import simplejson as json


git_version = Popen(['git', 'describe', '--always'], 
    stdout=PIPE, stderr=PIPE).stdout.read().strip()
__version__ = git_version if git_version else 'alpha'
# cleanup so this doesn't showup in pydoc
del git_version, PIPE


class Simplenote:
    """The core Simplenote class."""
    def __init__(self, email, password):
        self.base_url = 'https://simple-note.appspot.com/api2/'
        self.email = email
        self.password = password
        self.has_error = False
        self.last_error = ''
     
    def _error(self, msg='', exitcode=None):
        self.has_error = True
        self.last_error = msg
        if exitcode != None:
            print msg
            sys.exit(exitcode)
        
    def login(self):
        # the login url is just api
        url = 'https://simple-note.appspot.com/api/login'
        query = {'email': self.email, 'password': self.password}
        data = base64.b64encode(urllib.urlencode(query))
        try:
            fh = urllib2.urlopen(url, data)
            self.authtok = fh.read()
        except urllib2.HTTPError, e:
            # Received a non 2xx status code
            self._error('http error: ' + str(e.code))
            print e.readlines()
            return None
        except urllib2.URLError, e:
            # Non http error, like network issue
            self._error('url error:' + e.reason)
            return None
        fh.close()
    
    def note(self, key=None):
        if key == None:
            self._error('Unable to get note: Key not given')
        url = self.base_url + 'data/' + key
        query = {'auth': self.authtok, 'email': self.email}
        data = urllib.urlencode(query)
        fh = urllib2.urlopen(url + '?' + data)
        note = json.loads(fh.read())
        fh.close()
        return note
    
    def delete(self):
        pass
    
    def index(self, length=100):
        url = self.base_url + 'index'
        query = {'length': length, 'auth': self.authtok, 'email': self.email}
        data = urllib.urlencode(query)
        # this is a get request so everything is sent in url
        fh = urllib2.urlopen(url + '?' + data)
        index = json.loads(fh.read())
        fh.close()
        return index