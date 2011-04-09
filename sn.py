#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Simplenote CLI

Command line interface to simplenote.

"""


import sys
import os
import traceback
from optparse import OptionParser
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import math

from simplenote import Simplenote
import progress_bar as pb

# development modules, can be removed later
import pprint


git_version = Popen(['git', 'describe', '--always'], 
    stdout=PIPE, stderr=PIPE).stdout.read().strip()
__version__ = git_version if git_version else 'alpha'


def dict_to_xml(dict):
    """Takes a dictionary and creates xml."""
    root = ET.Element('note')
    for field, value in dict.iteritems():
        if str(value) == '[]':
            continue
        ET.SubElement(root, field).text = str(value)
    return root


def format_date(timestamp):
    date = datetime.fromtimestamp(timestamp)
    return date.strftime('%b %d %Y %H:%M:%S')
    
    
def main():
    """The main function."""
    parser = OptionParser(version='%prog v' + __version__)
    parser.add_option('-c', '--config', default='config.ini',
        help='Location of config file (default: %default)', metavar='FILE')
    parser.add_option('-o', '--output', default='simplenotebak.json.txt',
        help='Output file name (default: %default)', metavar='FILE')
    (options, args) = parser.parse_args() 
 
    # set script's path and add '/' to end
    script_path = os.path.abspath(os.path.dirname(sys.argv[0])) + '/'
 
    if args:
        print 'debug: you wanted to run command: ' + args[0]
    
    config = ConfigParser()
    # can pass multiple files to config.read but it merges them, which we don't want
    if not config.read(options.config):
        # could not read file, try the script's path
        if not config.read(script_path + options.config):
            # Still can't find it, error out
            print 'Could not read any config file'
            sys.exit(1)
    email = config.get('simplenote', 'email')
    password = config.get('simplenote', 'password')
    
    sn = Simplenote(email, password)
    if not sn.login():
        print 'ERROR:', sn.last_error
        sys.exit(1)
    index = sn.full_index()
    #index = sn.index(5)
    if sn.has_error:
        print 'ERROR:', sn.last_error
        sys.exit(1)
    #print '- index -'
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(index)
    print 'number of notes:', str(len(index))
    notecount = float(len(index))
    #print '- data -'
    notes = []
    i = 0
    #for note_meta in index['data']:
    for note_meta in index:
        note = sn.note(note_meta['key'])
        if sn.has_error:
            print 'ERROR:', sn.last_error
            sys.exit(1)
        notes.append(note)
        #pp.pprint(note)
        i += 1
        pb.progress(50, math.floor(float(i) / notecount * 100.0))
    print 'Number of api calls:', str(sn.api_count)
    # xml format
    #xmlnotes = ''
    #for note in notes:
    #    if 'xml' in locals():
    #        xml.append(dict_to_xml(note))
    #    else:
    #        xml = dict_to_xml(note)
    #xmlnotes = '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
    #xmlnotes += ET.tostring(xml, encoding="UTF-8")
    #print xmlnotes
    # JSON format
    jsonnotes = []
    i = 0
    for note in notes:
        if note['deleted'] == 1:
            continue
        json_note_tmp = {'modifydate': format_date(float(note['modifydate']))}
        json_note_tmp.update({'createdate': format_date(float(note['createdate']))})
        json_note_tmp.update({'tags': note['tags']})
        json_note_tmp.update({'systemtags': note['systemtags']})
        json_note_tmp.update({'content': note['content']})
        json_note_tmp.update({'key': note['key']})
        jsonnotes.append(json_note_tmp)
    #print json.dumps(jsonnotes)
    fh = open(options.output, 'w')
    fh.write(json.dumps(jsonnotes))
    fh.close()
 
 
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
