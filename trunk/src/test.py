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

import string, os, os.path, sys
import unittest # Unit tests framework
import basilicglobals

#basilicglobals.engine_home=os.getcwd()
basilicglobals.engine_home="."

print "Assuming test are ran from %s" % basilicglobals.engine_home

#sys.exit(1)


import basilic


from basilic import Basilic, User, UserBase, Schema, configfile
from pprint import pprint
import decoder

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

    'passwords':[   "Passwords",
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
        schemas=self.basilic.getSchemaIds()
        for sch_id in schemas:
            schema=Schema(self.basilic, sch_id)
            print schema.schema_names


class TestBasilicI18N(TestBasilic):

    def test_01_loadcatalogs(self):
        pass

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
        TestBasilicI18N,
        TestBasilicCipher,
        TestBasilicDecoders,
        TestBasilicSchemas,
        TestBasilicUser,
        ]

    for suite in suites:
        suite=unittest.makeSuite(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)

