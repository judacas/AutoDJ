# main.py

from fingerprinter import create_chroma_fingerprint
from recognizer import chunk_match, find_whole_song_in_mix, refine_whole_match

# from recognizer import confident_chunk_match

if __name__ == "__main__":
    SOURCE_SONG_PATH = "source_song.mp3"
    MIX_PATH = "short_mix.wav"

    # --- Task #4: Fingerprinting ---
    song_fp_data = create_chroma_fingerprint(SOURCE_SONG_PATH)
    mix_fp_data = create_chroma_fingerprint(MIX_PATH)

    song_fp, song_sr = song_fp_data
    mix_fp, mix_sr = mix_fp_data

    if song_sr != mix_sr:
        print(
            "\nWarning: Sample rates of song and mix do not match. Results may be inaccurate."
        )

    # --- Task #5: Song-in-Mix Recognition ---

    # This version is with starting with a few chunk matches
    # Deprecated, tried to be too precise

    if song_fp is not None and mix_fp is not None:
        rough_start, rough_end = find_whole_song_in_mix(song_fp, mix_fp, mix_sr)
        if rough_start is not None and rough_end is not None:
            print("\n--- 🎵 Partial Result 🎵 ---")
            print(
                f"The source song was roughly found in the mix from {rough_start:.2f} seconds to {rough_end:.2f} seconds."
            )

        song_start, song_end, mix_start, mix_end = chunk_match(song_fp, mix_fp, mix_sr)
        if song_start is not None and song_end is not None:
            print("\n--- 🎵 Final Result 🎵 ---")
            print(
                f"Hopefully good match! Song Start: {song_start:.2f}, Song End: {song_end:.2f}"
            )
            print(f"Start in the mix: {mix_start:.2f}, End in the mix: {mix_end:.2f}")
        else:
            print("wtf?")

    # Most recent version, conservative start and end

    # if song_fp is not None and mix_fp is not None:
    #     rough_start, rough_end = find_whole_song_in_mix(song_fp, mix_fp, mix_sr)
    #     if rough_start is not None and rough_end is not None:
    #         print("\n--- 🎵 Partial Result 🎵 ---")
    #         print(f"The source song was roughly found in the mix from {rough_start:.2f} seconds to {rough_end:.2f} seconds.")

    #     song_start, song_end, mix_start, mix_end = confident_chunk_match(song_fp, mix_fp, mix_sr)
    #     if song_start is not None and song_end is not None:
    #         print("\n--- 🎵 Final Result 🎵 ---")
    #         print(f"Safe match! Song Start: {song_start:.2f}, Song End: {song_end:.2f}")
    #         print(f"Start in the mix: {mix_start:.2f}, End in the mix: {mix_end:.2f}")
    #     else:
    #         print("wtf?")
