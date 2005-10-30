# ______________________________________________________________________
"""Module API
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn

Defines the official API and constants for use from external programs or
plugins.
See  doc/api.txt

$Id: api.py 10 2005-10-30 16:47:54Z odeckmyn $
"""
# ______________________________________________________________________

import basilic

operations=[
    "request",
    "test",
    "debug",
    ]

operators=[
    "+",
    "-",
    "?",
    ]

def operation_test(basilic,stream,params):
    stream.write('OK\n')
    stream.write('---\n')
    stream.write(basilic.version.full_copyright)

def operation_request(basilic,stream,userlogin=None,userbase=None,tags=[],format="xml"):
    stream.write('<!DOCTYPE xml PUBLIC>')
    stream.write("<yes>no</yes>")