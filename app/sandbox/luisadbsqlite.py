# -*- coding: utf-8 -*-
#
import sqlite3 as dbserver 

#
#----------------------------------------------------------------------------------------------------
#
# VARIABLES GLOBALES
#

def getConnection(dbfile='luisa.db'):
    if getConnection.dbconn is None:
        getConnection.dbconn = dbserver.connect(dbfile)
    return getConnection.dbconn
getConnection.dbconn = None


def getCursor():
    dbconn = getConnection()
    getCursor.dbcursor = dbconn.cursor()
    return getCursor.dbcursor
getCursor.dbcursor = None

def query(query):
    print(query)
    cursor = getCursor()
    cursor.execute(query)
    return cursor

def queryExec(_query,cursor=None,params=None,multi=False):
    return query(_query)


def commit():
    dbconn = getConnection()
    dbconn.commit()

