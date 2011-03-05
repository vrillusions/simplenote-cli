#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Simplenote CLI

Command line interface to simplenote.

"""


import urllib
import urllib2
import base64
import sys
import traceback
from optparse import OptionParser
from ConfigParser import ConfigParser

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
        self.last_error = ''
    
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
            self.last_error = 'http error: ' + str(e.code)
            print e.readlines()
            return None
        except urllib2.URLError, e:
            # Non http error, like network issue
            self.last_error = 'url error:', e.reason
            return None
        fh.close()
    
    def note(self):
        pass
    
    def delete(self):
        pass
    
    def index(self, length=100):
        url = self.base_url + 'index'
        query = {'length': length, 'auth': self.authtok, 'email': self.email}
        data = urllib.urlencode(query)
        # this is a get request so everything is sent in url
        fh = urllib2.urlopen(url + '?' + data)
        index = fh.read()
        fh.close()
        return index

 
def main():
    """The main function."""
    parser = OptionParser(version='%prog v' + __version__)
    parser.add_option('-c', '--config', default='config.ini',
        help='Location of config file (default: %default)', metavar='FILE')
    (options, args) = parser.parse_args() 
 
    config = ConfigParser()
    config.read(options.config)
    email = config.get('simplenote', 'email')
    password = config.get('simplenote', 'password')
    
    sn = Simplenote(email, password)
    sn.login()
    if sn.last_error != '':
        print 'ERROR:', sn.last_error
        sys.exit(1)
    print sn.index(1)
 
 
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt, e:
		# Ctrl-c
		raise e
	except SystemExit, e:
		# sys.exit()
		raise e
	except Exception, e:
		print "ERROR, UNEXPECTED EXCEPTION"
		print str(e)
		traceback.print_exc()
		sys.exit(1)
	else:
		# Main function is done, exit cleanly
		sys.exit(0)
