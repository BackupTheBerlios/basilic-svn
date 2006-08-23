# ______________________________________________________________________
"""SQL module 
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL.

Handles everything about SQL.
Only SQLLite is supported by now.

$Id: sql.py 10 2005-10-30 16:47:54Z odeckmyn $

Original file is there :
$URL$
"""
# ______________________________________________________________________


import string
from sqlutils import *

# CREATE TABLES

TABLES={
    "usr" : "TM_USR_Users",
    "usb" : "TM_USB_UserBases",
    "sch" : "TM_SCH_Schemas",
    "res" : "TM_RES_Ressources",
}

TABLE_DETAILS={
    "usr" : [
             ("usr_id",         "integer",  "PRIMARY KEY"),
             ("usr_login",      "varchar",  "NOT NULL UNIQUE"),
             ("usr_password",   "varchar",  "NOT NULL"),
             ("usr_fullname",   "varchar",  ""),
             ("usr_email",      "varchar",  ""),
             ("usr_key",        "varchar",  "NOT NULL"),
             ("usr_enabled",    "boolean",  "NOT NULL"),
            ],

    "usb" : [
             ("usb_id",         "integer",  "PRIMARY KEY"),
             ("usr_id",         "varchar",  "NOT NULL"),
             ("usb_public",     "boolean",  "NOT NULL"),
             ("sch_id",         "varchar",  "NOT NULL"),
             ("usb_title",      "varchar",  "NOT NULL"),
             ("usb_description","varchar",  ""),
            ],

    "sch" : [
             ("sch_id",         "varchar",  "PRIMARY KEY"),
             ("sch_title",      "varchar",  "NOT NULL"),
             ("sch_description","varchar",  ""),
             ("sch_schema",     "varchar",  "NOT NULL"),
            ],

    "res" : [
             ("res_id",         "integer",  "PRIMARY KEY"),  # Unique id
             ("usb_id",         "integer",  "NOT NULL"),     # Corresponding UserBase
             ("res_tags",       "varchar",  ""),             # Tags used, comma separated
             ("res_value",      "varchar",  "NOT NULL"),     # Ciphered dictionary, according to schema
            ],

}


CreateTableUsers=ForgeCreateTable("usr")

CreateTableUserBases=ForgeCreateTable("usb")

CreateTableSchemas=ForgeCreateTable("sch")

CreateTableRessources=ForgeCreateTable("res")

CreateTables=string.join( [CreateTableUsers, CreateTableUserBases, CreateTableSchemas, CreateTableRessources],'\n')

# DROP TABLES

DropTables=""
for table in TABLES.keys():
    DropTables+="DROP TABLE %s;\n" % TABLES[table]

# GENERAL SQL

SelectRowId="SELECT ROWID FROM %s"

# USERS TABLE

SelectUsers="SELECT usr_id, usr_login FROM %s WHERE usr_enabled=1 ORDER BY usr_login" % TABLES['usr']

SelectUsersDetails="SELECT usr_id, usr_login, usr_fullname, usr_email FROM %s WHERE usr_enabled=1 ORDER BY usr_id" % TABLES['usr']

SelectAllUsers="SELECT usr_id, usr_login FROM %s ORDER BY usr_login" % TABLES['usr']

SelectDisabledUsers="SELECT usr_id, usr_login FROM %s WHERE usr_enabled=0 ORDER BY usr_id" % TABLES['usr']

SelectUser="SELECT usr_id, usr_login, usr_fullname, usr_email FROM %s WHERE usr_id=?" % TABLES['usr']

SelectUserLogin="SELECT usr_id, usr_login, usr_fullname, usr_email FROM %s WHERE usr_login=?" % TABLES['usr']

SelectUserKey="SELECT usr_key FROM %s WHERE usr_id=?" % TABLES['usr']

SelectUserPassword="SELECT usr_id FROM %s WHERE usr_login=? AND usr_password=?" % TABLES['usr']

InsertUser="INSERT INTO %s (usr_login, usr_password, usr_fullname, usr_email, usr_key, usr_enabled) VALUES (?, ?, ? ,? ,?, 1)" % TABLES['usr']

UpdateUserEnabled="UPDATE %s SET usr_enabled=? WHERE usr_id=?" % TABLES['usr']

# USERBASES TABLE

InsertUserBase="INSERT INTO %s (usr_id, usb_public, sch_id, usb_title, usb_description) VALUES (?, ?, ? ,? ,?)" % TABLES['usb']

SelectUserBasesForUser="SELECT usb_id, usr_id, usb_public, sch_id, usb_title, usb_description FROM %s WHERE usr_id=?" % TABLES['usb']

SelectUserBasesForUserAndSchema="SELECT usb_id, usr_id, usb_public, sch_id, usb_title, usb_description FROM %s WHERE usr_id=? AND sch_id=?" % TABLES['usb']

SelectUserBaseDetails="SELECT usb_id, usr_id, usb_public, sch_id, usb_title, usb_description FROM %s WHERE usb_id=?" % TABLES['usb']

SelectPublicUserBaseFromTitle="SELECT usb_id, usr_id, usb_public, sch_id, usb_title, usb_description FROM %s WHERE usb_title=? AND usb_public=1" % TABLES['usb']

SelectUserBaseFromTitleForLogin="SELECT usb_id, %s.usr_id, usb_public, sch_id, usb_title, usb_description FROM %s, %s WHERE usb_title=? AND usr_login=? AND %s.usr_id=%s.usr_id" % (TABLES['usb'], TABLES['usb'], TABLES['usr'], TABLES['usb'], TABLES['usr'] )

# SCHEMA TABLE

InsertSchema="INSERT INTO %s (sch_id, sch_title, sch_description, sch_schema) VALUES (?,?,?,?)" % TABLES['sch']

SelectSchemaDetails="SELECT sch_id, sch_title, sch_description, sch_schema FROM %s WHERE sch_id=?" % TABLES['sch']

SelectSchemas="SELECT sch_id, sch_title, sch_description, sch_schema FROM %s ORDER BY sch_id" % TABLES['sch']

SelectSchemaIds="SELECT sch_id FROM %s ORDER BY sch_id" % TABLES['sch']

# RESSOURCE TABLE

InsertRessource="INSERT INTO %s (res_id, usb_id, res_tags, res_value) VALUES (?,?,?,?)" % TABLES['res']

SelectRessourceDetails="SELECT res_id, usb_id, res_tags, res_value FROM %s WHERE res_id=?" % TABLES['res']

SelectRessources="SELECT res_id, usb_id, res_tags, res_value FROM %s ORDER BY res_id" % TABLES['res']

SelectRessourceIds="SELECT res_id FROM %s ORDER BY res_id" % TABLES['res']

