# Simplenote Command-line Interface

[![Project Status: Abandoned – Initial development has started, but there has not yet been a stable, usable release; the project has been abandoned and the author(s) do not intend on continuing development.](https://www.repostatus.org/badges/latest/abandoned.svg)](https://www.repostatus.org/#abandoned)

## Project has been abandoned

In early 2019 the old api was shut down.  While trying to get access to new API they suggested [sncli](https://github.com/insanum/sncli) which offers options to backup simplenote plus a whole lot more.  I see it as a superset of what this project can do and still makes it simple to create backups.

## Files

- simplenote.py: This is the library that is used by sn.py.
- sn.py: The frontend command line interface.

## Getting started

Copy config.ini.default to config.ini and add your login information.  Then run sn.py
to get a backup of your entire simplenote database.  Use the -o option to set the output
file.

## Formats supported

Currently it exports as JSON.  It tries to be compatible with 
[simplenote import](http://simplenote-import.appspot.com/) but the format could always
change.  There's also experimental xml output (has to be enabled in source code)
