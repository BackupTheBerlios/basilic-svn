# ______________________________________________________________________
"""Version Module
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL.

A very simple module for storing versions and copyright informations.

$Id$
Original file is there :
$URL$
"""
# ______________________________________________________________________


import i18n
import time

name="Basilic"
version="0.2"
copyright="2004-%d Olivier Deckmyn" % time.localtime()[0]
project_url="http://basilic.berlios.de/"
see_url=_("see %s") % project_url

version_string="%s - v%s" % (name, version,)
full_copyright="""%s version %s
(c)%s
%s""" % (name, version, copyright, see_url)

