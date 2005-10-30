# ______________________________________________________________________
"""Module Decoder
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn

This modules decodes string sent to API into operations and parameters
Also handles the logic of decoding requests and so
See  doc/api.txt

$Id:$
"""
# ______________________________________________________________________

import basilic,api
import string

formats=basilic.formats
operations=api.operations
sql_operators=[
    "AND",
    "NOT",
    "OR",
    ]
operators=api.operators

# Building the operators_translator dictionnary
operators_translator={}
i=0
for op in operators:
    operators_translator[op]=sql_operators[i]
    i+=1

# --- DECODERS -------------------------------------------------------------

def decode_path(path, separator="/"):
    """Decode an URL path. Extracts the operation and the parameters (into
    a tuple)"""
    if path and path[0]==separator: # Remove any leading separator
        path=path[1:]
    s=path.split(separator)
    operation=s[0].lower()
    if operation in operations:
        parameters=s[1:]
    else: # request is default and implicit
        operation="request"
        parameters=s
    if parameters==[""]:
        parameters=[]

    paramaters=map(string.lower,parameters)
    
    return (operation, parameters)

def decode_tags(tags):
    """Decodes the tag string, from something like +python-win32+!zop*, into 
    something like [("and","python"), ("not","win32"), ("and not","zop*")] 
    which means "where tags is python, but not win32, and start with zop"
    """
    if not tags:        # the nil case
        return [] 

    # We do work in lowercase
    tags=tags.lower()
    # We do remove any blank, space, tab or linefeed:
    tags=string.join(tags.split())
    # If we have no operator in front, insert the default one : "+"
    if not tags[0] in operators:
        tags="+"+tags
    
    for operator in operators:
        tags=tags.replace(operator, " %s " % operators_translator[operator])

    res=tags.split(" ")
    
    if res:
        del res[0] # Remove first empty element, if any
    
    result=[]
    for i in range(0,len(res)/2):
        result.append((res[i*2],res[i*2+1]))
    
    return result

def _detectuserlogin(basilic,userlogin):
    """Returns the userlogin string if given userlogin exists ; returns None
    else"""
    # Let's lower things
    if userlogin:
        userlogin=userlogin.lower()

    if not basilic.getUserIdFromLogin(userlogin):
        userlogin=None
    return userlogin

def _detectuserbase(basilic,userlogin,userbase):
    """Returns the userbase string. If userlogin is None, we look for any public
    userbase with this name. If userlogin is given, we only look for private 
    or public userbase for this userlogin. Else returns None."""
    # Let's lower things
    if userlogin:
        userlogin=userlogin.lower()
        
    if userlogin:
        userbase=basilic.getUserBaseForLogin(userbase, userlogin)
    else:
        userbase=basilic.getPublicUserBase(userbase)
    return userbase

def decode_request(basilic,params):
    """Decodes the given params tuple for a request, into a tuple :
    (userlogin,userbase,tags,format) where :
    - userlogin : specifies that the request is only for given user - None if not present
    - userbase : specifies that the request is restricted the userbase(s) named "userbase" - None else.
    - tags : list of tags, if specified. A tag is a tuple (operator, tag). Where operator is the operator
    to apply to search ("OR", "AND", "LIKE" for example). If no tags founds, returns an empty list.
    See doc/api.txt for more.
    """
    userlogin=userbase=None
    tags=[]
    format="xml"
    
    if params and (params[-1] in formats): # Format is the latest parameter, if exists
        format=params.pop(-1)

    has_tags="tags" in params # Handle tags
    if has_tags: # If tags marker is present, we know we have only two solutions for userlogin/userbase
        tags_index=params.index("tags")
        tags=params.pop(tags_index+1) # We consume tags values
        del params[tags_index]     # We remove the tags marker, useless now
        tags=decode_tags(tags)
    else:
        tags=[]

    # Now we only have nothing, userbase, userlogin or userbase and userlogin
    if len(params)>0:
        userlogin=_detectuserlogin(basilic,params[0])
        if userlogin:
            params.pop(0)
    
    if len(params)>0:
        userbase=_detectuserbase(basilic,userlogin,params[0])
        if userbase:
            params.pop(0)
            
    # One might still have unconsumed elements here
    # We have decided to be silent about them
    return (userlogin,userbase,tags,format)
    
