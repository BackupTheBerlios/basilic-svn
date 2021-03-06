# ______________________________________________________________________
"""Module i18n
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL

Handles everything about internationalisation of Basilic Project.

$Id: i18n.py 10 2005-10-30 16:47:54Z odeckmyn $

Original file is there :
$URL$
"""
# ______________________________________________________________________

import os.path, sys, locale
import basilicglobals
import basilic

# Some constants
domain="basilic"
localesDir = os.path.join(basilicglobals.engine_home, 'locales')
print localesDir

# Trying to import gettext, if installed.
try:
    import gettext
    from gettext import gettext as _
    # Install internationalization stuff and define _()
    gettext.install( domain, unicode=True )
except ImportError:
    import sys
    print >> sys.stderr, ( "You don't have gettext module, no " \
                           "internationalization will be used." )
    # define _() so program will not fail
    import __builtin__
    __builtin__.__dict__[ "_" ] = lambda x: x


def set_language(lang_code):
    """Set the applications language."""
    if sys.modules.has_key('gettext'): # If gettext was installed
        #print "Installing translation for domain=%s, localesDir=%s, language=%s" % (domain, localesDir, lang_code)
        gettext.translation(domain,localesDir,languages=[lang_code]).install()

