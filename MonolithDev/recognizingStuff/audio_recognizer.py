"""
Audio Recognition System
A consolidated script for finding songs within audio mixes using chroma-based
fingerprinting.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import librosa  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
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
        """
        Recognize a song within a mix with fine-tuning based on highest confidence chunk.
        """
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

        # Find rough match
        rough_start, rough_end = self.find_rough_match(song_chroma, mix_chroma, mix_sr)

        if rough_start is None or rough_end is None:
            return {"success": False, "error": "No match found"}

        # Generate aligned confidences to find the best reference chunk
        self.logger.info("Generating aligned confidences for fine-tuning...")
        (time_points, certainty_scores, reference_chunk) = (
            self.generate_alignedConfidences(
                song_chroma=song_chroma,
                mix_chroma=mix_chroma,
                sr=mix_sr,
                song_start_time=0.0,
                mix_start_time=rough_start,
                song_end_time=rough_end - rough_start,
                mix_end_time=rough_end,
            )
        )

        # Fine-tune alignment using the reference chunk
        refined_start, refined_end = self.fine_tune_alignment(
            song_chroma=song_chroma,
            mix_chroma=mix_chroma,
            sr=mix_sr,
            rough_start_time=rough_start,
            rough_end_time=rough_end,
            reference_chunk=reference_chunk,
        )

        return {
            "success": True,
            "song_path": song_path,
            "mix_path": mix_path,
            "rough_match": {"start": rough_start, "end": rough_end},
            "fine_tuned_match": {"start": refined_start, "end": refined_end},
            "reference_chunk": reference_chunk,
            "confidence_analysis": {
                "time_points": time_points,
                "certainty_scores": certainty_scores,
                "max_certainty": max(certainty_scores) if certainty_scores else 0,
                "avg_certainty": np.mean(certainty_scores) if certainty_scores else 0,
            },
            "precise_match": {
                "song_start": 0.0,
                "song_end": refined_end - refined_start,
                "mix_start": refined_start,
                "mix_end": refined_end,
            },
        }

    def generate_certainty_graph(
        self,
        time_points: list[float],
        certainty_scores: list[float],
    ):
        # Create the graph
        plt.figure(figsize=(12, 6))
        plt.plot(
            time_points, certainty_scores, "b-", linewidth=2, marker="o", markersize=4
        )
        plt.xlabel("Time (seconds) - Aligned to Song Start")
        plt.ylabel("Certainty Metric")
        plt.title("Audio Alignment Certainty Over Time")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Add some statistics
        max_certainty = max(certainty_scores) if certainty_scores else 0
        avg_certainty = np.mean(certainty_scores) if certainty_scores else 0
        plt.text(
            0.02,
            0.98,
            f"Max Certainty: {max_certainty:.2f}\nAvg Certainty: {avg_certainty:.2f}",
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Save the graph to a file and open it immediately
        plt.savefig("certainty_graph.png", dpi=300, bbox_inches="tight")
        print("Graph saved as 'certainty_graph.png'")

        self.logger.info(f"Graph generated with {len(time_points)} data points")
        self.logger.info(
            f"Max certainty: {max_certainty:.2f}, "
            f"Average certainty: {avg_certainty:.2f}"
        )

    def generate_alignedConfidences(
        self,
        song_chroma: np.ndarray,
        mix_chroma: np.ndarray,
        sr: int,
        song_start_time: float,
        mix_start_time: float,
        song_end_time: float,
        mix_end_time: float,
        n_chunks: int = 20,
        overlap_percentage: float = 0.9,
    ) -> Tuple[list[float], list[float], dict]:
        """
        Generate a graph showing certainty metric over time for aligned audio segments.

        Args:
            song_chroma: Source song chroma features
            mix_chroma: Mix chroma features
            sr: Sample rate
            song_start_time: Start time of song segment (in seconds)
            mix_start_time: Start time of mix segment (in seconds)
            song_end_time: End time of song segment (in seconds)
            mix_end_time: End time of mix segment (in seconds)
            n_chunks: Number of chunks to divide the audio into (default 20)
            overlap_percentage: Percentage overlap between consecutive chunks (default 0.5 = 50%)
        """
        self.logger.info("Generating certainty graph...")

        # Convert times to frames
        song_start_frame = librosa.time_to_frames(
            song_start_time, sr=sr, hop_length=self.config.hop_length
        )
        mix_start_frame = librosa.time_to_frames(
            mix_start_time, sr=sr, hop_length=self.config.hop_length
        )
        song_end_frame = librosa.time_to_frames(
            song_end_time, sr=sr, hop_length=self.config.hop_length
        )
        mix_end_frame = librosa.time_to_frames(
            mix_end_time, sr=sr, hop_length=self.config.hop_length
        )

        # Calculate the duration of the shorter segment to avoid out-of-bounds
        min_duration_frames = min(
            song_end_frame - song_start_frame, mix_end_frame - mix_start_frame
        )

        # Calculate chunk size based on number of chunks and overlap percentage
        # Formula: chunk_frames = min_duration_frames / (n_chunks - (n_chunks - 1) * overlap_percentage)
        # This accounts for the overlap reducing the effective coverage
        effective_chunks = n_chunks - (n_chunks - 1) * overlap_percentage
        chunk_frames = int(min_duration_frames / effective_chunks)

        # Calculate step size based on overlap percentage
        overlap_frames = int(chunk_frames * overlap_percentage)
        step_frames = chunk_frames - overlap_frames

        # Calculate the time offset (how much the song starts after the mix)
        time_offset = song_start_time - mix_start_time

        # Prepare data for plotting
        time_points = []
        certainty_scores = []

        # Extract the relevant segments
        song_segment = song_chroma[:, song_start_frame:song_end_frame]
        mix_segment = mix_chroma[:, mix_start_frame:mix_end_frame]

        # Debug: print segment info
        print(f"Song segment shape: {song_segment.shape}")
        print(f"Mix segment shape: {mix_segment.shape}")
        print(f"Time offset: {time_offset:.2f}s")
        print(f"Min duration frames: {min_duration_frames}")
        print(f"Number of chunks: {n_chunks}")
        print(f"Overlap percentage: {overlap_percentage:.1%}")
        print(f"Chunk frames: {chunk_frames}")
        print(f"Overlap frames: {overlap_frames}")
        print(f"Step frames: {step_frames}")

        # Store chunk information for fine-tuning analysis
        chunk_info = []

        # Slide through the segments with overlapping chunks
        current_frame = 0
        chunk_count = 0
        while current_frame + chunk_frames <= min_duration_frames:
            # Extract chunks
            song_chunk = song_segment[:, current_frame : current_frame + chunk_frames]
            mix_chunk = mix_segment[:, current_frame : current_frame + chunk_frames]

            # Calculate certainty using cross-correlation
            certainty = self._calculate_chunk_certainty(song_chunk, mix_chunk)

            # Calculate the aligned time (subtract the offset to align with song start)
            aligned_time = (
                librosa.frames_to_time(
                    current_frame + song_start_frame,
                    sr=sr,
                    hop_length=self.config.hop_length,
                )
                - time_offset
            )

            print(
                f"Chunk {chunk_count}: aligned_time={aligned_time:.2f}s, "
                f"certainty={certainty:.2f}"
            )

            time_points.append(aligned_time)
            certainty_scores.append(certainty)

            # Store chunk info for fine-tuning
            chunk_info.append(
                {
                    "chunk_id": chunk_count,
                    "aligned_time": aligned_time,
                    "certainty": certainty,
                    "song_start_frame": current_frame + song_start_frame,
                    "mix_start_frame": current_frame + mix_start_frame,
                    "chunk_frames": chunk_frames,
                }
            )

            current_frame += step_frames
            chunk_count += 1

        # Find the highest confidence chunk for reference alignment
        reference_chunk = self._find_reference_chunk(chunk_info)

        self.generate_certainty_graph(time_points, certainty_scores)

        return time_points, certainty_scores, reference_chunk

    def _calculate_chunk_certainty(
        self, song_chunk: np.ndarray, mix_chunk: np.ndarray
    ) -> float:
        """
        Calculate certainty metric between two audio chunks using cross-correlation.

        Args:
            song_chunk: Song chroma chunk
            mix_chunk: Mix chroma chunk

        Returns:
            Certainty score (higher = more certain)
        """
        # Normalize the chunks
        song_norm = (song_chunk - np.mean(song_chunk)) / (np.std(song_chunk) + 1e-8)
        mix_norm = (mix_chunk - np.mean(mix_chunk)) / (np.std(mix_chunk) + 1e-8)

        # Calculate cross-correlation
        correlation = correlate(mix_norm, song_norm, mode="valid", method="fft")
        time_correlation = np.sum(correlation, axis=0)

        best_match_frame = np.argmax(time_correlation)
        best_match_score = time_correlation[best_match_frame]

        # Return the maximum correlation value as certainty
        return float(best_match_score)

    def _find_reference_chunk(self, chunk_info: list[dict]) -> dict:
        """
        Find the chunk with the highest certainty score to use as reference.

        Args:
            chunk_info: List of chunk information dictionaries

        Returns:
            Dictionary containing reference chunk information
        """
        if not chunk_info:
            return {}

        # Find chunk with highest certainty
        reference_chunk = max(chunk_info, key=lambda x: x["certainty"])

        self.logger.info(
            f"Reference chunk found: ID {reference_chunk['chunk_id']} "
            f"at time {reference_chunk['aligned_time']:.2f}s "
            f"with certainty {reference_chunk['certainty']:.2f}"
        )

        return reference_chunk

    def fine_tune_alignment(
        self,
        song_chroma: np.ndarray,
        mix_chroma: np.ndarray,
        sr: int,
        rough_start_time: float,
        rough_end_time: float,
        reference_chunk: dict,
    ) -> Tuple[float, float]:
        """
        Fine-tune alignment using the highest confidence chunk as reference.

        Args:
            song_chroma: Source song chroma features
            mix_chroma: Mix chroma features
            sr: Sample rate
            rough_start_time: Initial rough estimate start time
            rough_end_time: Initial rough estimate end time
            reference_chunk: Reference chunk with highest confidence

        Returns:
            Tuple of (refined_start_time, refined_end_time)
        """
        print(reference_chunk)
        if not reference_chunk:
            self.logger.warning(
                "No reference chunk provided, returning rough estimates"
            )
            return rough_start_time, rough_end_time

        self.logger.info("Fine-tuning alignment using reference chunk...")

        # Extract chunk parameters
        chunk_frames = reference_chunk["chunk_frames"]
        song_chunk_start_frame = reference_chunk["song_start_frame"]
        mix_chunk_start_frame = reference_chunk["mix_start_frame"]

        # Center a window of 3 chunks in the mix around the reference chunk
        mix_window_start = max(0, mix_chunk_start_frame - chunk_frames)
        mix_window_end = min(
            mix_chroma.shape[1], mix_chunk_start_frame + chunk_frames * 2
        )

        # Extract the song chunk and mix window
        song_chunk = song_chroma[
            :, song_chunk_start_frame : song_chunk_start_frame + chunk_frames
        ]
        mix_window = mix_chroma[:, mix_window_start:mix_window_end]

        # Use find_rough_match with the chunk and window
        chunkOffsetStart, chunkOffsetEnd = self.find_rough_match(
            song_chunk, mix_window, sr
        )
        print(librosa.frames_to_time(chunk_frames, sr=sr))
        chunkOffsetStart -= librosa.frames_to_time(chunk_frames, sr=sr)
        chunkOffsetEnd -= librosa.frames_to_time(chunk_frames, sr=sr)
        print(chunkOffsetStart, chunkOffsetEnd)
        refined_start_time = chunkOffsetStart + mix_chunk_start_frame
        refined_end_time = chunkOffsetEnd + mix_chunk_start_frame

        return rough_start_time, rough_end_time


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

        # Show reference chunk information
        if "reference_chunk" in result and result["reference_chunk"]:
            ref = result["reference_chunk"]
            print(
                f"Reference chunk: ID {ref['chunk_id']} at {ref['aligned_time']:.2f}s "
                + f"with certainty {ref['certainty']:.2f}"
            )

        # Show confidence analysis
        if "confidence_analysis" in result:
            analysis = result["confidence_analysis"]
            print(
                f"Confidence analysis: Max={analysis['max_certainty']:.2f}, "
                + f"Avg={analysis['avg_certainty']:.2f}"
            )

        print("\n--- Certainty Graph Generated ---")
        print("Graph saved as 'certainty_graph.png'")
    else:
        print(f"\nRecognition failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
