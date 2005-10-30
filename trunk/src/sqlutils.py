# ______________________________________________________________________
"""SQL Utils module 
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn
License : GPL.

Smart SQL utility functions.
Only SQLLite is supported by now.

$Id$
Original file is there :
$URL$
"""
# ______________________________________________________________________


import string
import sql


def ForgeCreateTable(trigram):
    """Forges the 'CREATE TABLE' for given trigram"""
    table_name=sql.TABLES[trigram]
    columns=sql.TABLE_DETAILS[trigram]
    struct=[]
    for col in columns:
        struct.append("%s %s %s"% col)
    return "CREATE TABLE %s (%s);" % (table_name, string.join(struct,', '))


def ExecSQL(db, statement, args=None):
    """Executes given statement on given db and returns result"""
    cur=db.cursor()
    statement=string.replace(statement,'?','%s')
    if args is None:
        cur.execute(statement)
    else:
        cur.execute(statement, args)
    return cur.fetchall()

def getRowId(db, table_id):
    return ExecSQL(db, sql.SelectRowId % sql.TABLES[table_id])[-1][0]

