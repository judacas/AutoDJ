"""FastAPI application exposing playlist conversion utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    #allow_origins=["*"],  # Allow all origins for simplicity; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    playlist_name: str
    playlist_description: str
    playlist_images: List[Dict[str, object]]  # Allow mixed types for width/height
    playlist_owner: Dict[str, str]
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
    
    # Get playlist metadata from Spotify API
    playlist_info: dict = {
        "name": f"Playlist {playlist_id[:8]}...",
        "description": "",
        "images": [],
        "owner": {"display_name": "Unknown"}
    }
    try:
        client = _spotify_service._create_client()
        fetched_info = client.playlist(playlist_id, fields="name,description,images,owner")
        if fetched_info:
            playlist_info = fetched_info
    except Exception as exc:
        # If we can't get metadata, use defaults (already set above)
        pass
    
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
                "album_images": track.album.images or [],
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
        playlist_name=playlist_info.get("name", f"Playlist {playlist_id[:8]}..."),
        playlist_description=playlist_info.get("description", ""),
        playlist_images=[
            {
                "url": img["url"], 
                "width": img.get("width"), 
                "height": img.get("height")
            }
            for img in playlist_info.get("images", [])
        ],
        playlist_owner={
            "display_name": playlist_info.get("owner", {}).get("display_name", "Unknown"),
            "id": playlist_info.get("owner", {}).get("id", ""),
        },
        total_tracks=playlist.total,
        tracks=tracks,
    )
