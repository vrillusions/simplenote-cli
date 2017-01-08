#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Simplenote CLI

Command line interface to simplenote.

Environment Variables
    LOGLEVEL: overrides the level specified here. Default is warning

"""
import sys
import os
import errno
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


__version__ = '0.4.0-dev'


class ConfigError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class SimpleNoteCache(object):
    def __init__(self, cache_dir):
        self._log = logging.getLogger('sn.SimpleNoteCache')
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(self.cache_dir, 'cache.json')
        self._load_cache()

    def _load_cache(self, call_count=1):
        self._log.debug(
            'Loading cache from %s. Attempt %s',
            self.cache_file,
            call_count)
        try:
            with open(self.cache_file, 'r') as fh:
                self.cache = json.loads(fh.read())
        except IOError as exc:
            if call_count > 2:
                self._log.critical('loading cache failed 3 times. giving up')
                raise
            if errno.errorcode[exc.errno] == 'ENOENT':
                self._log.info('cache file does not exist. creating')
                self.cache = {}
                self.save_cache()
                self._load_cache(call_count=call_count + 1)
            else:
                raise

    def save_cache(self, call_count=1):
        self._log.debug(
            'saving cache to %s. Attempt %s',
            self.cache_file,
            call_count)
        try:
            with open(self.cache_file, 'w') as fh:
                fh.write(json.dumps(self.cache))
        except IOError as exc:
            if call_count > 2:
                self._log.critical('saving cache failed 3 times. giving up')
                raise
            if errno.errorcode[exc.errno] == 'ENOENT':
                self._log.info('creating new cache file %s', self.cache_file)
                os.makedirs(self.cache_dir)
                self.save_cache(call_count=call_count + 1)
            else:
                raise

    def get_changed(self, index):
        self._log.info('index count: %s', len(index))
        cache_notes = self.cache.keys()
        index_notes = [x['key'] for x in index]
        changed_notes = []
        for cache_note in cache_notes:
            if cache_note not in index_notes:
                self._log.debug('note %s not in index, deleting', cache_note)
                del self.cache[cache_note]
        # TODO:2017-01-08: probably a more efficient way of looking up a value
        index_dict = {}
        for note in index:
            index_dict[note['key']] = note
        for (key, value) in self.cache.items():
            if value['syncnum'] != index_dict[key]['syncnum']:
                self._log.debug(
                    'note %s syncnum %s differs from index syncnum %s',
                    key,
                    value['syncnum'],
                    index_dict[key]['syncnum'])
                changed_notes.append(key)
        for index_note in index:
            if index_note['key'] not in self.cache:
                self._log.debug('found new note %s', index_note['key'])
                changed_notes.append(index_note['key'])
        return changed_notes


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


def read_first_config(files):
    """parse the first file that exists then return config object

    config.read() will parse all files in a list and merge them together with
    the last file that exists taking precedence.  This will try each file in the
    list and the first file that exists it will read in then stop.

    @return config object
    @raises ConfigError() if no files could be found
    """
    log = logging.getLogger('sn.read_first_config')
    config = RawConfigParser()
    for config_file in files:
        log.debug('Attempting to read %s', config_file)
        if config.read(config_file):
            return config
    raise ConfigError('could not read any config file')


def main():
    """The main function."""
    parser = OptionParser(version='%prog v' + __version__)
    parser.add_option(
        '-c', '--config', default='',
        help='Location of config file', metavar='FILE')
    parser.add_option(
        '-o', '--output', default='simplenotebak.json.txt',
        help='Output file name (default: %default)', metavar='FILE')
    parser.add_option(
        '-q', '--quiet', default=False,
        help='Suppres output, mainly progress bar', action='store_true')
    (options, args) = parser.parse_args()
    log = logging.getLogger('sn')
    appdir = AppDirs('simplenote-cli')
    if args:
        log.debug('you wanted to run command: {}'.format(args[0]))
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    config_files = [
        options.config,
        os.path.join(appdir.user_config_dir, 'config.ini'),
        os.path.join(script_path, 'config.ini'),
    ]
    config = read_first_config(config_files)
    email = config.get('simplenote', 'email')
    password = config.get('simplenote', 'password')
    if config.has_option('simplenote', 'data_dir'):
        data_dir = config.get('simplenote', 'data_dir')
    else:
        data_dir = appdir.user_data_dir
    sn = Simplenote(email, password)
    sn.login()
    sncache = SimpleNoteCache(data_dir)
    log.debug('loading index')
    index = sn.full_index()
    changed = sncache.get_changed(index)
    if log.isEnabledFor(logging.DEBUG):
        log.debug('saving entire index file as fullindex.json.txt')
        with open('fullindex.json.txt', 'w') as fh:
            fh.write(json.dumps(index))
    log.info('number of changes: %s', len(changed))
    notecount = float(len(changed))
    i = 0
    for note_id in changed:
        note = sn.note(note_id)
        sncache.cache[note_id] = note
        i += 1
        if i % 50 == 0:
            log.debug('%s items added, save cache', i)
            sncache.save_cache()
        if not options.quiet:
            pb.progress(50, math.floor(float(i) / notecount * 100.0))
    sncache.save_cache()
    log.info('Number of api calls: {}'.format(sn.api_count))
    if log.isEnabledFor(logging.DEBUG):
        log.debug('saving all notes as fullnotes.json.txt')
        with open('fullnotes.json.txt', 'w') as fh:
            fh.write(json.dumps(sncache.cache))
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
    for note in sncache.cache.values():
        if note['deleted'] == 1:
            continue
        json_note_tmp = {'modifydate': format_date(float(note['modifydate']))}
        json_note_tmp.update({'createdate': format_date(float(note['createdate']))})
        json_note_tmp.update({'tags': note['tags']})
        json_note_tmp.update({'systemtags': note['systemtags']})
        json_note_tmp.update({'content': note['content']})
        json_note_tmp.update({'key': note['key']})
        jsonnotes.append(json_note_tmp)
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
