# main.py

from fingerprinter import create_chroma_fingerprint
from recognizer import find_song_in_mix

if __name__ == "__main__":
    SOURCE_SONG_PATH = 'source_song.mp3'
    MIX_PATH = 'mix.mp3'

    # --- Task #4: Fingerprinting ---
    song_fp_data = create_chroma_fingerprint(SOURCE_SONG_PATH)
    mix_fp_data = create_chroma_fingerprint(MIX_PATH)
    
    song_fp, song_sr = song_fp_data
    mix_fp, mix_sr = mix_fp_data
    
    if song_sr != mix_sr:
        print("\nWarning: Sample rates of song and mix do not match. Results may be inaccurate.")

    # --- Task #5: Song-in-Mix Recognition ---
    if song_fp is not None and mix_fp is not None:
        start, end = find_song_in_mix(song_fp, mix_fp, mix_sr)
        
        print("\n--- 🎵 Final Result 🎵 ---")
        print(f"The source song was found in the mix from {start:.2f} seconds to {end:.2f} seconds.")