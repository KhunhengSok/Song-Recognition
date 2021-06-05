from pydub import AudioSegment
import pandas as pd 
import librosa 
from .Sampling_v1 import * 
from .compare_v1 import * 
from .SongHelper import * 


def concat_song(dir, filenames, destination_file_path):
    '''
        params:
            - files_path: list of file path
    '''
    song = None
    for name in filenames: 
        file = os.path.join(dir, name)
        if file.endswith('.mp3'):
                sound = AudioSegment.from_mp3(file)
                if song is None: 
                    song = sound 
                else: 
                    song = song + sound 
        # song.export(destination_file_path, format="mp3")
        song.export(os.path.join(dir , 'generated.mp3'), format="mp3")

    return destination_file_path


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