# ______________________________________________________________________
"""Basilic Test Cases.
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL.

All test cases for the Basilic Project.
Each and every function of the framework is supposed to be tested here.
Tests have been written before implementing the code.

Launch tests using Makefile :
$ make test

$Id: test.py 10 2005-10-30 16:47:54Z odeckmyn $

Original file is there :
$URL$
"""
# ______________________________________________________________________



# Remove some warnings for the tests
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, append=1)

import string, os.path, sys
import unittest # Unit tests framework
import basilicglobals

# During test, because it is launched from sandbox/engine, engine_home is "."
basilicglobals.engine_home=os.path.realpath('.')

from basilic import Basilic, User, UserBase, Schema, configfile
from pprint import pprint
import decoder
import i18n


# --------------------------------------------------------------------
# ---- TESTS DATASETS 
# --------------------------------------------------------------------

default_login="user1"
default_password="stupidpassword"
default_fullname="User #1"
default_email="user1@gmail.com"

test_users=[
    (default_login, default_password, default_fullname, default_email),
    ('user2',       default_password, 'User #2',        'user2@gmail.com'),
    ('user3',       default_password, 'User #3',        'user3@gmail.com'),
]

test_bases={
  default_login:
    [
      ('My Bookmarks', 0, 'bookmark', "All my Bookmarks"),
      ('My Public Bookmarks', 1, 'bookmark', "All my Bookmarks"),
      ('My hosts', 0, 'ssh', None),
    ],
  'user2':
    [
      ('My Bookmarks', 0, 'bookmark', "All my Bookmarks"),
      ('My Public Bookmarks', 1, 'bookmark', "All my Bookmarks"),
      ('My hosts', 0, 'ssh', None),
    ]
  }

test_schemas={
    'bookmark': [   'Bookmark',
                    'Collection of Internet Bookmarks',
                    [
                        {
                          'name' : 'title',
                          'label': 'Title of the ressource',
                          'type' : 'string',
                          'mandatory' : 1,
                        },
                        {
                          'name' : 'url',
                          'label' : 'URL',
                          'type' : 'string',
                          'mandatory' : 1,
                        },
                        {
                          'name' : 'comment',
                          'label' : 'Comment',
                          'type' : 'text',
                          'mandatory' : 0,
                        },
                    ]
                ],
    'ssh':      [   "SSH",
                    "Collection of SSH hosts.",
                    [
                        {
                          'name' : 'title',
                          'label': 'Title',
                          'type' : 'string',
                          'mandatory' : 0,
                        },
                        {
                          'name' : 'hostname',
                          'label' : 'Hostname or IP',
                          'type' : 'string',
                          'mandatory' : 1,
                        },
                        {
                          'name' : 'login',
                          'label' : 'Login',
                          'type' : 'string',
                          'mandatory' : 0,
                        },
                        {
                          'name' : 'port',
                          'label' : 'SSH Port',
                          'type' : 'text',
                          'mandatory' : 1,
                          'default' : 22,
                        },
                        {
                          'name' : 'comment',
                          'label' : 'Comment',
                          'type' : 'text',
                          'mandatory' : 0,
                        },
                    ]
                ],

    'password':[   "Passwords",
                    "Secure password storage",
                    [
                        {
                          'name' : 'title',
                          'label': 'Title of the ressource',
                          'type' : 'string',
                          'mandatory' : 1,
                        },
                        {
                          'name' : 'ressource',
                          'label' : 'Ressource',
                          'type' : 'string',
                          'mandatory' : 0,
                        },
                        {
                          'name' : 'login',
                          'label' : 'Login',
                          'type' : 'string',
                          'mandatory' : 0,
                        },
                        {
                          'name' : 'password',
                          'label' : 'Password',
                          'type' : 'string',
                          'mandatory' : 0,
                        },
                        {
                          'name' : 'comment',
                          'label' : 'Comment',
                          'type' : 'text',
                          'mandatory' : 0,
                        },
                    ]
                ],
}

# --------------------------------------------------------------------
# ---- USEFUL TESTS FUNCTIONS 
# --------------------------------------------------------------------


def inject_schemas(basilic, schemas):
    for sch_id in schemas.keys():
        schema=schemas[sch_id]
        title=schema[0]
        description=schema[1]
        schema=schema[2]
        basilic.createSchema(sch_id, title, description, schema)

def inject_users(basilic, users, bases):
    for user in users:
        usr_id=basilic.createUser(*user)                # Creating user
        usr=User(basilic, usr_id, user[1])              # Getting user object
        if bases.has_key(usr.login):
            for userbase in bases[usr.login]:
                usr.createUserBase(*userbase)               # Creating user base


def inject_userbases(basilic, bases):
    for base in bases:
        login=base[0]
#        basilic.


# --------------------------------------------------------------------
# ---- TESTS CASES
# --------------------------------------------------------------------

class TestBasilic(unittest.TestCase):

    def setUp(self):
        config=configfile.default_config
        config['global']['database']=":memory:" # overrides the default DB
        self.basilic=Basilic(config)
        # Build structure
        self.basilic.createDatabaseStructure()
        # Inject Schemas
        inject_schemas(self.basilic, test_schemas)
        # Inject Users
        inject_users(self.basilic, test_users, test_bases)

    def tearDown(self):
        self.basilic.db.close()
        del self.basilic

class TestBasilicCipher(TestBasilic):

    def test_01_cipher(self):
        ciphered_key=self.basilic._createKey(default_password)
        # uncrypt ciphered key, using correct password
        key=self.basilic._decrypt(ciphered_key, default_password)
        # recrypt key, using correct password
        xkey=self.basilic._crypt(key, default_password)
        self.assertEqual(ciphered_key, xkey)

        # uncrypt ciphered key, using incorrect password
        key=self.basilic._decrypt(ciphered_key, "xxx"+default_password)
        # recrypt key, using correct password
        xkey=self.basilic._crypt(key, default_password)
        self.assertNotEqual(ciphered_key, xkey)

        # uncrypt ciphered key, using correct password
        key=self.basilic._decrypt(ciphered_key, default_password)
        # recrypt key, using incorrect password
        xkey=self.basilic._crypt(key, "xxx"+default_password)
        self.assertNotEqual(ciphered_key, xkey)

    def test_01_crypt_decrypt_string(self):
        user=self.basilic.connect(default_login, default_password)
        s="This is my test string, using ascii chars. It's quite easy :-)"
        cs=user.crypt_string(s)
        ucs=user.decrypt_string(cs)
        self.assertEqual(s,ucs)

class TestBasilicUser(TestBasilic):

    def test_01_injection(self):
        list=self.basilic.getUsersDetails()
        self.assertEqual(len(list),len(test_users))
        for id in range(0,len(test_users)): # Testing users
          self.assertEqual(list[id][1], test_users[id][0]) # Check user name
          self.assertEqual(list[id][2], test_users[id][2]) # Check FullName
          self.assertEqual(list[id][3], test_users[id][3]) # Check Email

    def test_02_getUserIdFromLogin(self):
        id=self.basilic.getUserIdFromLogin('user1')
        self.assertEqual(id,1) # good user
        id=self.basilic.getUserIdFromLogin('userINCORRECT')
        self.assertEqual(id,None) # non existing user

    def test_03_getUserId(self):
        id=self.basilic.getUserId('user1', 'X'+default_password)
        self.assertEqual(id, None) # Bad password should not log in
        id=self.basilic.getUserId('userabc', default_password)
        self.assertEqual(id, None) # unknown user should not log in
        id=self.basilic.getUserId('user1', default_password)
        self.assertEqual(id,1) # good user and password
        id=self.basilic.getUserId('user2', default_password)
        self.assertEqual(id,2) # good user and password

    def test_04_connect(self):
        user=self.basilic.connect(default_login, default_password)
        self.assertNotEqual(user, None) # this user should connect
        self.assertEqual(user.uid,1)
        self.assertEqual(user.login,default_login)
        self.assertEqual(user.password,default_password)
        self.assertEqual(user.fullname, default_fullname)
        self.assertEqual(user.email, default_email)

    def test_05_userbases(self):
        user=self.basilic.connect(default_login, default_password)
        usb_ids=user.listUserBases()
        self.assertEqual(len(usb_ids), len(test_bases[default_login])) #Check userbases injection


class TestBasilicSchemas(TestBasilic):

    def test_01_schemas(self):
        schemaIds=self.basilic.getSchemaIds()
        schemaIds.sort()
        self.assertEqual(schemaIds, ['bookmark', 'password', 'ssh'])

        bookmark=self.basilic.getSchema('bookmark')
        self.assertEqual(bookmark.uid,'bookmark')
        self.assertEqual(bookmark.title,'Bookmark')
        self.assertEqual(bookmark.description,'Collection of Internet Bookmarks')

        fieldNames=bookmark.getFieldNames()
        fieldNames.sort()
        self.assertEqual(fieldNames,['comment','title','url'])

        field=bookmark.getField('comment')
        self.assertEqual(field['name'],'comment')
        self.assertEqual(field['label'],'Comment')
        self.assertEqual(field['type'],'text')
        self.assertEqual(field['mandatory'],0)

    def test_01_schemas_userbase(self):
        user=self.basilic.connect(default_login, default_password)
        usb_id=user.listUserBases()[0] # First userbase of default user
        base=user.getUserBase(usb_id)
        self.assertEqual(base.title, 'My Bookmarks')
        self.assertEqual(base.description, 'All my Bookmarks')
        self.assertEqual(base.schema.uid, 'bookmark')

        schema=self.basilic.getSchema('bookmark')
        self.assertEqual(base.schema, schema)


class TestBasilicRessources(TestBasilic):

    def test_01_create(self):
        user=self.basilic.connect(default_login, default_password)
        usb_id=user.listUserBases()[0] # First userbase of default user
        base=user.getUserBase(usb_id) # We should have loaded 'My Bookmarks' base
        res_id=base.createRessource('zope,python','xxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxxxxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxxxxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxxxxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxxxxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxxxxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxxxxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxxxxxtest1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1test1xxx')
        print res_id


class TestBasilicI18N(TestBasilic):

    def _test_loadcatalog(self, code):
        success=True
        try:
            i18n.set_language(code)
        except IOError:
            success=False
        return success

    def test_01_loadcatalogs_fr(self):
        success=self._test_loadcatalog('fr')
        self.assertEqual(success, True) # French catalog is supposed to load

    def test_02_loadcatalogs_en(self):
        success=self._test_loadcatalog('en')
        self.assertEqual(success, True) # English (Default) catalog is supposed to load

    def test_03_loadcatalogs_dummy(self):
        success=self._test_loadcatalog('xx')
        self.assertEqual(success, False ) # Dummy catalog is not supposed to load



class TestBasilicDecoders(TestBasilic):

    def test_01_decode_path(self):
        self.assertEqual(
            decoder.decode_path("/test/"),
            ("test",[])
        )

        self.assertEqual(
            decoder.decode_path("/test"),
            ("test",[])
        )

        self.assertEqual(
            decoder.decode_path("test/"),
            ("test",[])
        )

        self.assertEqual(
            decoder.decode_path("test"),
            ("test",[])
        )

        self.assertEqual(
            decoder.decode_path("/request/a/b/c"),
            ("request",["a","b","c"])
        )

        self.assertEqual(
            decoder.decode_path("/debug/a/b/c"),
            ("debug",["a","b","c"])
        )

        self.assertEqual(
            decoder.decode_path("/debugxxx/a/b/c"),
            ("request",["debugxxx","a","b","c"])
        )

        self.assertEqual(
            decoder.decode_path("/odeckmyn/tags/python+zope"),
            ("request",["odeckmyn","tags","python+zope"])
        )

        self.assertEqual(
            decoder.decode_path(""),
            ("request",[])
        )


    def test_02_detectuserlogin(self):
        basilic=self.basilic
        self.assertEqual(
            decoder._detectuserlogin(basilic,"user1"),
            "user1"
        )

        self.assertEqual(
            decoder._detectuserlogin(basilic,"User1"),
            "user1"
        )

        self.assertEqual(
            decoder._detectuserlogin(basilic,"blablab"),
            None
        )

    def test_03_detectuserbase(self):
        basilic=self.basilic

        self.assertEqual(
            decoder._detectuserbase(basilic,None,"My Public Bookmarks"),
            "My Public Bookmarks"
        )

        self.assertEqual(
            decoder._detectuserbase(basilic,None,"Blablabla"),
            None
        )

        self.assertEqual(
            decoder._detectuserbase(basilic,"user1","My Public Bookmarks"),
            "My Public Bookmarks"
        )

        self.assertEqual(
            decoder._detectuserbase(basilic,"user1","My Bookmarks"),
            "My Bookmarks"
        )

    def test_04_decode_tags(self):
        self.assertEqual(
            decoder.decode_tags(""),
            []
        )

        self.assertEqual(
            decoder.decode_tags("zope"),
            [("AND","zope")]
        )

        self.assertEqual(
            decoder.decode_tags("zope+python"),
            [("AND","zope"),("AND","python")]
        )

        self.assertEqual(
            decoder.decode_tags("+zope+python"),
            [("AND","zope"),("AND","python")]
        )

        self.assertEqual(
            decoder.decode_tags("zope+python-win32"),
            [("AND","zope"),("AND","python"),("NOT","win32")]
        )

        self.assertEqual(
            decoder.decode_tags("-zope"),
            [("NOT","zope")]
        )

        self.assertEqual(
            decoder.decode_tags("zope?python"),
            [("AND","zope"),("OR","python")]
        )


    def test_05_decode_request(self):
        basilic=self.basilic

        tags=[("AND","python"),("AND","zope")] # Supposed translations of "python+zope"

        self.assertEqual(
            decoder.decode_request(basilic,["user1","tags","python+zope"]),
            ("user1",None,tags,"xml")
        )

        self.assertEqual(
            decoder.decode_request(basilic,["user1","tags","python+zope","csv"]),
            ("user1",None,tags,"csv")
        )

        self.assertEqual(
            decoder.decode_request(basilic,["user1","tags","python+zope","xxx"]),
            ("user1",None,tags,"xml")
        )

        self.assertEqual(
            decoder.decode_request(basilic,["odeckmyn","tags","python+zope"]),
            (None,None,tags,"xml")
        )

        self.assertEqual(
            decoder.decode_request(basilic,["My Public Bookmarks","tags","python+zope"]),
            (None,"My Public Bookmarks",tags,"xml")
        )

        self.assertEqual(
            decoder.decode_request(basilic,["user1", "My Bookmarks","tags","python+zope"]),
            ("user1","My Bookmarks",tags,"xml")
        )

        self.assertEqual(
            decoder.decode_request(basilic,[]),
            (None,None,[],"xml")
        )

if __name__ == '__main__':

    suites=[
#        TestBasilicI18N,
        TestBasilicCipher,
#        TestBasilicDecoders,
#        TestBasilicSchemas,
#        TestBasilicRessources,
#        TestBasilicUser,
        ]

    for suite in suites:
        suite=unittest.makeSuite(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)

