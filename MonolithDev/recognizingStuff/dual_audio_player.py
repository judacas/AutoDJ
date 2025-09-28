"""
Dual Audio Player
A simple utility for playing two MP3 files simultaneously from their respective starting points.
"""

import logging
import threading
import time
from pathlib import Path
from typing import Optional, Tuple

import librosa
import numpy as np
import pygame

logger = logging.getLogger(__name__)


class DualAudioPlayer:
    """Handles simultaneous playback of two audio files."""

    def __init__(self):
        """Initialize pygame mixer for audio playback."""
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        self.logger = logging.getLogger(__name__)

    def play_dual_audio(
        self,
        file1_path: str,
        file2_path: str,
        start1: float = 0.0,
        start2: float = 0.0,
        volume1: float = 0.5,
        volume2: float = 0.5,
    ) -> bool:
        """
        Play two audio files simultaneously from their respective starting points.
        File 1 plays on the LEFT channel, File 2 plays on the RIGHT channel.

        Args:
            file1_path: Path to first audio file (plays on LEFT channel)
            file2_path: Path to second audio file (plays on RIGHT channel)
            start1: Start time in seconds for first file
            start2: Start time in seconds for second file
            volume1: Volume for first file (0.0 to 1.0)
            volume2: Volume for second file (0.0 to 1.0)

        Returns:
            True if playback started successfully, False otherwise
        """
        try:
            # Validate file paths
            if not Path(file1_path).exists():
                self.logger.error(f"File not found: {file1_path}")
                return False
            if not Path(file2_path).exists():
                self.logger.error(f"File not found: {file2_path}")
                return False

            self.logger.info(f"Playing dual audio:")
            self.logger.info(
                f"  File 1: {file1_path} (start: {start1}s, volume: {volume1})"
            )
            self.logger.info(
                f"  File 2: {file2_path} (start: {start2}s, volume: {volume2})"
            )

            # Load audio data with librosa for proper seeking
            audio1, sr1 = librosa.load(file1_path, sr=None)
            audio2, sr2 = librosa.load(file2_path, sr=None)

            # Calculate start samples
            start1_samples = int(start1 * sr1) if start1 > 0 else 0
            start2_samples = int(start2 * sr2) if start2 > 0 else 0

            # Trim audio to start from desired positions
            if start1_samples > 0:
                audio1 = audio1[start1_samples:]
            if start2_samples > 0:
                audio2 = audio2[start2_samples:]

            # Convert to pygame-compatible format
            # Convert float32 to int16 for pygame
            audio1_int16 = (audio1 * 32767).astype("int16")
            audio2_int16 = (audio2 * 32767).astype("int16")

            # Ensure stereo format (2D array) for pygame mixer
            if len(audio1_int16.shape) == 1:  # Mono to stereo
                audio1_int16 = np.column_stack((audio1_int16, audio1_int16))
            if len(audio2_int16.shape) == 1:  # Mono to stereo
                audio2_int16 = np.column_stack((audio2_int16, audio2_int16))

            # Create stereo-panned audio
            # File 1: Left channel only (right channel = 0)
            audio1_stereo = np.column_stack(
                (audio1_int16[:, 0], np.zeros_like(audio1_int16[:, 0]))
            )

            # File 2: Right channel only (left channel = 0)
            audio2_stereo = np.column_stack(
                (np.zeros_like(audio2_int16[:, 0]), audio2_int16[:, 0])
            )

            # Create pygame sounds from stereo-panned audio
            sound1 = pygame.sndarray.make_sound(audio1_stereo)
            sound2 = pygame.sndarray.make_sound(audio2_stereo)

            # Set volumes
            sound1.set_volume(volume1)
            sound2.set_volume(volume2)

            # Start both sounds immediately
            sound1.play()
            sound2.play()

            self.logger.info(
                f"Started playing {Path(file1_path).name} from {start1}s (LEFT channel)"
            )
            self.logger.info(
                f"Started playing {Path(file2_path).name} from {start2}s (RIGHT channel)"
            )
            self.logger.info("Dual audio playback started with stereo separation!")
            return True

        except Exception as e:
            self.logger.error(f"Error playing dual audio: {e}")
            return False

    def stop_all(self):
        """Stop all currently playing audio."""
        pygame.mixer.stop()
        self.logger.info("Stopped all audio playback")

    def set_volume(self, volume: float):
        """Set master volume for all audio (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(volume)
        self.logger.info(f"Master volume set to {volume}")


def play_dual_audio(
    file1_path: str,
    file2_path: str,
    start1: float = 0.0,
    start2: float = 0.0,
    volume1: float = 0.5,
    volume2: float = 0.5,
) -> bool:
    """
    Convenience function to play two audio files simultaneously.
    File 1 plays on the LEFT channel, File 2 plays on the RIGHT channel.

    Args:
        file1_path: Path to first audio file (plays on LEFT channel)
        file2_path: Path to second audio file (plays on RIGHT channel)
        start1: Start time in seconds for first file
        start2: Start time in seconds for second file
        volume1: Volume for first file (0.0 to 1.0)
        volume2: Volume for second file (0.0 to 1.0)

    Returns:
        True if playback started successfully, False otherwise
    """
    player = DualAudioPlayer()
    return player.play_dual_audio(
        file1_path, file2_path, start1, start2, volume1, volume2
    )


def main():
    """Test the dual audio player with sample files."""

    # Sample file paths (update these to your actual files)
    file1 = "downloads/originals/Bt71DPAcWXM__UWAIE - KAPO - SALSATION® choreography by Alejandro Angulo.mp3"
    file2 = "downloads/mixes/PbB_dF7Hetc__Fiesta Latina Mix 2024 ｜ Latin Party Mix 2024 ｜ The Best Latin Party Hits by OSOCITY.mp3"

    print("Testing Dual Audio Player")
    print(f"File 1: {file1}")
    print(f"File 2: {file2}")

    # Test playing both files from the beginning
    success = play_dual_audio(file1, file2, start1=0.0, start2=308.64)

    if success:
        print("Dual audio playback started!")
        print("Press Enter to stop playback...")
        input()

        # Stop playback
        player = DualAudioPlayer()
        player.stop_all()
        print("Playback stopped")
    else:
        print("Failed to start dual audio playback")


if __name__ == "__main__":
    main()
