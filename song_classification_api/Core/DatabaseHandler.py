from mysql import connector
from mysql.connector.errors import DatabaseError
from mysql.connector import (connection)
import mysql
from mysql.connector.constants import ClientFlag


#Google Cloud SQL
def connect(cred=dict()):
    # if len(cred) == 0: 
    #     cred['user'] = 'root'
    #     cred['password'] = ''
    #     cred['host'] = '34.87.117.237'
    #     cred['database'] = 'song_classification_api'
    config = {
        'user': 'root',
        'password': 'Tkx$3MI*ThCi',
        'host': '34.87.117.237',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'ssl/server-ca.pem',
        'ssl_cert': 'ssl/client-cert.pem',
        'ssl_key': 'ssl/client-key.pem'
    }
    try:
        cnx = mysql.connector.connect(**config)
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


#local
# def connect(cred=dict()):
#     if len(cred) == 0: 
#         cred['user'] = 'root'
#         cred['password'] = ''
#         cred['host'] = '127.0.0.1'
#         cred['database'] = 'song_classification_api'
#     try:
#         cnx = connection.MySQLConnection(user=cred['user'], password=cred['password'], host=cred['host'], database=cred['database'])
#         return cnx
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Something is wrong with your user name or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#     else:
#         cnx.close()