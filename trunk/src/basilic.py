# ______________________________________________________________________
"""Basilic Main Module
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn

Main Basilic module. Contains all the logic.

$Id$
"""
# ______________________________________________________________________



import sqlite, sql
import random, string, md5, rijndael, base64
import configfile, version
import i18n

__version__=version.version_string
engine_home=None
instance_home=None

schemas_types=[
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
        self.loadFromDB()

    def loadFromDB(self):
        """Loads all details of user from the DB"""
        x=self.basilic.ExecSQL(sql.SelectUser,(self.uid,))
        if len(x)==0:
            raise _("User %s not found in database") % self.uid
        else:
            x=x[0]
        self.login=x[1]
        self.fullname=x[2]
        self.email=x[3]

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

    def connect(self, basename):
        """Connects to given base"""
        pass

    def changePassword(self, password):
        """Set new password for user. Converts ciphered key."""
        pass

    def createUserBase(self, title, isPublic, schema_name, description=""):
        """Creates a new UserBase for the current user, given its details. Returns a UserBase object"""
        db=self.basilic.db
        self.basilic.ExecSQL(sql.InsertUserBase, (self.uid, isPublic, schema_name, title, description) )
        db.commit()
        usb_id=sql.getRowId(db,'usb')
        return UserBase(self, usb_id)



class UserBase:

    def __init__(self, user, uid):
        """Initialize an UserBase given the user object and the userbase id"""
        self.user=user
        self.basilic=user.basilic
        self.uid=uid
        self.title=None
        self.isPublic=None
        self.schema=None
        self.schema_name=None
        self.description=None
        self.loadFromDB()

    def loadFromDB(self):
        """Loads all details of userbase from the DB"""
        x=self.basilic.ExecSQL(sql.SelectUserBaseDetails,(self.uid,))
        if len(x)==0:
            raise _("UserBase %s not found in database") % self.uid
        else:
            x=x[0]
        self.title=x[1]
        self.isPublic=x[2]
        self.schema_name=x[3]
        self.description=x[4]

    def getSchema(self):
        """Returns schema of the base"""
        pass

    def getRessourceIds(self,tags=None):
        """Returns the list of ressources Ids for current user. If tags is provided, the list is limited to the items matching given tags."""
        pass

    def getRessource(self, uid):
        """Returns the value for id. Content is unciphered using current user password"""
        pass


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
        self.loadFromDB()

    def loadFromDB(self):
        """Loads all details of schema from the DB"""
        x=self.basilic.ExecSQL(sql.SelectSchemaDetails,(self.uid,))
        if len(x)==0:
            raise _("Schema %s not found in database") % self.uid
        else:
            x=x[0]
        self.title=x[1]
        self.description=x[2]
        self.schema=self.interpret(x[3])
        self.schema_names=[]
        for item in self.schema:
            self.schema_names.append(item['name'])

    def interpret(self, schema_string):
        """Interprets the schema string into a schema object. Based on python eval. 
        In case of any error in interpreting, None is returned."""
        try:
            return reval(schema_string)
        except:
            return None
