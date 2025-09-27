#!/usr/bin/env python3
"""High level orchestration for the AutoDJ playlist pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from logging_config import get_module_logger

from get_playlist_songs import SpotifyPlaylistService
from models import PlaylistResponse
from youtube_utils import QueryType, YouTubeDownloader

logger = get_module_logger(__name__)


@dataclass
class PipelineResult:
    """Container with the artefacts produced by :class:`PlaylistPipeline`."""

    playlist_id: str
    playlist: PlaylistResponse
    playlist_json: Path
    download_summaries: Dict[QueryType, dict]


class PlaylistPipeline:
    """Coordinate fetching playlist metadata and downloading related audio."""

    def __init__(
        self,
        spotify_service: Optional[SpotifyPlaylistService] = None,
        downloader: Optional[YouTubeDownloader] = None,
    ) -> None:
        self.spotify_service = spotify_service or SpotifyPlaylistService()
        self.downloader = downloader or YouTubeDownloader()

    def run(
        self,
        playlist_uri: str,
        mixes_per_track: int = 10,
        download_songs: bool = True,
        download_mixes: bool = True,
    ) -> PipelineResult:
        """Execute the playlist workflow from Spotify fetch to audio downloads."""

        playlist = self.spotify_service.fetch_playlist(playlist_uri)
        if not playlist:
            raise ValueError("Unable to fetch playlist from Spotify")

        playlist_id = self.spotify_service.extract_playlist_id(playlist_uri)
        playlist_path = self.spotify_service.save_playlist_to_json(
            playlist, playlist_id
        )

        summaries: Dict[QueryType, dict] = {}
        if download_songs:
            logger.info("Starting download of original tracks")
            summaries[QueryType.SONG] = self._download_with_handling(
                playlist_id, QueryType.SONG, None
            )

        if download_mixes:
            logger.info("Starting download of DJ mixes")
            summaries[QueryType.MIX] = self._download_with_handling(
                playlist_id, QueryType.MIX, mixes_per_track
            )

        return PipelineResult(
            playlist_id=playlist_id,
            playlist=playlist,
            playlist_json=playlist_path,
            download_summaries=summaries,
        )

    def _download_with_handling(
        self,
        playlist_id: str,
        query_type: QueryType,
        mixes_per_track: Optional[int],
    ) -> dict:
        try:
            summary = self.downloader.download_playlist(
                playlist_id,
                query_type,
                max_results_per_track=mixes_per_track,
            )
        except Exception as exc:
            raise ValueError(
                f"Failed to download {query_type.value} results for playlist {playlist_id}"
            ) from exc

        return summary.as_dict()
