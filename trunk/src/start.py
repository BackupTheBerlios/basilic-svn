# ______________________________________________________________________
"""Basilic Starter.
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL.

A simple launcher for basilic server
Config file is read. Servers are launched.
This file is not supposed to be modified by user nor admin.

$Id: start.py 10 2005-10-30 16:47:54Z odeckmyn $
Original file is there :
$URL$
"""
# ______________________________________________________________________

# Remove some warnings for the starter
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, append=1)

# imports
import basilic
import os.path
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-c", "--config", dest="config_filename", default="etc/default.cfg",
                  help="use given config file")
parser.add_option("-i", "--instance_home", dest="instance_home", default=".",
                  help="set the instance home. if given, config file is default.cfg from relative etc/")


(options, args) = parser.parse_args()

basilic.instance_home=os.path.abspath(options.instance_home)
config_filename=options.config_filename
basilic.engine_home=os.path.abspath(basilic.configfile.from_directory)

# Let's start !
os.chdir(instance_home) # Moving to instance dir, so that all files can be relative
print _("Starting %s...") % basilic.version.version_string
print "---"
print _("Engine home : %s") % basilic.engine_home
print _("Instance home : %s") % basilic.instance_home
print _("Configuration file : %s") % config_filename
print "---"

# Read configuration file and get db name
config=basilic.configfile.read_config(config_filename)
db_name=config['global']['database']

print _("Initialising database : %s") % db_name

# Run basilic instance
base=basilic.Basilic(config)

print _("Initialised. Starting servers.")

# Launch servers
if config['http-server']['active']:  # If HTTP Server is active
    import httpserver
    httpserver.Server(base).run()


if config['xmlrpc-server']['active']: # If XML-RPC Server is active
    import xmlrpcserver
    xmlrpcserver.Server(base).run()

print _('Servers launched. Returning to hitchike in the galaxy.')

