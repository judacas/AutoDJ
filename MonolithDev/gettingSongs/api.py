"""FastAPI application exposing playlist conversion utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .get_playlist_songs import SpotifyPlaylistService
from .playlist_pipeline import PlaylistPipeline
from .youtube_utils import QueryType

app = FastAPI(
    title="AutoDJ Playlist Service",
    description=(
        "Endpoints for converting Spotify playlists and retrieving their tracks."
    ),
    version="1.0.0",
)

_pipeline = PlaylistPipeline()
_spotify_service = SpotifyPlaylistService()


class PlaylistConversionRequest(BaseModel):
    """Input payload for launching the playlist conversion pipeline."""

    playlist_url: str = Field(..., description="Spotify playlist URL or URI")
    mixes_per_track: int = Field(
        10,
        ge=0,
        description="Number of mix downloads to attempt per track.",
    )
    download_songs: bool = Field(
        True, description="Whether to download the original tracks."
    )
    download_mixes: bool = Field(
        True, description="Whether to download DJ mixes."
    )


class PlaylistConversionResponse(BaseModel):
    """Response returned when a playlist conversion is triggered."""

    playlist_id: str
    total_tracks: int
    playlist_json: Path
    download_summaries: Dict[str, Dict]


class PlaylistTracksResponse(BaseModel):
    """Response containing track information for a Spotify playlist."""

    playlist_id: str
    total_tracks: int
    tracks: List[Dict[str, object]]


@app.post("/playlist/convert", response_model=PlaylistConversionResponse)
async def convert_playlist(request: PlaylistConversionRequest) -> PlaylistConversionResponse:
    """Trigger the AutoDJ pipeline for the provided Spotify playlist."""

    try:
        result = _pipeline.run(
            request.playlist_url,
            mixes_per_track=request.mixes_per_track,
            download_songs=request.download_songs,
            download_mixes=request.download_mixes,
        )
    except ValueError as exc:  # Validation or download errors surface as 400s
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    summaries = {
        (query_type.value if isinstance(query_type, QueryType) else str(query_type)): summary
        for query_type, summary in result.download_summaries.items()
    }

    return PlaylistConversionResponse(
        playlist_id=result.playlist_id,
        total_tracks=result.playlist.total,
        playlist_json=result.playlist_json,
        download_summaries=summaries,
    )


@app.get("/playlist/tracks", response_model=PlaylistTracksResponse)
async def get_playlist_tracks(playlist_url: str) -> PlaylistTracksResponse:
    """Return the tracks contained in the requested Spotify playlist."""

    playlist = _spotify_service.fetch_playlist(playlist_url)
    if playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found or empty")

    playlist_id = _spotify_service.extract_playlist_id(playlist_url)
    tracks: List[Dict[str, object]] = []
    for item in playlist.items:
        if item.track is None:
            continue
        track = item.track
        tracks.append(
            {
                "name": track.name,
                "artists": [artist.name for artist in track.artists],
                "album": track.album.name,
                "duration_ms": track.duration_ms,
                "duration": track.duration_formatted,
                "explicit": track.explicit,
                "preview_url": track.preview_url,
                "spotify_url": (track.external_urls or {}).get("spotify"),
                "spotify_uri": track.uri,
                "spotify_id": track.id,
                "added_at": item.added_at,
            }
        )

    return PlaylistTracksResponse(
        playlist_id=playlist_id,
        total_tracks=playlist.total,
        tracks=tracks,
    )
