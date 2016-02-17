#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Simplenote CLI

Command line interface to simplenote.

Environment Variables
    LOGLEVEL: overrides the level specified here. Default is warning

"""


import sys
import os
from optparse import OptionParser
from ConfigParser import RawConfigParser
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import math
import logging

from simplenote import Simplenote
import util.progress_bar as pb
from util.appdirs import AppDirs

# development modules, can be removed later
import pprint


__version__ = '0.3.0'


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

    log = logging.getLogger('sn')

    # get script's path
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

    appdir = AppDirs('simplenote-cli')
    local_cache = os.path.join(appdir.user_data_dir, 'data.cache')

    if args:
        log.debug('you wanted to run command: {}'.format(args[0]))
    config = RawConfigParser()
    # can pass multiple files to config.read but it merges them, which we don't
    # want. Order here:
    #
    # - exact value of -c option (ie config.ini)
    # - xdg_config_dir (ie ~/.config/vrillusions/simplenote-cli)
    # - script path, where this file resides
    # 1st try exact value
    if not config.read(options.config):
        log.info('could not read %s' % options.config)
        # next try xdg config dir
        xdg_config_file = os.path.join(appdir.user_config_dir, 'config.ini')
        if not config.read(xdg_config_file):
            log.info('could not read %s' % xdg_config_file)
            # next try script path
            script_config_file = os.path.join(script_path, 'config.ini')
            if not config.read(script_config_file):
                log.info('could not read %s' % script_config_file)
                # Still can't find it, error out
                log.critical('could not read any config file')
                return 1
    email = config.get('simplenote', 'email')
    password = config.get('simplenote', 'password')

    # TODO: GET PATH TO CACHE FILE (PROBABLY THROUGH XDG)

    #sn = Simplenote(email, password, cache_file)
    sn = Simplenote(email, password)
    sn.login()
    index = sn.full_index()
    #index = sn.index(5)
    #print '- index -'
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(index)
    log.info('number of notes: {}'.format(len(index)))
    notecount = float(len(index))
    #print '- data -'
    notes = []
    i = 0
    #for note_meta in index['data']:
    for note_meta in index:
        note = sn.note(note_meta['key'])
        notes.append(note)
        #pp.pprint(note)
        i += 1
        pb.progress(50, math.floor(float(i) / notecount * 100.0))
    log.debug('Number of api calls: {}'.format(sn.api_count))
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
    with open(options.output, 'w') as fh:
        fh.write(json.dumps(jsonnotes))


if __name__ == "__main__":
    # Logger config
    # DEBUG, INFO, WARNING, ERROR, or CRITICAL
    # This will set log level from the environment variable LOGLEVEL or default
    # to warning. You can also just hardcode the error if this is simple.
    _loglevel = getattr(logging, os.getenv('LOGLEVEL', 'WARNING').upper())
    _logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=_loglevel, format=_logformat)

    sys.exit(main())
