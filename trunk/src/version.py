# ______________________________________________________________________
"""Version Module
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL.

A very simple module for storing versions and copyright informations.

$Id: version.py 10 2005-10-30 16:47:54Z odeckmyn $

Original file is there :
$URL$
"""
# ______________________________________________________________________

# Imports
# NB : This module must not import i18n in order to avoid chicken-eggs problem
import time
import os.path
import basilicglobals

name="Basilic"
version=open(os.path.join(basilicglobals.engine_home,"version.txt")).read()
#version=open("version.txt").read()
copyright="2004-%d Olivier Deckmyn" % time.localtime()[0]
project_url="http://basilic.berlios.de/"
see_url="see %s" % project_url

version_string="%s - v%s" % (name, version,)
full_copyright="""%s version %s
(c)%s
%s""" % (name, version, copyright, see_url)

