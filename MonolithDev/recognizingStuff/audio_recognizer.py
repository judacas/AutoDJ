"""
Audio Recognition System
A consolidated script for finding songs within audio mixes using chroma-based
fingerprinting.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import librosa  # type: ignore
import numpy as np  # type: ignore
from scipy.signal import correlate  # type: ignore

logger = logging.getLogger(__name__)


class AudioRecognizerConfig:
    """Configuration class for audio recognition parameters."""

    def __init__(self):
        # Audio processing parameters
        self.hop_length = 512
        self.chunk_seconds = 5
        self.n_chunks = 30
        self.buffer_seconds = 30
        self.min_chunk_factor = 4

        # Matching thresholds
        self.confidence_threshold_rough = 10000
        self.confidence_threshold_core = 1000
        self.similarity_threshold = 0.6
        self.isometry_tolerance = 100

        # Refinement parameters
        self.trim_portion = 0.25
        self.min_similarity_threshold = 0.8
        self.beats_per_measure = 4


class AudioFingerprinter:
    """Handles audio fingerprinting using chroma features."""

    def __init__(self, config: AudioRecognizerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def create_fingerprint(
        self, audio_file: str
    ) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """
        Create chroma-based fingerprint from audio file.

        Args:
            audio_file: Path to audio file

        Returns:
            Tuple of (chroma_features, sample_rate) or (None, None) if error
        """
        try:
            preloaded_fingerprint = self.load_fingerprint(
                self.get_fingerprint_path(audio_file)
            )
            if (
                preloaded_fingerprint[0] is not None
                and preloaded_fingerprint[1] is not None
            ):
                return preloaded_fingerprint
        except Exception:
            self.logger.info("preloaded fingerprint not found, creating new one")

        audio_path = Path(audio_file)
        if not audio_path.exists():
            self.logger.error(f"Audio file not found: {audio_file}")
            return None, None

        try:
            self.logger.info(f"Fingerprinting '{audio_file}'...")
            y, sr = librosa.load(audio_file, sr=None)
            chroma = librosa.feature.chroma_stft(
                y=y, sr=sr, hop_length=self.config.hop_length
            )
            self.logger.info("Fingerprinting complete.")
            self.save_fingerprint(
                chroma, int(sr), self.get_fingerprint_path(audio_file)
            )

            return chroma, int(sr)
        except Exception as e:
            self.logger.error(f"Error processing {audio_file}: {e}")
            return None, None

    def get_fingerprint_path(self, audio_file: str) -> str:
        """Get the path to the fingerprint file, using only the base filename."""
        from pathlib import Path

        base_name = Path(audio_file).name
        return f"fingerprints/{base_name}.npz"

    def save_fingerprint(
        self, chroma: Optional[np.ndarray], sr: Optional[int], file_path: str
    ) -> bool:
        """Save fingerprint data to file."""
        if chroma is None or sr is None:
            self.logger.error("Cannot save fingerprint: chroma or sr is None")
            return False

        try:
            np.savez(file_path, chroma=chroma, sr=sr)
            self.logger.info(f"Fingerprint saved to {file_path}.npz")
            return True
        except Exception as e:
            self.logger.error(f"Error saving fingerprint: {e}")
            return False

    def load_fingerprint(
        self, file_path: str
    ) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """Load fingerprint from file."""
        try:
            with np.load(file_path) as data:
                return data["chroma"], data["sr"]
        except Exception as e:
            self.logger.error(f"Error loading fingerprint: {e}")
            return None, None


class AudioRecognizer:
    """Main audio recognition engine."""

    def __init__(self, config: AudioRecognizerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def find_rough_match(
        self, song_chroma: np.ndarray, mix_chroma: np.ndarray, sr: Optional[int]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Find rough estimate of song location in mix using cross-correlation.

        Args:
            song_chroma: Source song chroma features
            mix_chroma: Mix chroma features
            sr: Sample rate

        Returns:
            Tuple of (start_time, end_time) or (None, None) if no match
        """
        if sr is None:
            self.logger.error("Sample rate is None, cannot find rough match")
            return None, None

        self.logger.info("Searching for rough song match in mix...")

        # Normalize features
        song_norm = (song_chroma - np.mean(song_chroma)) / np.std(song_chroma)
        mix_norm = (mix_chroma - np.mean(mix_chroma)) / np.std(mix_chroma)

        # Cross-correlation
        correlation = correlate(mix_norm, song_norm, mode="valid", method="fft")
        time_correlation = np.sum(correlation, axis=0)
        best_match_frame = np.argmax(time_correlation)
        best_match_score = time_correlation[best_match_frame]

        self.logger.info(f"Best match score: {best_match_score:.2f}")

        if best_match_score < self.config.confidence_threshold_rough:
            self.logger.warning(
                "No real match found: best match score below threshold."
            )
            return None, None

        start_time = librosa.frames_to_time(
            best_match_frame, sr=sr, hop_length=self.config.hop_length
        ).item()
        song_duration_frames = song_chroma.shape[1]
        song_duration_secs = librosa.frames_to_time(
            song_duration_frames, sr=sr, hop_length=self.config.hop_length
        ).item()
        end_time = start_time + song_duration_secs

        self.logger.info(
            f"Rough match found! Start: {start_time:.2f}s, End: {end_time:.2f}s"
        )
        return start_time, end_time

    def recognize_song_in_mix(self, song_path: str, mix_path: str) -> dict:
        """Recognize a song within a mix and refine alignment via beat matching."""
        fingerprinter = AudioFingerprinter(self.config)

        # Create fingerprints
        self.logger.info(f"Creating fingerprints for {song_path} and {mix_path}")
        song_chroma, song_sr = fingerprinter.create_fingerprint(song_path)
        self.logger.info(f"Fingerprint created for {song_path}")

        self.logger.info(f"Creating fingerprints for {mix_path}")
        mix_chroma, mix_sr = fingerprinter.create_fingerprint(mix_path)
        self.logger.info(f"Fingerprints created for {song_path} and {mix_path}")

        if song_chroma is None or mix_chroma is None or mix_sr is None:
            return {"success": False, "error": "Failed to create fingerprints"}

        if song_sr is not None and song_sr != mix_sr:
            self.logger.info(
                "Song sample rate (%s) differs from mix sample rate (%s); "
                "resampling song audio for beat alignment.",
                song_sr,
                mix_sr,
            )

        # Find rough match
        rough_start, rough_end = self.find_rough_match(song_chroma, mix_chroma, mix_sr)

        if rough_start is None or rough_end is None:
            return {"success": False, "error": "No match found"}

        # Fine-tune alignment using beat matching to a downbeat
        refined_start, refined_end, beat_alignment = self.fine_tune_alignment(
            song_path=song_path,
            mix_path=mix_path,
            sr=mix_sr,
            rough_start_time=rough_start,
            rough_end_time=rough_end,
        )

        return {
            "success": True,
            "song_path": song_path,
            "mix_path": mix_path,
            "rough_match": {"start": rough_start, "end": rough_end},
            "fine_tuned_match": {"start": refined_start, "end": refined_end},
            "beat_alignment": beat_alignment,
            "precise_match": {
                "song_start": 0.0,
                "song_end": refined_end - refined_start,
                "mix_start": refined_start,
                "mix_end": refined_end,
            },
        }

    def fine_tune_alignment(
        self,
        song_path: str,
        mix_path: str,
        sr: int,
        rough_start_time: float,
        rough_end_time: float,
    ) -> Tuple[float, float, dict]:
        """
        Fine-tune alignment by beat matching song and mix downbeats.

        Args:
            song_path: Path to the source song audio file
            mix_path: Path to the mix audio file
            sr: Sample rate used for analysis
            rough_start_time: Initial rough estimate start time
            rough_end_time: Initial rough estimate end time

        Returns:
            Tuple of (refined_start_time, refined_end_time, alignment_info)
        """

        self.logger.info("Fine-tuning alignment using beat matching...")

        try:
            song_audio, _ = librosa.load(song_path, sr=sr)
            mix_audio, _ = librosa.load(mix_path, sr=sr)
        except Exception as exc:
            self.logger.error(f"Failed to load audio for beat matching: {exc}")
            return rough_start_time, rough_end_time, {"status": "load_failed"}

        song_duration = len(song_audio) / sr
        mix_duration = len(mix_audio) / sr

        # Compute beat tracks
        song_onset_env = librosa.onset.onset_strength(y=song_audio, sr=sr)
        mix_onset_env = librosa.onset.onset_strength(y=mix_audio, sr=sr)

        song_tempo, song_beats = librosa.beat.beat_track(
            onset_envelope=song_onset_env, sr=sr
        )
        mix_tempo, mix_beats = librosa.beat.beat_track(
            onset_envelope=mix_onset_env, sr=sr
        )

        beats_per_measure = max(1, self.config.beats_per_measure)

        song_downbeat_frames = song_beats[::beats_per_measure]
        mix_downbeat_frames = mix_beats[::beats_per_measure]

        if len(song_downbeat_frames) == 0 or len(mix_downbeat_frames) == 0:
            self.logger.warning(
                "Beat tracking failed to find downbeats; using rough estimate."
            )
            return rough_start_time, rough_end_time, {
                "status": "beat_tracking_failed",
                "song_tempo": float(song_tempo),
                "mix_tempo": float(mix_tempo),
            }

        song_downbeat_times = librosa.frames_to_time(
            song_downbeat_frames, sr=sr
        )
        mix_downbeat_times = librosa.frames_to_time(mix_downbeat_frames, sr=sr)

        song_downbeat_time = float(song_downbeat_times[0])

        # Find the downbeat in the mix closest to the rough start
        candidate_index = np.searchsorted(mix_downbeat_times, rough_start_time)
        candidate_times = []
        if candidate_index < len(mix_downbeat_times):
            candidate_times.append(float(mix_downbeat_times[candidate_index]))
        if candidate_index > 0:
            candidate_times.append(float(mix_downbeat_times[candidate_index - 1]))

        if not candidate_times:
            self.logger.warning(
                "No suitable downbeat candidates near rough start; using rough estimate."
            )
            return rough_start_time, rough_end_time, {
                "status": "no_downbeat_near_match",
                "song_tempo": float(song_tempo),
                "mix_tempo": float(mix_tempo),
            }

        mix_downbeat_time = min(
            candidate_times, key=lambda time_value: abs(time_value - rough_start_time)
        )

        refined_start_time = mix_downbeat_time - song_downbeat_time
        refined_start_time = max(0.0, refined_start_time)

        # Ensure the refined start keeps the song within the mix duration
        if refined_start_time + song_duration > mix_duration:
            refined_start_time = max(0.0, mix_duration - song_duration)

        refined_end_time = refined_start_time + song_duration

        alignment_info = {
            "status": "aligned",
            "song_tempo": float(song_tempo),
            "mix_tempo": float(mix_tempo),
            "song_downbeat_time": song_downbeat_time,
            "mix_downbeat_time": mix_downbeat_time,
            "beats_per_measure": beats_per_measure,
        }

        self.logger.info(
            "Beat alignment complete: start %.2fs, end %.2fs (mix downbeat %.2fs)",
            refined_start_time,
            refined_end_time,
            mix_downbeat_time,
        )

        return refined_start_time, refined_end_time, alignment_info


def main():
    """Main function to run the audio recognition pipeline."""

    # Configuration
    config = AudioRecognizerConfig()

    SOURCE_SONG_PATH = "downloads\originals\Bt71DPAcWXM__UWAIE - KAPO - SALSATION® choreography by Alejandro Angulo.mp3"
    MIX_PATH = "downloads\PbB_dF7Hetc__Fiesta Latina Mix 2024 ｜ Latin Party Mix 2024 ｜ The Best Latin Party Hits by OSOCITY.mp3"  # Fixed: was .wav

    # Create pipeline
    pipeline = AudioRecognizer(config)

    # Run recognition
    result = pipeline.recognize_song_in_mix(SOURCE_SONG_PATH, MIX_PATH)

    # Print results
    if result["success"]:
        print("\n--- Recognition Results ---")
        print(f"Source song: {result['song_path']}")
        print(f"Mix: {result['mix_path']}")

        if "rough_match" in result and result["rough_match"]["start"] is not None:
            rough = result["rough_match"]
            print(f"Rough match: {rough['start']:.2f}s to {rough['end']:.2f}s")

        if "precise_match" in result:
            precise = result["precise_match"]
            print("Precise match:")
            print(
                f"  Song segment: {precise['song_start']:.2f}s to "
                f"{precise['song_end']:.2f}s"
            )
            print(
                f"  Mix segment: {precise['mix_start']:.2f}s to "
                f"{precise['mix_end']:.2f}s"
            )

        # Show fine-tuned results if available
        if "fine_tuned_match" in result:
            fine_tuned = result["fine_tuned_match"]
            print(
                f"Fine-tuned match: {fine_tuned['start']:.2f}s to {fine_tuned['end']:.2f}s"
            )

        # Show beat alignment details
        if "beat_alignment" in result:
            alignment = result["beat_alignment"]
            status = alignment.get("status", "unknown")
            print("Beat alignment status:", status)
            if status == "aligned":
                print(
                    f"  Song downbeat at {alignment['song_downbeat_time']:.2f}s"
                    f" aligned to mix downbeat at {alignment['mix_downbeat_time']:.2f}s"
                )
                print(
                    f"  Tempos — song: {alignment['song_tempo']:.1f} BPM, "
                    f"mix: {alignment['mix_tempo']:.1f} BPM"
                )
    else:
        print(f"\nRecognition failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
