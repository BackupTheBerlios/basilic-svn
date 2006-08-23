# ______________________________________________________________________
"""Basilic Main Module
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL

Main Basilic module. Contains all the logic.

$Id: basilic.py 10 2005-10-30 16:47:54Z odeckmyn $

Original file is there :
$URL$
"""
# ______________________________________________________________________

# Major globals

# Imports
import basilicglobals
import sqlite, sql
import random, string, md5, rijndael, base64
import configfile, version
import i18n

__version__=version.version_string

schema_field_types=[
    'string',
    'int',
    'boolean',
    'text',
    ]

formats=[
    "xml",
    "rss",
    "atom",
    "csv",
    "python",
    ]

class Basilic:
    """Singleton class handling everything about the Basilic system. Use connect to get a user object."""

    def __init__(self, config=None):
         """Using the given config file, opens the database at initialisation time"""
         if not config: # if no config object given, use the default config file
             config=configfile.read_config()
         self.config=config
         self.db = sqlite.connect(config['global']['database'])
         self.version=version #version, the module
         i18n.set_language(config['global']['language'])
         self._schemas_cache={} # A schema cache, to keep one instance in memory
         self._userbase_cache={} # A userbase cache. XXX TODO : USE A FIFO HERE FOR MEMORY SAVE

    # End-User Actions
    def connect(self, login, password):
        """Returns an user object, to interact with system"""
        usr_id=self.getUserId(login, password)
        if usr_id is not None:
            return User(self, usr_id, password)
        else:
            return None

    def getUsersDetails(self):
        """Returns a list of all user details (including email, fullname, etc.), but passwords"""
        return self.ExecSQL(sql.SelectUsersDetails)

    def getUserDetails(self, usr_id):
        """Returns all details (including email, fullname, etc.), but passwords for the given cus_id"""
        return self.ExecSQL(sql.SelectUser, usr_id)

    def getUserId(self, login, password):
        """Returns usr_id if given login/password is correct. Returns None else."""
        result=self.ExecSQL(sql.SelectUserPassword, (login,password))
        if len(result)==0:
            return None
        else:
            return result[0][0]

    def getUserIdFromLogin(self, login):
        """Returns usr_id if given login is correct. Returns None else."""
        result=self.ExecSQL(sql.SelectUserLogin, login)
        if len(result)==0:
            return None
        else:
            return result[0][0] # is usr_id

    def getPublicUserBase(self, usb_title):
        """Returns usb_title if at least one public userbase exists with
        a title==usb_title"""
        result=self.ExecSQL(sql.SelectPublicUserBaseFromTitle, usb_title)
        if len(result)==0:
            return None
        else:
            return usb_title

    def getUserBaseForLogin(self, usb_title, usr_login):
        """Returns usb_title if at least one public or private userbase exists
        with a title==usb_title for user whose login is usr_login"""
        result=self.ExecSQL(sql.SelectUserBaseFromTitleForLogin, (usb_title, usr_login))
        if len(result)==0:
            return None
        else:
            return usb_title

    def _createKey(self, password):
        """Returns the initial secret key, ciphered using password"""
        alpha=string.ascii_letters+"0123456789"
        random.seed()                                   # Initialise random machine
        key=''
        for i in range(0,128):                          # Key is 128*8=1024 bits long
            key+=random.choice(alpha)
        mdkey=md5.md5(key).hexdigest()
        ciphered_key=self._crypt(mdkey, password)
        return ciphered_key

    def _crypt(self, s, key):
        """Returns the s string encrypted with key"""
        mdkey=md5.md5(key).hexdigest()
        result=rijndael.encrypt(mdkey,s)
        return base64.encodestring(result)

    def _decrypt(self, s, key):
        """Returns the s string decrypted with key"""
        mdkey=md5.md5(key).hexdigest()
        s=base64.decodestring(s)
        return rijndael.decrypt(mdkey,s)

    def createUser(self, login, password, fullname, email):
        """Creates a new user. Raises an exception if users already exists. Returns usr_id."""
        # First create the user secret key
        ciphered_key=self._createKey(password)
        # Insert user into DB
        self.ExecSQL(sql.InsertUser, (login.lower(), password, fullname, email.lower(), ciphered_key) )
        self.db.commit()
        usr_id=sql.getRowId(self.db,'usr')
        # Returns new user's id
        return usr_id

    def createSchema(self, uid, title, description, schema):
        """Creates a new schema. Raises an exceptions if a schema with same id already exists. Returns sch_id."""
        self.ExecSQL(sql.InsertSchema, (uid, title, description, str(schema)))
        self.db.commit()
        return uid

    def getSchema(self, uid):
        """Return schema object for given schema uid"""
        if not uid in self._schemas_cache.keys():
            schema=Schema(self, uid)
            self._schemas_cache[uid]=schema
        return self._schemas_cache[uid]

    def getUserBase(self, user, uid):
        """Return user base object for given base uid"""
        if not uid in self._userbase_cache.keys():
            base=UserBase(user, uid)
            self._userbase_cache[uid]=base
        return self._userbase_cache[uid]



    # Internal methods
    def createDatabaseStructure(self):
        """Creates the database structure. """
        self.ExecSQL(sql.CreateTables)

    # Utility functions
    def ExecSQL(self, statement, args=None):
        """A simple wrapper to sql.ExecSQL method"""
        return sql.ExecSQL(self.db, statement, args)

    def getSchemaIds(self):
        """Returns the lists of available schemas ids"""
        ids=self.ExecSQL(sql.SelectSchemaIds)
        result=[]
        for id in ids:
            result.append(id[0])
        return result

    def getSchemas(self):
        """Returns the lists of available schemas and details"""
        return self.ExecSQL(sql.SelectSchemas)


class User:

    def __init__(self, basilic, uid, password):
        self.basilic=basilic
        self.uid=uid
        self.password=password
        self.login=None
        self.fullname=None
        self.email=None
        self._loadFromDB()
        self._key=self._loadKeyFromDB()   # kind of a cache
        self._mdkey=md5.md5(self._key).hexdigest()   # md5ized

    def _loadFromDB(self):
        """Loads all details of user from the DB"""
        x=self.basilic.ExecSQL(sql.SelectUser,(self.uid,))
        if len(x)==0:
            raise _("User %s not found in database") % self.uid
        else:
            x=x[0]
        self.login=x[1]
        self.fullname=x[2]
        self.email=x[3]

    def _loadKeyFromDB(self):
        """Loads key from the DB"""
        x=self.basilic.ExecSQL(sql.SelectUserKey,(self.uid,))
        if len(x)==0:
            raise _("User %s not found in database") % self.uid
        else:
            x=x[0]
        key=self.basilic._decrypt(x[0], self.password)
        return key

    def listUserBases(self):
        """Returns all base ids for this user"""
        bases=self.basilic.ExecSQL(sql.SelectUserBasesForUser,(self.uid))
        result=[]
        for base in bases:
            result.append(base[0])
        return result

    def listUserBaseDetails(self):
        """Returns all base details for this user"""
        bases=self.basilic.ExecSQL(sql.SelectUserBasesForUser,(self.uid))
        return bases

    def getUserBase(self, uid):
        """Connects to given user base"""
        return self.basilic.getUserBase(self,uid)

    def changePassword(self, password):
        """Set new password for user. Converts ciphered key."""
        # TODO : invalidate current cached uncrypted key
        pass 

    def createUserBase(self, title, isPublic, schema_uid, description=""):
        """Creates a new UserBase for the current user, given its details. Returns a UserBase object"""
        db=self.basilic.db
        self.basilic.ExecSQL(sql.InsertUserBase, (self.uid, isPublic, schema_uid, title, description) )
        db.commit()
        usb_id=sql.getRowId(db,'usb')
        return UserBase(self, usb_id)

    def crypt_string(self, s):
        """Crypt given string, using current user password. Result is base64 
        version of resulting binary string"""
        l=len(s)
        s2=[] # split s into s2, made of 16 chars
        for i in range(0,l/16+1):
            ss=(s[16*i:16*(i+1)]).ljust(16) #substring
            s2.append(ss)

        cs2=[] # is ciphered s2
        for x in s2:
            y=rijndael.encrypt(self._mdkey,x) # crypt string, remove trailing \n
            cs2.append(y)

        cs=string.join(cs2,'') # cs is a string, joined from cs2
        cs=base64.encodestring(cs)   # base64 yourself
        return cs

    def decrypt_string(self, s):
        """Decrypt given string, using current user password"""
        s=base64.decodestring(s) # s was base64ed
        l=len(s)
        s2=[]
        for i in range(0,l/16):
            x=s[i*16:(i+1)*16]
            x=rijndael.decrypt(self._mdkey,x)
            s2.append(x) # uncipher

        us=string.join(s2,'') # rejoin all
        us=us.rstrip()
        return us
        


class UserBase:

    def __init__(self, user, uid):
        """Initialize an UserBase given the user object and the userbase id"""
        self.user=user
        self.basilic=user.basilic
        self.uid=uid
        self.title=None
        self.isPublic=None
        self.schema=None
        self.schema_uid=None
        self.description=None
        self._loadFromDB()

    def _loadFromDB(self):
        """Loads all details of userbase from the DB"""
        x=self.basilic.ExecSQL(sql.SelectUserBaseDetails,(self.uid,))
        if len(x)==0:
            raise _("UserBase %s not found in database") % self.uid
        else:
            x=x[0]

        # Fields : usb_id, usr_id, usb_public, sch_id, usb_title, usb_description 

        self.isPublic=x[2]
        self.schema_uid=x[3]
        self.title=x[4]
        self.schema=self.basilic.getSchema(self.schema_uid)
        self.description=x[5]

    def getSchema(self):
        """Returns schema of the base"""
        return self.schema

    def getRessourceIds(self,tags=None):
        """Returns the list of ressources Ids for current user. If tags is provided, the list is limited to the items matching given tags."""
        pass

    def getRessource(self, uid):
        """Returns the value for id. Content is unciphered using current user password"""
        pass

    def createRessource(self, tags, value):
        """Creates a new ressource, cipher the value and insert in DB. Returns 
        ressource UID"""
        c_value=self.user.crypt_string(str(value))
        c2=self.user.decrypt_string(c_value)
        db=self.basilic.db #res_id, usb_id, res_tags, res_value
        self.basilic.ExecSQL(sql.InsertRessource, (self.uid, tags, c_value) )
        db.commit()
        usb_id=sql.getRowId(db,'usb')
        


# This is stolen from mxTools
# Thanx to eGenix for this tip
def reval(codestring,locals=None,eval=eval):
    """ Restricted execution eval()."""
    if locals is not None:
        return eval(codestring,{'__builtins__':{}},locals)
    else:
        return eval(codestring,{'__builtins__':{}})


class Schema:

    def __init__(self, basilic, uid):
        self.basilic=basilic
        self.uid=uid
        self.title=None
        self.description=None
        self.schema=None
        self.fieldNames=[] # Names of fields, ordered
        self.fields={}     # Fields (structured)
        self._loadFromDB()

    def _loadFromDB(self):
        """Loads all details of schema from the DB"""
        x=self.basilic.ExecSQL(sql.SelectSchemaDetails,(self.uid,))
        if len(x)==0:
            raise _("Schema %s not found in database") % self.uid
        else:
            x=x[0]
        self.title=x[1]
        self.description=x[2]
        self.schema=self._interpret(x[3])
        self._digestSchema()

    def _digestSchema(self):
        """Gets all informations from schema structure, and inject into fields
        structure"""
        self.fieldNames=[]
        self.fields={}
        for field in self.schema:
            fieldName=field['name']
            self.fieldNames.append(fieldName)
            self.fields[fieldName]=field

    def _interpret(self, schema_string):
        """Interprets the schema string into a schema object. Based on python eval. 
        In case of any error in interpreting, None is returned."""
        try:
            return reval(schema_string)
        except:
            return None

    def getFieldNames(self):
        """Returns all fields names of current schema, as a list of strings"""
        return self.fieldNames
    
    def getField(self,fieldName):
        """Returns the field of given name"""
        return self.fields[fieldName]
        
        
