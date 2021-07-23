import librosa
import librosa.display
import matplotlib.pyplot as plt
import glob 
import numpy as np
import pandas as pd
import matplotlib.mlab as mlab
from scipy.signal import find_peaks

from scipy.fft import fft, fftfreq, rfft, rfftfreq, irfft, ifft
from scipy.io import wavfile
import scipy

import sys
# sys.path.append("..") # Adds higher directory to python modules path.

from .Dejavu.Fingerprinting import * 
import io, json

import queue
import os
import re

from mysql import connector
from mysql.connector.errors import DatabaseError
from mysql.connector import (connection)
import mysql
from time import time
import random

from mutagen.easyid3 import EasyID3
import mutagen


# version 2 
upper_freq = 5000
n_fft = 1024
amp_min = 5
sr = 44100


        
def preprocess(y, sr, n_fft=1024, hop_length=None, waveplot=False,  spectrogram=False):
    new_sr = 11025
    if hop_length is None: 
        hop_length=  n_fft//4
    #filtering frequency higher than 5KHz
    
    ##apply fft
    yf = rfft(y, workers=-1)
    xf = rfftfreq(len(y), 1/sr)
    upper = upper_freq* int(yf.shape[0]/new_sr /2 )
    yf[upper:] = 0
    y_recover = irfft(yf)
    
    #Downsampling 
    new_y = librosa.core.resample(y_recover, sr,  new_sr)
    
    if waveplot: 
        librosa.display.waveplot(new_y, sr)
    
    if spectrogram: 
        librosa.display.specshow(librosa.amplitude_to_db(librosa.stft(new_y, n_fft=n_fft, hop_length=hop_length), ref=np.mean), sr=new_sr, y_axis='log', x_axis='time')
        plt.colorbar()
    return new_y, new_sr



def feature_extraction(y, sr, n_fft=1024, hop_length=None):
#     print(f'duration: {librosa.get_duration(y)}')
    new_y, new_sr = preprocess(y, sr, n_fft=1024, hop_length=hop_length)
    return generate_fingerprints(new_y, new_sr,  amp_min=amp_min)[0]        
        
def feature_extraction_from_file(file_path, sr=44100, n_fft=1024, hop_length=None, amp_min=amp_min):
    y, sr = librosa.load(file_path, sr=sr, mono=True) 
#     print(f'duration: {librosa.get_duration(y)}')
    new_y, new_sr = preprocess(y, sr, n_fft=n_fft, hop_length=hop_length)
    return generate_fingerprints(new_y, new_sr, amp_min=amp_min)[0]

def preprocess_string(string):
    return   string.replace("'", "''")


def get_song_meta(file_path):
    song_name, artist, album = '', '', ''
    try: 
        metadata = EasyID3(file_path)
    except mutagen.id3.ID3NoHeaderError:
        metadata = mutagen.File(file_path, easy=True)
        metadata.add_tags()
    if len(metadata) >0:
        song_name = metadata['Ttile']
        artist = metadata['Contributing artists']
        album = metadata['Album']
    else: 
        song_name = os.path.basename(file_path)
    
    dict = {
        'song_name': song_name,
        'artist':    artist,
        'album':     album
    }
    return dict



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        