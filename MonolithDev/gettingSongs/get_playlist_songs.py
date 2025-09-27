#!/usr/bin/env python3
"""Utilities for fetching and persisting Spotify playlist metadata."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Optional

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from logging_config import get_module_logger
from models import PlaylistResponse, PlaylistTrack

# Set up logger for this module
logger = get_module_logger(__name__)


class SpotifyPlaylistService:
    """High-level helper for working with Spotify playlists."""

    def __init__(self, client: Optional[spotipy.Spotify] = None) -> None:
        self._client: Optional[spotipy.Spotify] = client

    @staticmethod
    def extract_playlist_id(playlist_uri: str) -> str:
        """Normalize any Spotify playlist reference into its bare playlist ID."""
        if playlist_uri.startswith("spotify:playlist:"):
            return playlist_uri.split(":")[-1]
        if "spotify.com/playlist/" in playlist_uri:
            return playlist_uri.split("/")[-1].split("?")[0]
        return playlist_uri

    def fetch_playlist(self, playlist_uri: str) -> Optional[PlaylistResponse]:
        """Fetch the complete playlist response from Spotify."""
        playlist_id = self.extract_playlist_id(playlist_uri)
        try:
            aggregated_response = self._collect_paginated_tracks(playlist_id)
        except spotipy.exceptions.SpotifyException as exc:  # pragma: no cover - network
            logger.error(f"Spotify API error: {exc}")
            return None
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(f"Unexpected error fetching playlist: {exc}")
            return None

        try:
            playlist_response = PlaylistResponse.model_validate(aggregated_response)
        except Exception as exc:
            logger.error(f"Error parsing playlist response: {exc}")
            return None

        if not playlist_response.items:
            logger.warning("No songs found in this playlist.")
            return None

        return playlist_response

    def save_playlist_to_json(
        self,
        playlist_response: PlaylistResponse,
        playlist_id: str,
        output_dir: str = "output",
    ) -> Path:
        """Persist the playlist to JSON using the service's serialization strategy."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / f"playlist_{playlist_id}.json"
        filepath.write_text(
            playlist_response.model_dump_json(indent=2), encoding="utf-8"
        )

        logger.info(f"Playlist data saved to: {filepath}")
        return filepath

    def log_playlist(self, playlist_response: PlaylistResponse) -> None:
        """Pretty-print playlist contents using the configured logger."""
        logger.info("-" * 50)
        for index, playlist_track in enumerate(
            self._iter_tracks(playlist_response), start=1
        ):
            if playlist_track.track is None:
                logger.info(f"{index:3d}. [No track data]")
                continue
            logger.info(f"{index:3d}. {playlist_track.track.to_detailed_string()}")
        logger.info(f"Total tracks in playlist: {playlist_response.total}")

    def _create_client(self) -> spotipy.Spotify:
        credentials = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
        )
        return spotipy.Spotify(client_credentials_manager=credentials)

    def _collect_paginated_tracks(self, playlist_id: str) -> dict:
        all_tracks: list[dict] = []
        offset = 0
        limit = 100  # Spotify's maximum per request
        last_response: Optional[dict] = None

        while True:
            raw_results = self.client.playlist_tracks(
                playlist_id, limit=limit, offset=offset
            )
            if raw_results:
                last_response = raw_results
                items = raw_results.get("items") or []
                all_tracks.extend(items)

            if not raw_results or not raw_results.get("next"):
                break

            offset += limit

        return {
            "href": last_response.get("href", "") if last_response else "",
            "items": all_tracks,
            "limit": last_response.get("limit", limit) if last_response else limit,
            "next": None,
            "offset": 0,
            "previous": None,
            "total": len(all_tracks),
        }

    @staticmethod
    def _iter_tracks(playlist_response: PlaylistResponse) -> Iterable[PlaylistTrack]:
        return (item for item in playlist_response.items if item.track is not None)

    @property
    def client(self) -> spotipy.Spotify:
        if self._client is None:
            self._client = self._create_client()
        return self._client


def get_playlist_songs(
    playlist_uri: str, service: Optional[SpotifyPlaylistService] = None
) -> Optional[PlaylistResponse]:
    """Compatibility wrapper that fetches songs using :class:`SpotifyPlaylistService`."""
    service = service or SpotifyPlaylistService()
    return service.fetch_playlist(playlist_uri)


def save_playlist_to_json(
    playlist_response: PlaylistResponse,
    playlist_id: str,
    output_dir: str = "output",
    service: Optional[SpotifyPlaylistService] = None,
) -> Path:
    """Proxy to :meth:`SpotifyPlaylistService.save_playlist_to_json` for backwards compatibility."""
    service = service or SpotifyPlaylistService()
    return service.save_playlist_to_json(playlist_response, playlist_id, output_dir)


def log_playlist_songs(
    playlist_response: PlaylistResponse,
    service: Optional[SpotifyPlaylistService] = None,
) -> None:
    """Compatibility wrapper around :meth:`SpotifyPlaylistService.log_playlist`."""
    service = service or SpotifyPlaylistService()
    service.log_playlist(playlist_response)


def main() -> None:
    """CLI entry point used when running the module directly."""
    if len(sys.argv) != 2:
        logger.error("Usage: python get_playlist_songs.py <playlist_uri>")
        logger.error("\nExamples:")
        logger.error(
            "  python get_playlist_songs.py spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"
        )
        logger.error(
            "  python get_playlist_songs.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        )
        sys.exit(1)

    playlist_uri = sys.argv[1]
    service = SpotifyPlaylistService()
    playlist_id = service.extract_playlist_id(playlist_uri)
    logger.info(f"Fetching songs from playlist: {playlist_id}")

    playlist_response = service.fetch_playlist(playlist_uri)
    if not playlist_response:
        logger.error("Failed to fetch playlist data.")
        sys.exit(1)

    service.log_playlist(playlist_response)
    service.save_playlist_to_json(playlist_response, playlist_id)


if __name__ == "__main__":
    main()
