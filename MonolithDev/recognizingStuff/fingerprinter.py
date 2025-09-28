# fingerprinter.py

import warnings

import librosa
import numpy as np

warnings.filterwarnings("ignore")


def create_chroma_fingerprint(audio_file):
    """
    Loads an audio file and computes its chroma features, which act as a fingerprint.
    """
    print(f"Fingerprinting '{audio_file}'...")
    try:
        y, sr = librosa.load(audio_file, sr=None)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        print("Fingerprinting complete.")
        return chroma, sr
    except Exception as e:
        print(f"Error processing {audio_file}: {e}")
        return None, None


def save_fingerprint(fingerprint_data, file_path):
    """Saves the fingerprint data (chroma and sr) to a file."""
    np.savez(file_path, chroma=fingerprint_data[0], sr=fingerprint_data[1])
    print(f"Fingerprint saved to {file_path}.npz")


def load_fingerprint(file_path):
    """Loads a fingerprint from a file."""
    with np.load(f"{file_path}.npz") as data:
        return data["chroma"], data["sr"]
