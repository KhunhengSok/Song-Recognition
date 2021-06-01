import numpy as np
import hashlib
from scipy.ndimage.morphology import (binary_erosion,
                                      generate_binary_structure,
                                      iterate_structure)
from scipy.ndimage.filters import maximum_filter
import matplotlib.pyplot as plt
from typing import List, Tuple
import matplotlib.mlab as mlab
from operator import itemgetter
from time  import time
import librosa

from .settings import *

# Dejavu

# DEJAVU JSON RESPONSE
SONG_ID = "song_id"
SONG_NAME = 'song_name'
RESULTS = 'results'

HASHES_MATCHED = 'hashes_matched_in_input'

# Hashes fingerprinted in the db.
FINGERPRINTED_HASHES = 'fingerprinted_hashes_in_db'
# Percentage regarding hashes matched vs hashes fingerprinted in the db.
FINGERPRINTED_CONFIDENCE = 'fingerprinted_confidence'

# Hashes generated from the input.
INPUT_HASHES = 'input_total_hashes'
# Percentage regarding hashes matched vs hashes from the input.
INPUT_CONFIDENCE = 'input_confidence'

TOTAL_TIME = 'total_time'
FINGERPRINT_TIME = 'fingerprint_time'
QUERY_TIME = 'query_time'
ALIGN_TIME = 'align_time'
OFFSET = 'offset'
OFFSET_SECS = 'offset_seconds'

# DATABASE CLASS INSTANCES:
DATABASES = {
    'mysql': ("dejavu.database_handler.mysql_database", "MySQLDatabase"),
    'postgres': ("dejavu.database_handler.postgres_database", "PostgreSQLDatabase")
}

# TABLE SONGS
SONGS_TABLENAME = "songs"

# SONGS FIELDS
FIELD_SONG_ID = 'song_id'
FIELD_SONGNAME = 'song_name'
FIELD_FINGERPRINTED = "fingerprinted"
FIELD_FILE_SHA1 = 'file_sha1'
FIELD_TOTAL_HASHES = 'total_hashes'

# TABLE FINGERPRINTS
FINGERPRINTS_TABLENAME = "fingerprints"

# FINGERPRINTS FIELDS
FIELD_HASH = 'hash'
FIELD_OFFSET = 'offset' 

# FINGERPRINTS CONFIG:
# This is used as connectivity parameter for scipy.generate_binary_structure function. This parameter
# changes the morphology mask when looking for maximum peaks on the spectrogram matrix.
# Possible values are: [1, 2]
# Where 1 sets a diamond morphology which implies that diagonal elements are not considered as neighbors (this
# is the value used in the original dejavu code).
# And 2 sets a square mask, i.e. all elements are considered neighbors.
CONNECTIVITY_MASK = 2

# Sampling rate, related to the Nyquist conditions, which affects
# the range frequencies we can detect.
DEFAULT_FS = 44100

# Size of the FFT window, affects frequency granularity
DEFAULT_WINDOW_SIZE = 4096

# Ratio by which each sequential window overlaps the last and the
# next window. Higher overlap will allow a higher granularity of offset
# matching, but potentially more fingerprints.
DEFAULT_OVERLAP_RATIO = 0.5

# Degree to which a fingerprint can be paired with its neighbors. Higher values will
# cause more fingerprints, but potentially better accuracy.
DEFAULT_FAN_VALUE = 5  # 15 was the original value.

# Minimum amplitude in spectrogram in order to be considered a peak.
# This can be raised to reduce number of fingerprints, but can negatively
# affect accuracy.
DEFAULT_AMP_MIN = 10

# Number of cells around an amplitude peak in the spectrogram in order
# for Dejavu to consider it a spectral peak. Higher values mean less
# fingerprints and faster matching, but can potentially affect accuracy.
PEAK_NEIGHBORHOOD_SIZE = 10  # 20 was the original value.

# Thresholds on how close or far fingerprints can be in time in order
# to be paired as a fingerprint. If your max is too low, higher values of
# DEFAULT_FAN_VALUE may not perform as expected.
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200

# If True, will sort peaks temporally for fingerprinting;
# not sorting will cut down number of fingerprints, but potentially
# affect performance.
PEAK_SORT = True

# Number of bits to grab from the front of the SHA1 hash in the
# fingerprint calculation. The more you grab, the more memory storage,
# with potentially lesser collisions of matches.
FINGERPRINT_REDUCTION = 20

# Number of results being returned for file recognition
TOPN = 2

# def get_2D_peaks(arr2D: np.array, plot: bool = False, amp_min: int = DEFAULT_AMP_MIN):
# #     ->List[Tuple[List[int], List[int]]]
#     """
#     Extract maximum peaks from the spectogram matrix (arr2D).

#     :param arr2D: matrix representing the spectogram.
#     :param plot: for plotting the results.
#     :param amp_min: minimum amplitude in spectrogram in order to be considered a peak.
#     :return: a list composed by a list of frequencies and times.
#     """
#     # Original code from the repo is using a morphology mask that does not consider diagonal elements
#     # as neighbors (basically a diamond figure) and then applies a dilation over it, so what I'm proposing
#     # is to change from the current diamond figure to a just a normal square one:
#     #       F   T   F           T   T   T
#     #       T   T   T   ==>     T   T   T
#     #       F   T   F           T   T   T
#     # In my local tests time performance of the square mask was ~3 times faster
#     # respect to the diamond one, without hurting accuracy of the predictions.
#     # I've made now the mask shape configurable in order to allow both ways of find maximum peaks.
#     # That being said, we generate the mask by using the following function
#     # https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generate_binary_structure.html
#     struct = generate_binary_structure(2, CONNECTIVITY_MASK)

#     #  And then we apply dilation using the following function
#     #  http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.iterate_structure.html
#     #  Take into account that if PEAK_NEIGHBORHOOD_SIZE is 2 you can avoid the use of the scipy functions and just
#     #  change it by the following code:
#     #  neighborhood = np.ones((PEAK_NEIGHBORHOOD_SIZE * 2 + 1, PEAK_NEIGHBORHOOD_SIZE * 2 + 1), dtype=bool)
#     neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

#     # find local maxima using our filter mask
#     local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D

#     # Applying erosion, the dejavu documentation does not talk about this step.
#     background = (arr2D == 0)
#     eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

#     # Boolean mask of arr2D with True at peaks (applying XOR on both matrices).
#     detected_peaks = local_max != eroded_background

#     # extract peaks
#     amps = arr2D[detected_peaks]
#     freqs, times = np.where(detected_peaks)

#     # filter peaks
#     amps = amps.flatten()

#     # get indices for frequency and time
#     filter_idxs = np.where(amps > amp_min)

#     freqs_filter = freqs[filter_idxs]
#     times_filter = times[filter_idxs]

#     print(f'arr2D shape: {arr2D.shape}')
#     ratio = arr2D.shape[0]/arr2D.shape[1]
#     if plot:
#         # scatter of the peaks
# #         fig, ax = plt.subplots(figsize=(ratio*20,20))
#         fig, ax = plt.subplots(figsize=(40, 24))
#         ax.imshow(arr2D)
#         librosa.display.specshow(arr2D)
#         ax.scatter(times_filter, freqs_filter, linewidths=0.5)
#         ax.set_xlabel('Time')
#         ax.set_ylabel('Frequency')
#         ax.set_title("Spectrogram")
#         plt.gca().invert_yaxis()
#         plt.show()

#     return list(zip(freqs_filter, times_filter))


def generate_hashes(peaks: List[Tuple[int, int]], fan_value: int = DEFAULT_FAN_VALUE) -> List[Tuple[str, int]]:
    """
    Hash list structure:
       sha1_hash[0:FINGERPRINT_REDUCTION]    time_offset
        [(e05b341a9b77a51fd26, 32), ... ]

    :param peaks: list of peak frequencies and times.
    :param fan_value: degree to which a fingerprint can be paired with its neighbors.
    :return: a list of hashes with their corresponding offsets.
    """
    # frequencies are in the first position of the tuples
    idx_freq = 0
    # times are in the second position of the tuples
    idx_time = 1

    if PEAK_SORT:
        peaks.sort(key=itemgetter(1))

    hashes = []
    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):

                freq1 = peaks[i][idx_freq]
                freq2 = peaks[i + j][idx_freq]
                t1 = peaks[i][idx_time]
                t2 = peaks[i + j][idx_time]
                t_delta = t2 - t1

                if MIN_HASH_TIME_DELTA <= t_delta <= MAX_HASH_TIME_DELTA:
                    h = hashlib.sha1(f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode('utf-8'))
#                     hashes.append((h.hexdigest()[0:FINGERPRINT_REDUCTION], t1.astype(str) ))
                    hashes.append((h.hexdigest()[0:FINGERPRINT_REDUCTION], t1.astype(str) ))

    return hashes




def fingerprint(channel_samples: List[float],
                Fs: int = DEFAULT_FS,
                wsize: int = DEFAULT_WINDOW_SIZE,
                wratio: float = DEFAULT_OVERLAP_RATIO,
                fan_value: int = DEFAULT_FAN_VALUE,
                amp_min: int = DEFAULT_AMP_MIN) -> List[Tuple[str, int]]:
    """
    FFT the channel, log transform output, find local maxima, then return locally sensitive hashes.

    :param channel_samples: channel samples to fingerprint.
    :param Fs: audio sampling rate.
    :param wsize: FFT windows size.
    :param wratio: ratio by which each sequential window overlaps the last and the next window.
    :param fan_value: degree to which a fingerprint can be paired with its neighbors.
    :param amp_min: minimum amplitude in spectrogram in order to be considered a peak.
    :return: a list of hashes with their corresponding offsets.
    """
    # FFT the signal and extract frequency components
    arr2D = mlab.specgram(
        channel_samples,
        NFFT=wsize,
        Fs=Fs,
        window=mlab.window_hanning,
        noverlap=int(wsize * wratio))[0]

    # Apply log transform since specgram function returns linear array. 0s are excluded to avoid np warning.
#     arr2D = 10 * np.log10(arr2D, out=np.zeros_like(arr2D), where=(arr2D != 0))

    # ===================================Change===========================================
    arr2D = librosa.stft(channel_samples)
    
    local_maxima = get_2D_peaks(np.abs(arr2D), plot=False, amp_min=amp_min, Fs=Fs)
    
    # return hashes
    return generate_hashes(local_maxima, fan_value=fan_value)


def get_2D_peaks(arr2D: np.array, plot: bool = False, amp_min: int = DEFAULT_AMP_MIN,Fs: int = DEFAULT_FS)\
        -> List[Tuple[List[int], List[int]]]:
    """
    Extract maximum peaks from the spectogram matrix (arr2D).

    :param arr2D: matrix representing the spectogram.
    :param plot: for plotting the results.
    :param amp_min: minimum amplitude in spectrogram in order to be considered a peak.
    :param FS
    :return: a list composed by a list of frequencies and times.
    """
    # Original code from the repo is using a morphology mask that does not consider diagonal elements
    # as neighbors (basically a diamond figure) and then applies a dilation over it, so what I'm proposing
    # is to change from the current diamond figure to a just a normal square one:
    #       F   T   F           T   T   T
    #       T   T   T   ==>     T   T   T
    #       F   T   F           T   T   T
    # In my local tests time performance of the square mask was ~3 times faster
    # respect to the diamond one, without hurting accuracy of the predictions.
    # I've made now the mask shape configurable in order to allow both ways of find maximum peaks.
    # That being said, we generate the mask by using the following function
    # https://docs.scipy.or g/doc/scipy/reference/generated/scipy.ndimage.generate_binary_structure.html
    struct = generate_binary_structure(2, CONNECTIVITY_MASK)

    #  And then we apply dilation using the following function
    #  http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.iterate_structure.html
    #  Take into account that if PEAK_NEIGHBORHOOD_SIZE is 2 you can avoid the use of the scipy functions and just
    #  change it by the following code:
    #  neighborhood = np.ones((PEAK_NEIGHBORHOOD_SIZE * 2 + 1, PEAK_NEIGHBORHOOD_SIZE * 2 + 1), dtype=bool)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # find local maxima using our filter mask
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D

    # Applying erosion, the dejavu documentation does not talk about this step.
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    # Boolean mask of arr2D with True at peaks (applying XOR on both matrices).
    detected_peaks = local_max != eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    freqs, times = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()

    # get indices for frequency and time
    filter_idxs = np.where(amps > amp_min) 

    freqs_filter = freqs[filter_idxs]
    times_filter = times[filter_idxs]

    ratio = arr2D.shape[0]/arr2D.shape[1]
#     print(ratio)
    # print(f'arr2D shape: {arr2D.shape}')
    
    
    # if plot:
    #     # scatter of the peaks
    #     fig, ax = plt.subplots()
    #     fig, ax = plt.subplots(figsize=(arr2D.shape[0]/15, arr2D.shape[1]/15))

    #     ax.imshow(arr2D)
    #     ax.scatter(times_filter, freqs_filter, linewidths=0.5)
    #     ax.set_xlabel('Time')
    #     ax.set_ylabel('Frequency')
    #     ax.set_title("Spectrogram")
    #     plt.gca().invert_yaxis()
    #     plt.show()

    if plot: 
        spec = np.empty(detected_peaks.shape)
        spec.fill(False)
        spec[freqs_filter, times_filter] = True

        librosa.display.specshow(spec, x_axis='time', y_axis='log', sr=Fs, hop_length=256)
        plt.colorbar()
    return list(zip(freqs_filter, times_filter))



# def generate_hashes(peaks: List[Tuple[int, float]], fan_value: int = DEFAULT_FAN_VALUE) -> List[Tuple[str, int]]:
#     """
#     Hash list structure:
#        sha1_hash[0:FINGERPRINT_REDUCTION]    time_offset
#         [(e05b341a9b77a51fd26, 32), ... ]

#     :param peaks: list of peak frequencies and times.
#     :param fan_value: degree to which a fingerprint can be paired with its neighbors.
#     :return: a list of hashes with their corresponding offsets.
#     """
#     # frequencies are in the first position of the tuples
#     idx_freq = 0
#     # times are in the second position of the tuples
#     idx_time = 1

#     if PEAK_SORT:
#         peaks.sort(key=itemgetter(1))

#     hashes = []
#     for i in range(len(peaks)):
#         for j in range(1, fan_value):
#             if (i + j) < len(peaks):

#                 freq1 = peaks[i][idx_freq]
#                 freq2 = peaks[i + j][idx_freq]
#                 t1 = peaks[i][idx_time]
#                 t2 = peaks[i + j][idx_time]
#                 t_delta = t2 - t1

#                 if MIN_HASH_TIME_DELTA <= t_delta <= MAX_HASH_TIME_DELTA:
#                     h = hashlib.sha1(f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode('utf-8'))

#                     hashes.append((h.hexdigest()[0:FINGERPRINT_REDUCTION], t1))

#     return hashes


def generate_fingerprints( samples: List[float], Fs=DEFAULT_FS, amp_min: int = DEFAULT_AMP_MIN ) -> Tuple[List[Tuple[str, int]], float]:
    f"""
    Generate the fingerprints for the given sample data (channel).

    :param samples: list of ints which represents the channel info of the given audio file.
    :param Fs: sampling rate which defaults to {DEFAULT_FS}.
    :return: a list of tuples for hash and its corresponding offset, together with the generation time.
    """
    t = time()
    hashes = fingerprint(samples, Fs=Fs, amp_min=amp_min)
    fingerprint_time = time() - t
    
    return hashes, fingerprint_time
