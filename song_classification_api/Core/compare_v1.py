from .DatabaseHandler import * 
import pandas as pd 
from .SongHelper import * 
from  .Sampling_v1 import * 

def find_fingerprint_match(hash, offset, conn=None):
    sql = f"""
        SELECT distinct * 
        FROM TBl_SONG_FINGERPRINTS
        WHERE hash = '{hash}'
    """
    if conn is None: 
        conn = connect()
    result = pd.read_sql(sql, conn)
    conn.close()
    return result




def classify_song(file_path):
    '''
        params: 
        - file_path: string of mp3 file
        
        return a dictionary of song_name with matched fingerprints
    '''
    fingerprints = feature_extraction_from_file(file_path)
    song_ids = { }
    matches = None 
    for fingerprint, offset in fingerprints: 
        result = find_fingerprint_match(fingerprint, offset)
        result['time_delta'] = result['offset'] - int(offset)
#             result = result.drop(['offset'], axis=1)            
        if matches is not  None and len(result) !=0:
            matches = pd.concat([matches, result], axis=0, )
        elif len(result) != 0 and matches is  None: 
            matches = result
            
    if matches is not None and  len(matches) >0:
        matches = matches.drop(['offset'], axis=1).groupby(['song_id','time_delta']).count().sort_values(by='hash', ascending=False).groupby('song_id').head(1)
        matches = matches.reset_index().loc[:, ['song_id', 'time_delta','hash']]
        matches = matches.loc[:, ['song_id', 'hash']]
        dic = {}
        for i in range(  len(matches) ):
            song_name = get_song_name(matches.loc[i, 'song_id'])[0]
            dic[song_name] = matches.loc[i, 'hash']
        return dic