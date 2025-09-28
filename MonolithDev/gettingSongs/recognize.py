# recognizer.py

import librosa
import numpy as np
from scipy.signal import correlate
import warnings

warnings.filterwarnings('ignore')

def find_song_in_mix(song_chroma, mix_chroma, sr):
    """
    Finds the start and end time of a song within a mix using cross-correlation.
    """
    print("Searching for song in mix...")
    
    song_norm = (song_chroma - np.mean(song_chroma)) / np.std(song_chroma)
    mix_norm = (mix_chroma - np.mean(mix_chroma)) / np.std(mix_chroma)

    correlation = correlate(mix_norm, song_norm, mode='valid', method='fft')
    time_correlation = np.sum(correlation, axis=0)
    best_match_frame = np.argmax(time_correlation)

    hop_length = 512
    start_time = librosa.frames_to_time(best_match_frame, sr=sr, hop_length=hop_length)

    song_duration_frames = song_chroma.shape[1]
    song_duration_secs = librosa.frames_to_time(song_duration_frames, sr=sr, hop_length=hop_length)
    end_time = start_time + song_duration_secs
    
    print(f"Match found! Estimated start: {start_time:.2f}s, Estimated end: {end_time:.2f}s")
    return start_time, end_time