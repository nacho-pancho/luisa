# -*- coding: utf-8 -*-
#
import sqlite3 as dbserver 

#
#----------------------------------------------------------------------------------------------------
#
# VARIABLES GLOBALES
#
database='/datos/data/microfilm/microfilm.db'
Port=3306
###
dbcursor={}
dbconn={}
        
def getCursor():
    global dbconn,dbcursor,Host,User,Password,Database
    lcursor={}
    try:
        lcursor=dbconn.cursor()
    except Exception as e:
        #conectar nuevamente y repetir
        print(type(e).__name__)
        print("intentando reconectar....")
        dbconn = dbserver.connect(Database)
        try:
            lcursor=dbconn.cursor()
        except dbserver.OperationalError:
            print("fallo en la reconexión")
            raise dbserver.OperationalError
        else:
            print("...reconectado.")
            return lcursor
    else:
        return lcursor
    
def queryExec(query,cursor=None,params=None,multi=False):
    global dbconn,dbcursor,Host,User,Password,Database
    if cursor is None:
        cursor=dbcursor
    print(query," params:",params," multi:",multi)
    try:
        cursor.execute(query,params,multi)
    except: 
        cursor=getCursor()
        cursor.execute(query)
    return cursor

def callProc(proc,params=[]):
    '''
    SQlite no tiene stored procedures
    '''
    return None

def commit():
    dbconn.commit()

try:
    dbconn = dbserver.connect(database)
except dbserver.Error as e:
    print(e)
    raise dbserver.Error
else:
    dbcursor=getCursor()
