"""
Pydantic models for Spotify data structures.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Artist(BaseModel):
    """Spotify artist model."""

    name: str = Field(..., description="Artist name")
    id: Optional[str] = Field(None, description="Spotify artist ID")
    external_urls: Optional[dict] = Field(
        None, description="External URLs for the artist"
    )
    href: Optional[str] = Field(None, description="Spotify API href for the artist")
    type: Optional[str] = Field(None, description="Object type (usually 'artist')")
    uri: Optional[str] = Field(None, description="Spotify URI for the artist")


class Album(BaseModel):
    """Spotify album model."""

    name: str = Field(..., description="Album name")
    id: Optional[str] = Field(None, description="Spotify album ID")
    album_type: Optional[str] = Field(
        None, description="Album type (album, single, compilation)"
    )
    artists: Optional[List[Artist]] = Field(None, description="Album artists")
    external_urls: Optional[dict] = Field(
        None, description="External URLs for the album"
    )
    href: Optional[str] = Field(None, description="Spotify API href for the album")
    images: Optional[List[dict]] = Field(None, description="Album cover images")
    release_date: Optional[str] = Field(None, description="Album release date")
    release_date_precision: Optional[str] = Field(
        None, description="Release date precision"
    )
    total_tracks: Optional[int] = Field(None, description="Total tracks in album")
    type: Optional[str] = Field(None, description="Object type (usually 'album')")
    uri: Optional[str] = Field(None, description="Spotify URI for the album")


class Track(BaseModel):
    """Spotify track model."""

    name: str = Field(..., description="Track name")
    id: Optional[str] = Field(None, description="Spotify track ID")
    artists: List[Artist] = Field(..., description="Track artists")
    album: Album = Field(..., description="Track album")
    duration_ms: int = Field(..., description="Track duration in milliseconds")
    explicit: Optional[bool] = Field(None, description="Whether the track is explicit")
    external_ids: Optional[dict] = Field(None, description="External IDs (ISRC, etc.)")
    external_urls: Optional[dict] = Field(
        None, description="External URLs for the track"
    )
    href: Optional[str] = Field(None, description="Spotify API href for the track")
    is_local: Optional[bool] = Field(None, description="Whether the track is local")
    is_playable: Optional[bool] = Field(
        None, description="Whether the track is playable"
    )
    popularity: Optional[int] = Field(None, description="Track popularity (0-100)")
    preview_url: Optional[str] = Field(None, description="Preview URL for the track")
    track_number: Optional[int] = Field(None, description="Track number in album")
    type: Optional[str] = Field(None, description="Object type (usually 'track')")
    uri: Optional[str] = Field(None, description="Spotify URI for the track")

    @property
    def duration_formatted(self) -> str:
        """Return formatted duration as MM:SS."""
        minutes = self.duration_ms // 60000
        seconds = (self.duration_ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"

    @property
    def artist_names(self) -> str:
        """Return comma-separated artist names."""
        return ", ".join([artist.name for artist in self.artists])

    def __str__(self) -> str:
        """Return formatted string representation of the track."""
        return f"{self.name} - {self.artist_names} ({self.duration_formatted})"

    def to_detailed_string(self) -> str:
        """Return detailed string representation with album info."""
        return f"{self.name}\n     Artist(s): {self.artist_names}\n     Album: {self.album.name}\n     Duration: {self.duration_formatted}"

    @property
    def song_details_formatted(self) -> str:
        """Return formatted song details for DJ LLM prompts."""
        explicit_text = "Yes" if self.explicit else "No"
        popularity_text = (
            f"{self.popularity}/100" if self.popularity is not None else "N/A"
        )

        return f"""**Song Details:**
- Title: {self.name}
- Artist(s): {self.artist_names}
- Album: {self.album.name}
- Release Year: {self.album.release_date[:4] if self.album.release_date and len(self.album.release_date) >= 4 else "N/A"}
- Duration: {self.duration_formatted}
- Popularity Score: {popularity_text}
- Explicit: {explicit_text}"""


class PlaylistTrack(BaseModel):
    """Spotify playlist track item model."""

    track: Optional[Track] = Field(None, description="The track object")
    added_at: Optional[str] = Field(
        None, description="When the track was added to playlist"
    )
    added_by: Optional[dict] = Field(None, description="User who added the track")
    is_local: Optional[bool] = Field(None, description="Whether the track is local")
    primary_color: Optional[str] = Field(
        None, description="Primary color for the track"
    )
    video_thumbnail: Optional[dict] = Field(
        None, description="Video thumbnail if available"
    )

    def __str__(self) -> str:
        """Return string representation of the playlist track."""
        return str(self.track) if self.track else "No track data available"


class Playlist(BaseModel):
    """Spotify playlist model."""

    id: str = Field(..., description="Spotify playlist ID")
    name: str = Field(..., description="Playlist name")
    description: Optional[str] = Field(None, description="Playlist description")
    collaborative: Optional[bool] = Field(
        None, description="Whether playlist is collaborative"
    )
    external_urls: Optional[dict] = Field(
        None, description="External URLs for the playlist"
    )
    followers: Optional[dict] = Field(None, description="Follower count and href")
    href: Optional[str] = Field(None, description="Spotify API href for the playlist")
    images: Optional[List[dict]] = Field(None, description="Playlist cover images")
    owner: Optional[dict] = Field(None, description="Playlist owner information")
    public: Optional[bool] = Field(None, description="Whether playlist is public")
    snapshot_id: Optional[str] = Field(None, description="Playlist snapshot ID")
    tracks: Optional["PlaylistResponse"] = Field(
        None, description="Paginated playlist tracks response"
    )
    total_tracks: Optional[int] = Field(None, description="Total number of tracks")
    type: Optional[str] = Field(None, description="Object type (usually 'playlist')")
    uri: Optional[str] = Field(None, description="Spotify URI for the playlist")

    @property
    def track_count(self) -> int:
        """Return the number of tracks in the playlist."""
        if self.tracks:
            # Count non-null tracks from items
            return len([item for item in self.tracks.items if item.track is not None])
        # Fall back to total from tracks response or total_tracks field
        return (self.tracks.total if self.tracks else None) or self.total_tracks or 0


class PlaylistResponse(BaseModel):
    """Response model for playlist tracks API call."""

    href: Optional[str] = Field(None, description="API href for the response")
    items: List[PlaylistTrack] = Field(..., description="List of playlist track items")
    limit: Optional[int] = Field(None, description="Response limit")
    next: Optional[str] = Field(None, description="Next page URL")
    offset: Optional[int] = Field(None, description="Response offset")
    previous: Optional[str] = Field(None, description="Previous page URL")
    total: int = Field(..., description="Total number of tracks")

    def __str__(self) -> str:
        """Return string representation of the playlist response."""
        return f"PlaylistResponse(total={self.total}, items={len(self.items)})"
