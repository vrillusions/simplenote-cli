# Simplenote Command-line Interface

Currently just a way to do offsite backups via command-line but will eventually
be a more full-featured [simplenote](http://simplenoteapp.com) client.

# Development Status

It currently works but still consider alpha until things are cleared up.

CAUTION: if you use this right now only have it run like once a week or longer. It pulls
all notes regardless if they changed or not.  So if you have 300 notes it's going to make
a total of 304 api requests to simplenote (300 notes + 3 index calls + 1 login) each time
you run this!  Eventually it will have a cache so it will only download the notes that 
have changed, allowing it ro run more frequently.

# Files

- simplenote.py: This is the library that is used by sn.py.
- sn.py: The frontend command line interface.

# Getting started

Copy config.ini.default to config.ini and add your login information.  Then run sn.py
to get a backup of your entire simplenote database.  Use the -o option to set the output
file.

# Formats supported

Currently it exports as JSON.  It tries to be compatible with 
[simplenote import](http://simplenote-import.appspot.com/) but the format could always
change.  There's also experimental xml output (has to be enabled in source code)
