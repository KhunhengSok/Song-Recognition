from  .DatabaseHandler import * 
from mutagen.easyid3 import EasyID3 
import mutagen 
import os 
import pandas as pd 


def get_song_meta(file_path):
    song_name, artist, album = '', '', ''
    try: 
        metadata = EasyID3(file_path)
    except mutagen.id3.ID3NoHeaderError:
        metadata = mutagen.File(file_path, easy=True)
        metadata.add_tags()
    if len(metadata) >0:
        song_name = metadata.get('Title', [''])[0]
        artist = metadata.get('Contributing artists', [''])[0]
        album = metadata.get('Album', [''])[0]
    else: 
        song_name = os.path.basename(file_path)
    
    dict = {
        'song_name': song_name,
        'artist':    artist,
        'album':     album
    }
    return dict

def get_song(id):
    sql = f"""
        SELECT  *
        FROM TBL_SONGS 
        WHERE id = {id}
    """
    cxn = connect()
    cursor = cxn.cursor()
    cursor.execute(sql)
    return cursor.fetchone()

   
    
def is_song_exists(song_name='', file_location=''):
    song_name = preprocess_string(song_name)
    file_location = preprocess_string(file_location)
    song_name = '%' + song_name.replace(' ', '%') + '%'
    file_location = '%' +  file_location.replace(' ', '%') +'%'
    sql = f"""
        SELECT *
        FROM TBL_SONGS 
        WHERE song_name like '{song_name}'
        OR file_location like '{file_location}'
    """
#     print(sql)
    conn = connect()
    return pd.read_sql(sql, conn).shape[0] >0

def preprocess_string(string):
    return   string.replace("'", "''")
    
def get_song_id(song_name='', file_location=''):
    song_name = '%' + song_name.replace(' ', '%') + '%'
    file_location = '%' +  file_location.replace(' ', '%') +'%'
    sql = f"""
        SELECT  id
        FROM TBL_SONGS 
        WHERE name like '{song_name}'
        OR file_location like '{file_location}'
        order by id
        limit 1
    """
    cxn = connect()
    cursor = cxn.cursor()
    cursor.execute(sql)
    return cursor.fetchone()[0]
    
    

def get_song_name(id):
    sql = f"""
        SELECT  name
        FROM TBL_SONGS 
        WHERE id = {id}
    """
    cxn = connect()
    cursor = cxn.cursor()
    cursor.execute(sql)
    return cursor.fetchone()

