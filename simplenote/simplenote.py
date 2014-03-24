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
import logging
import json

from .exceptions import SimplenoteError


__all__ = ['Simplenote']


_logger = logging.getLogger(__name__)


class Simplenote(object):
    """The core Simplenote class."""
    def __init__(self, email, password):
        """Sets up initial variables.

        email: The users' email address
        password: The users' password

        """
        _logger.debug('Entered Simplenote()')
        self.base_url = 'https://simple-note.appspot.com/api2/'
        self.email = email
        self.password = password
        self.authtok = ''
        self.api_count = 0

    def _process_query(self, url, query={}, add_authtok=True):
        """Processes the given url and query dictionary

        It's assumed all calls are GET requests and data is returned
        in JSON format. Increments api_count each time it's run.
        Returns False on error.

        url: The full url
        query (optional): Key, value dictionary with query variables.
        add_authtok (default: True): adds authentication information to
            query string

        """
        if add_authtok:
            if self.authtok == '':
                self._error('No auth token, must login first')
                return False
            query.update({'auth': self.authtok, 'email': self.email})

        if len(query) > 0:
            request = url + '?' + urllib.urlencode(query)
        else:
            request = url

        self.api_count += 1
        try:
            fh = urllib2.urlopen(request)
            response = fh.read()
            fh.close()
        except urllib2.HTTPError, e:
            # Received a non 2xx status code
            raise SimplenoteError('http error: ' + str(e.code))
        except urllib2.URLError, e:
            # Non http error, like network issue
            raise SimplenoteError('url error:' + e.reason)
        return json.loads(response)

    def login(self):
        """Logs in to Simplenote. Required before other methods.

        Returns False on error, True if successful.

        """
        # the login url is just api, not api2
        url = 'https://simple-note.appspot.com/api/login'
        query = {'email': self.email, 'password': self.password}
        data = base64.b64encode(urllib.urlencode(query))
        try:
            fh = urllib2.urlopen(url, data)
            self.authtok = fh.read()
        except urllib2.HTTPError, e:
            # Received a non 2xx status code
            raise SimplenoteError('http error: ' + str(e.code))
        except urllib2.URLError, e:
            # Non http error, like network issue
            raise SimplenoteError('url error:' + e.reason)
        fh.close()
        return True

    def note(self, key=None):
        """Retreives a single note.

        key: The note's key (can be obtained from index call)

        """
        if key == None:
            raise SimplenoteError('Unable to get note: Key not given')
        url = self.base_url + 'data/' + key
        note = self._process_query(url)
        return note

    def delete(self):
        raise NotImplementedError()

    def index(self, length=100, mark=None):
        """Retrieves index of notes.

        length: How many to retreive, defaults to 100 (max)
        mark: Get the next batch of notes.

        """
        url = self.base_url + 'index'
        query = {'length': length}
        if mark is not None:
            query.update({'mark': mark})
        index = self._process_query(url, query)
        return index

    def full_index(self):
        """Retrieves full index of notes."""
        indextmp = self.index()
        full_index = []
        for note in indextmp['data']:
            full_index.append(note)
        while True:
            if 'mark' in indextmp:
                mark = indextmp['mark']
                indextmp = ''
                indextmp = self.index(mark=mark)
                for note in indextmp['data']:
                    full_index.append(note)
            else:
                break
        return full_index
