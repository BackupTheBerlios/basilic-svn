# ______________________________________________________________________
"""Config file handling module 
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn

Handles everything about the configuration file. Default settings stands
here.

$Id$
"""
# ______________________________________________________________________

import version
from ConfigParser import SafeConfigParser
import time, os.path, sys

default_config={
    'global': {
        'language': 'fr',
        'encoding': 'utf-8',
        'database': 'db/default.sdb',
        'debug': 0,
    },
    'http-server': {
        'active': 1,
        'port': 6666,
        'host': '',
        'encoding': 'utf-8',
    },
    'xmlrpc-server': {
        'active': 0,
        'port': 6667,
        'host': '',
        'enxcoding': 'iso-8859-1',
    },
}

# Compute the "binaries" path - it is the directory of this file
class dummy:
    pass

from_directory=os.path.abspath(os.path.dirname(sys.modules[dummy.__module__].__file__))


def read_config(config_filename="default.cfg", override=default_config):
    """Reads a config file, config_filename and returns the config structure. If override is specified
    the read configuration updates this one. Default config is used when no override given
    so that configuration file should never lack mandatory values.
    If config filename is default one and does not exists, it is created using the
    default_config values."""
    result=override
    if config_filename=="default.cfg" and not os.path.isfile(config_filename): # if no default config file found, write the default one
        print _("No config file found, generating a default one, here : %s.") % os.path.abspath(config_filename)
        write_config(config_filename)
    c=SafeConfigParser()
    c.read([config_filename])
    for section in c.sections(): # iterate over sections
        for key in c.options(section): # iterate over values of section
            if not result.has_key(section):
                result[section]={}
            try: # trying first for integer
                value=c.getint(section,key)
            except ValueError: # else assume it's a string
                value=c.get(section,key)
            result[section][key]=value
    return result

def write_config(config_filename, config=default_config):
    """Writes the config_filename with given config. If config is omitted, the
    default configuration structure is used. This is useful for writing the 
    initial structure to the disk"""
    comments=""
    if config==default_config:
        comments+="# %s \n" % version.version_string
        comments+="# This is the default config file\n"
        comments+="# Generated on %s \n" % time.strftime('%x %X %Z')
        comments+="# Visit %s for more informations \n" % version.project_url
    c=SafeConfigParser()
    f=open(config_filename,'w')
    f.write(comments+"\n")
    for section in config.items():
        name=section[0]
        values=section[1]
        c.add_section(name)
        for value in values.items():
            c.set(name, value[0], value[1])
    c.write(f)
    f.flush()
    f.close()
