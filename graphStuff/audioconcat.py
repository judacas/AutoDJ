import librosa
import numpy as np
import pygame
from pathlib import Path
import time
from XTYpair import XTY_PAIR


def extract_excerpt(filename, start, end, sr=44100):
    duration = end - start
    y, _ = librosa.load(filename, sr=sr, offset=start, duration=duration, mono=True)
    return y

class MultiDualAudioPlayer:
    def __init__(self, sr=44100):
        pygame.mixer.pre_init(frequency=sr, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        self.sr = sr
        self.song_channel = None
        self.trans_channel = None

    def setup_both_audios(self, pairs: [XTY_PAIR], crossfade_duration=5.0):
        song_audio_chunks = []
        transition_audio_chunks = []

        
        for i in range(len(pairs)):
            pair = pairs[i]
            # Extract song excerpt
            song_excerpt = None
            transition_excerpt = None
            if i == 0:
                # For the first song, start from the beginning
                song_excerpt = extract_excerpt(
                    pair.X_song_path,
                    0,
                    pair.Xcross_out - pair.Xoffset + crossfade_duration,
                    sr=self.sr
                )
                song_audio_chunks.append(song_excerpt)
                song_audio_chunks.append(np.zeros(int(self.sr * (pair.Yoffset - pair.Xcross_out - crossfade_duration))))
            elif i == len(pairs) - 1:
                song_excerpt = extract_excerpt(
                    pair.X_song_path,
                    pair.Xcross_in - pair.Xoffset,
                    pair.Xcross_out - pair.Xoffset + crossfade_duration,
                    sr=self.sr
                )
                song_audio_chunks.append(song_excerpt)
                song_audio_chunks.append(np.zeros(int(self.sr * (pair.Yoffset - pair.Xcross_out - crossfade_duration))))
                # Go to the end for the last song
                song_excerpt = extract_excerpt(
                    pair.Y_song_path,
                    pair.Ycross_in - pair.Yoffset,
                    librosa.get_duration(filename=pair.Y_song_path),
                    sr=self.sr
                )
            else:
                song_excerpt = extract_excerpt(
                    pair.X_song_path,
                    pair.Xcross_in - pair.Xoffset,
                    pair.Xcross_out - pair.Xoffset + crossfade_duration,
                    sr=self.sr
                )
                song_audio_chunks.append(song_excerpt)
                song_audio_chunks.append(np.zeros(int(self.sr * (pair.Yoffset - pair.Xcross_out - crossfade_duration))))

            # Extract transition excerpt
            if i == 0:
                transition_audio_chunks.append(np.zeros(int(self.sr * (pair.Xcross_in - pair.Xoffset))))
            transition_excerpt = extract_excerpt(
                pair.mix_song_path,
                pair.Xcross_out,
                pair.Ycross_in + crossfade_duration,
                sr=self.sr
            )
            transition_audio_chunks.append(transition_excerpt)

        return song_audio_chunks, transition_audio_chunks

    # I still have to somehow get the pairs from the graph
    def play_dual_streams(self, pairs, song_volume=1.0, transition_volume=1.0):
        song_audio, trans_audio = setup_both_audios(self, pairs)

        song_audio = np.concatenate(song_audio)
        trans_audio = np.concatenate(trans_audio)
        max_len = max(len(song_audio), len(trans_audio))
        song_audio = np.pad(song_audio, (0, max_len - len(song_audio)))
        trans_audio = np.pad(trans_audio, (0, max_len - len(trans_audio)))

        song_audio_int16 = (song_audio * 32767).astype("int16")
        trans_audio_int16 = (trans_audio * 32767).astype("int16")

        song_stereo = np.column_stack((song_audio_int16, song_audio_int16))
        trans_stereo = np.column_stack((trans_audio_int16, trans_audio_int16))

        song_sound = pygame.sndarray.make_sound(song_stereo)
        trans_sound = pygame.sndarray.make_sound(trans_stereo)

        # Play on separate channels
        self.song_channel = song_sound.play()
        self.trans_channel = trans_sound.play()

        self.song_channel.set_volume(song_volume)
        self.trans_channel.set_volume(transition_volume)

        print("Playing concatenated song and transition streams.")

    def set_song_volume(self, volume):
        if self.song_channel:
            self.song_channel.set_volume(volume)

    def set_transition_volume(self, volume):
        if self.trans_channel:
            self.trans_channel.set_volume(volume)

    def crossfadeST(self, duration=5.0, steps=50):
        """Crossfade from song to transition over 'duration' seconds."""
        for i in range(steps + 1):
            t = i / steps
            self.set_song_volume(1.0 - t)
            self.set_transition_volume(t)
            time.sleep(duration / steps)

    def crossfadeTS(self, duration=5.0, steps=50):
        """Crossfade from transition to song over 'duration' seconds."""
        for i in range(steps + 1):
            t = i / steps
            self.set_song_volume(t)
            self.set_transition_volume(1.0 - t)
            time.sleep(duration / steps)

