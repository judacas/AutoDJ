#!/usr/bin/env python3
"""Shared utilities for downloading playlist tracks and mixes from YouTube."""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

import yt_dlp

from dj_LLM import DJQueryGenerator
from logging_config import get_module_logger
import database
from azure_blob_storage import AzureBlobStorage, AzureBlobStorageError
from models import Track

logger = get_module_logger(__name__)


class QueryType(str, Enum):
    """Types of supported search strategies."""

    SONG = "song"
    MIX = "mix"


@dataclass
class DownloadSummary:
    """Keep track of download metrics for reporting."""

    total_tracks: int
    requested_downloads: int = 0
    successful_downloads: int = 0
    skipped_downloads: int = 0
    failed_downloads: int = 0

    def as_dict(self) -> dict:
        return {
            "total_tracks": self.total_tracks,
            "requested_downloads": self.requested_downloads,
            "successful_downloads": self.successful_downloads,
            "skipped_downloads": self.skipped_downloads,
            "failed_downloads": self.failed_downloads,
        }


def get_tracks_from_database(playlist_id: str) -> Optional[List[Track]]:
    """Load playlist tracks from the database."""

    tracks = database.fetch_tracks_for_playlist(playlist_id)
    if not tracks:
        logger.error(
            "No tracks found for playlist %s. Have you fetched it with playlist_full_converter?",
            playlist_id,
        )
        return None

    logger.info(f"Found {len(tracks)} tracks in playlist")
    return tracks


def extract_youtube_id(video_url: str) -> str:
    """Extract a YouTube video ID from a URL."""

    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)",
        r"youtube\.com/v/([^&\n?#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    return "unknown_id"


def has_existing_download(
    playlist_id: str, youtube_id: str, query_type: QueryType
) -> bool:
    """Check the database for an existing download record."""

    try:
        return database.download_exists(playlist_id, youtube_id, query_type)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning(
            "Unable to determine if %s is already stored for playlist %s: %s",
            youtube_id,
            playlist_id,
            exc,
        )
        return False


def download_audio_from_youtube(
    video_url: str, output_dir: Path | str = "downloads"
) -> Optional[str]:
    """Download audio as MP3 using ``yt-dlp`` with idempotent filenames."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    youtube_id = extract_youtube_id(video_url)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_path / f"{youtube_id}__%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "postprocessor_args": ["-ar", "44100"],
        "extractaudio": True,
        "audioformat": "mp3",
    }

    try:
        logger.info(f"Downloading audio from: {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        id_files = list(output_path.glob(f"{youtube_id}__*"))
        if id_files:
            downloaded_file = max(id_files, key=lambda f: f.stat().st_mtime)
            return str(downloaded_file)
        logger.warning("Download completed but file not found")
        return None
    except Exception as exc:  # pragma: no cover - yt_dlp issues
        logger.error(f"Error downloading audio: {exc}")
        return None


class YouTubeDownloader:
    """Handle searching for and downloading tracks from YouTube."""

    def __init__(
        self,
        output_dir: str = "downloads",
        storage: Optional[AzureBlobStorage] = None,
    ) -> None:
        self._staging_root = Path(output_dir)
        self._staging_root.mkdir(parents=True, exist_ok=True)
        self._mix_generator: Optional[DJQueryGenerator] = None
        try:
            self.storage = storage or AzureBlobStorage.from_env()
        except AzureBlobStorageError as exc:
            raise RuntimeError(
                "Azure Blob Storage is not configured correctly."
            ) from exc

    def download_playlist(
        self,
        playlist_id: str,
        query_type: QueryType,
        max_results_per_track: Optional[int] = None,
    ) -> DownloadSummary:
        tracks = get_tracks_from_database(playlist_id)
        if not tracks:
            raise ValueError("Failed to load tracks from the database.")

        per_track_limit = max_results_per_track or (
            10 if query_type == QueryType.MIX else 1
        )
        summary = DownloadSummary(total_tracks=len(tracks))

        with tempfile.TemporaryDirectory(dir=self._staging_root) as staging_dir:
            staging_path = Path(staging_dir)
            target_dir = staging_path / (
                "mixes" if query_type == QueryType.MIX else "originals"
            )
            target_dir.mkdir(parents=True, exist_ok=True)

            for index, track in enumerate(tracks, start=1):
                logger.info(f"\n--- Track {index}/{len(tracks)}: {track} ---")
                self._download_for_track(
                    playlist_id,
                    track,
                    query_type,
                    per_track_limit,
                    summary,
                    target_dir,
                )

        return summary

    def _download_for_track(
        self,
        playlist_id: str,
        track: Track,
        query_type: QueryType,
        per_track_limit: int,
        summary: DownloadSummary,
        target_dir: Path,
    ) -> None:
        queries = self._create_search_queries(track, query_type)
        downloads_for_track = 0

        for query_index, query in enumerate(queries, start=1):
            if downloads_for_track >= per_track_limit:
                break

            logger.info(
                f"Trying query {query_index}/{len(queries)} for '{track.name}': {query}"
            )
            results = self._search_youtube(query)
            if not results:
                logger.warning(f"No search results found for query {query_index}")
                continue

            for result in results:
                if downloads_for_track >= per_track_limit:
                    break

                video_url = result.get("webpage_url") or result.get("url")
                if not video_url:
                    continue

                youtube_id = extract_youtube_id(video_url)
                summary.requested_downloads += 1

                if has_existing_download(playlist_id, youtube_id, query_type):
                    logger.info(
                        f"⏭️  Already downloaded, skipping: {result.get('title', 'Unknown title')}"
                    )
                    summary.skipped_downloads += 1
                    continue

                file_path = download_audio_from_youtube(video_url, target_dir)
                if file_path:
                    try:
                        blob_url = self.storage.upload_file(
                            playlist_id=playlist_id,
                            query_type=query_type.value,
                            local_path=Path(file_path),
                        )
                    except Exception as exc:  # pragma: no cover - Azure SDK runtime issues
                        logger.error(
                            "❌ Failed to upload %s to Azure Blob Storage: %s",
                            file_path,
                            exc,
                        )
                        summary.failed_downloads += 1
                        continue

                    logger.info(f"✅ Successfully uploaded to Azure: {blob_url}")
                    summary.successful_downloads += 1
                    downloads_for_track += 1
                    database.record_download(
                        playlist_id=playlist_id,
                        track_id=track.id or track.uri or f"track_{track.name}",
                        query_type=query_type,
                        youtube_id=youtube_id,
                        title=result.get("title"),
                        file_uri=blob_url,
                    )
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except OSError:
                        logger.debug("Unable to remove temporary file %s", file_path)
                else:
                    logger.error(f"❌ Failed to download: {video_url}")
                    summary.failed_downloads += 1

            if downloads_for_track < per_track_limit:
                logger.debug(
                    f"Only {downloads_for_track} downloads completed for '{track.name}' so far."
                )

        if downloads_for_track == 0:
            logger.error(f"❌ Failed to download any results for: {track}")

    def _create_search_queries(self, track: Track, query_type: QueryType) -> List[str]:
        if query_type == QueryType.SONG:
            return [
                (
                    f"{track.artist_names} - {track.name} "
                    "-video -karaoke -cover -instrumental -remix -live -acapella -concert -lyrics"
                )
            ]

        if query_type == QueryType.MIX:
            if self._mix_generator is None:
                try:
                    self._mix_generator = DJQueryGenerator()
                except Exception as exc:
                    logger.error("Unable to initialise DJ mix query generator: %s", exc)
                    raise RuntimeError(
                        "Missing configuration for DJ mix queries"
                    ) from exc
            return self._mix_generator.generate_queries(track).queries

        raise ValueError(f"Unknown query_type: {query_type}")

    @staticmethod
    def _search_youtube(query: str) -> List[dict]:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "default_search": "ytsearch1:",
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        except Exception as exc:  # pragma: no cover - yt_dlp issues
            logger.warning(f"Error executing search query '{query}': {exc}")
            return []

        entries = info.get("entries") if info else None
        return entries or []


def download_tracks_from_playlist(
    playlist_id: str,
    query_type: QueryType = QueryType.SONG,
    max_results_per_track: Optional[int] = None,
) -> Optional[dict]:
    """Public helper used by CLI scripts for backwards compatibility."""

    downloader = YouTubeDownloader()
    try:
        summary = downloader.download_playlist(
            playlist_id, query_type, max_results_per_track=max_results_per_track
        )
    except (ValueError, RuntimeError) as exc:
        logger.error(str(exc))
        return None

    return summary.as_dict()


def print_download_summary(
    summary: dict | DownloadSummary, label: str = "Tracks"
) -> None:
    """Log a download summary to stdout."""

    if isinstance(summary, DownloadSummary):
        summary_dict = summary.as_dict()
    else:
        summary_dict = summary

    print(f"{'=' * 50}")
    print(f"DOWNLOAD SUMMARY - {label.upper()}")
    print(f"{'=' * 50}")
    print(f"Total tracks processed: {summary_dict['total_tracks']}")
    print(f"Requested downloads: {summary_dict['requested_downloads']}")
    print(f"✅ Successfully downloaded: {summary_dict['successful_downloads']}")
    print(f"⏭️  Skipped (already downloaded): {summary_dict['skipped_downloads']}")
    print(f"❌ Failed: {summary_dict['failed_downloads']}")
    print(f"{'=' * 50}")


def main() -> None:  # pragma: no cover - convenience CLI
    import sys

    if len(sys.argv) != 2:
        logger.error("Usage: python youtube_utils.py <playlist_id>")
        sys.exit(1)

    playlist_id = sys.argv[1]
    summary = download_tracks_from_playlist(playlist_id, QueryType.SONG)
    if summary:
        print_download_summary(summary)


if __name__ == "__main__":  # pragma: no cover - CLI behaviour
    main()
