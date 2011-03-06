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
from subprocess import Popen, PIPE
# Make some effort to be backwards compatible with 2.5
try: 
    import json
except ImportError: 
    import simplejson as json
    
from simplenote import Simplenote

# development modules, can be removed later
import pprint


git_version = Popen(['git', 'describe', '--always'], 
    stdout=PIPE, stderr=PIPE).stdout.read().strip()
__version__ = git_version if git_version else 'alpha'


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
    index = sn.index(1)
    pp = pprint.PrettyPrinter(indent=4)
    for note_meta in index['data']:
        note = sn.note(note_meta['key'])
        pp.pprint(note)
 
 
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
