DROP TABLE TM_USR_Users;
CREATE TABLE TM_USR_Users (usr_id integer PRIMARY KEY, usr_login varchar NOT NULL UNIQUE, usr_password varchar NOT NULL, usr_fullname varchar, usr_email varchar);

DROP TABLE TM_USB_UserBases;
CREATE TABLE TM_USB_UserBases (usb_id integer PRIMARY KEY, usr_id varchar NOT NULL, usb_public boolean NOT NULL, sch_id varchar NOT NULL, usb_title varchar NOT NULL, usb_description varchar);

DROP TABLE TM_SCH_Schemas;
CREATE TABLE TM_SCH_Schemas (sch_id varchar PRIMARY KEY, sch_title varchar NOT NULL, sch_description varchar, sch_schema varchar NOT NULL);

DROP TABLE TM_RES_Ressources;
CREATE TABLE TM_RES_Ressources (res_id integer PRIMARY KEY, usb_id integer NOT NULL, res_tags varchar, res_value varchar NOT NULL);

