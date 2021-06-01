from mysql import connector
from mysql.connector.errors import DatabaseError
from mysql.connector import (connection)
import mysql

def connect(cred=dict()):
    if len(cred) == 0: 
        cred['user'] = 'root'
        cred['password'] = ''
        cred['host'] = '127.0.0.1'
        cred['database'] = 'song_classification_api'
    try:
        cnx = connection.MySQLConnection(user=cred['user'], password=cred['password'], host=cred['host'], database=cred['database'])
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()