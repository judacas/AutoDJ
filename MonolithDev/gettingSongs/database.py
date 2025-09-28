"""Database utilities for persisting Spotify playlist metadata."""

from __future__ import annotations

import hashlib
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Iterable, List, Optional, Union

from config import get_database_url
from logging_config import get_module_logger
from models import Album as AlbumModel
from models import Artist as ArtistModel
from models import PlaylistResponse
from models import Track as TrackModel
from pydantic import ValidationError
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    delete,
    inspect,
    select,
)
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)

logger = get_module_logger(__name__)

if TYPE_CHECKING:  # pragma: no cover - runtime import avoided for circular deps
    from youtube_utils import QueryType

Base = declarative_base()


class Playlist(Base):
    __tablename__ = "playlists"

    spotify_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    collaborative: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    public: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    snapshot_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    href: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tracks: Mapped[List["PlaylistTrack"]] = relationship(
        "PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan"
    )
    downloads: Mapped[List["Download"]] = relationship(
        "Download", back_populates="playlist", cascade="all, delete-orphan"
    )


class Album(Base):
    __tablename__ = "albums"

    spotify_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    album_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    release_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    release_date_precision: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_tracks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    href: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tracks: Mapped[List["Track"]] = relationship("Track", back_populates="album")
    artists: Mapped[List["AlbumArtist"]] = relationship(
        "AlbumArtist", back_populates="album", cascade="all, delete-orphan"
    )


class Artist(Base):
    __tablename__ = "artists"

    spotify_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    href: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tracks: Mapped[List["TrackArtist"]] = relationship(
        "TrackArtist", back_populates="artist", cascade="all, delete-orphan"
    )
    albums: Mapped[List["AlbumArtist"]] = relationship(
        "AlbumArtist", back_populates="artist", cascade="all, delete-orphan"
    )


class Track(Base):
    __tablename__ = "tracks"

    spotify_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    album_id: Mapped[str] = mapped_column(
        ForeignKey("albums.spotify_id"), nullable=False
    )
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    explicit: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_playable: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_local: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    popularity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preview_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    track_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_id_isrc: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    album: Mapped[Album] = relationship("Album", back_populates="tracks")
    artists: Mapped[List["TrackArtist"]] = relationship(
        "TrackArtist", back_populates="track", cascade="all, delete-orphan"
    )
    playlist_items: Mapped[List["PlaylistTrack"]] = relationship(
        "PlaylistTrack", back_populates="track", cascade="all, delete-orphan"
    )
    downloads: Mapped[List["Download"]] = relationship(
        "Download", back_populates="track", cascade="all, delete-orphan"
    )


class TrackArtist(Base):
    __tablename__ = "track_artists"

    track_id: Mapped[str] = mapped_column(
        ForeignKey("tracks.spotify_id", ondelete="CASCADE"), primary_key=True
    )
    artist_id: Mapped[str] = mapped_column(
        ForeignKey("artists.spotify_id", ondelete="CASCADE"), primary_key=True
    )
    artist_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    track: Mapped[Track] = relationship("Track", back_populates="artists")
    artist: Mapped[Artist] = relationship("Artist", back_populates="tracks")


class AlbumArtist(Base):
    __tablename__ = "album_artists"
    __table_args__ = (
        UniqueConstraint("album_id", "artist_id", name="uq_album_artist"),
    )

    album_id: Mapped[str] = mapped_column(
        ForeignKey("albums.spotify_id", ondelete="CASCADE"), primary_key=True
    )
    artist_id: Mapped[str] = mapped_column(
        ForeignKey("artists.spotify_id", ondelete="CASCADE"), primary_key=True
    )
    artist_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    album: Mapped[Album] = relationship("Album", back_populates="artists")
    artist: Mapped[Artist] = relationship("Artist", back_populates="albums")


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[str] = mapped_column(
        ForeignKey("playlists.spotify_id", ondelete="CASCADE"), nullable=False
    )
    track_id: Mapped[str] = mapped_column(
        ForeignKey("tracks.spotify_id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    added_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    added_by_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    added_by_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_local: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    playlist: Mapped[Playlist] = relationship("Playlist", back_populates="tracks")
    track: Mapped[Track] = relationship("Track", back_populates="playlist_items")


class Download(Base):
    __tablename__ = "downloads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[str] = mapped_column(
        ForeignKey("playlists.spotify_id", ondelete="CASCADE"), nullable=False
    )
    track_id: Mapped[str] = mapped_column(
        ForeignKey("tracks.spotify_id", ondelete="CASCADE"), nullable=False
    )
    query_type: Mapped[str] = mapped_column(String, nullable=False)
    youtube_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    playlist: Mapped[Playlist] = relationship("Playlist", back_populates="downloads")
    track: Mapped[Track] = relationship("Track", back_populates="downloads")


_engine = None
_SessionLocal: Optional[sessionmaker] = None


def _stable_id(prefix: str, parts: Iterable[Optional[str]]) -> str:
    concatenated = "::".join(part or "" for part in parts)
    digest = hashlib.sha256(concatenated.encode("utf-8")).hexdigest()
    return f"{prefix}_{digest}"


def _ensure_identifier(prefix: str, *candidates: Optional[str]) -> str:
    for candidate in candidates:
        if candidate:
            return candidate
    return _stable_id(prefix, candidates)


def _mask_database_url(url: str) -> str:
    """Mask sensitive information in database URL for safe logging."""
    if not url or '@' not in url:
        return url
    
    try:
        parts = url.split('@')
        if len(parts) != 2:
            return url
        
        user_pass_part = parts[0]
        host_part = parts[1]
        
        if ':' in user_pass_part:
            user_pass = user_pass_part.split('://', 1)
            if len(user_pass) == 2:
                scheme = user_pass[0]
                credentials = user_pass[1]
                if ':' in credentials:
                    user = credentials.split(':')[0]
                    return f"{scheme}://{user}:***@{host_part}"
        
        return url
    except Exception:
        # If anything goes wrong, return a safe fallback
        return "***masked***"


def get_engine():
    global _engine, _SessionLocal
    if _engine is not None:
        return _engine

    database_url = get_database_url()
    if not database_url:
        raise RuntimeError(
            f"Database URL not configured. Set the {DATABASE_URL} environment variable."
        )
    logger.info("Database URL: %s", _mask_database_url(database_url))
    _engine = create_engine(database_url, future=True)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine


def init_db() -> None:
    logger.info("Initializing database")
    engine = get_engine()
    Base.metadata.create_all(engine)


@contextmanager
def session_scope() -> Iterable[Session]:
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _upsert_artist(
    session: Session, artist_model: ArtistModel, artist_cache: dict[str, Artist]
) -> Artist:
    artist_id = _ensure_identifier(
        "artist", artist_model.id, artist_model.uri, artist_model.name
    )
    artist = artist_cache.get(artist_id)
    if artist is None:
        artist = session.get(Artist, artist_id)
    if artist is None:
        artist = Artist(
            spotify_id=artist_id,
            name=artist_model.name,
            href=artist_model.href,
            external_url=(artist_model.external_urls or {}).get("spotify"),
        )
        session.add(artist)
    else:
        artist.name = artist_model.name
        artist.href = artist_model.href
        artist.external_url = (artist_model.external_urls or {}).get("spotify")

    artist_cache[artist_id] = artist
    return artist


def _upsert_album(
    session: Session,
    album_model: AlbumModel,
    album_cache: dict[str, Album],
    artist_cache: dict[str, Artist],
) -> Album:
    album_id = _ensure_identifier(
        "album", album_model.id, album_model.uri, album_model.name
    )
    album = album_cache.get(album_id)
    if album is None:
        album = session.get(Album, album_id)
    if album is None:
        album = Album(spotify_id=album_id, name=album_model.name)
        session.add(album)
        album_cache[album_id] = album
    else:
        album_cache[album_id] = album
    album.album_type = album_model.album_type
    album.release_date = album_model.release_date
    album.release_date_precision = album_model.release_date_precision
    album.total_tracks = album_model.total_tracks
    album.href = album_model.href
    album.external_url = (album_model.external_urls or {}).get("spotify")

    # Sync album artists
    existing_relations = {
        rel.artist.spotify_id: rel for rel in album.artists if rel.artist is not None
    }
    new_artist_ids: set[str] = set()
    if album_model.artists:
        for index, artist_model in enumerate(album_model.artists):
            artist = _upsert_artist(session, artist_model, artist_cache)
            new_artist_ids.add(artist.spotify_id)
            relation = existing_relations.get(artist.spotify_id)
            if relation is None:
                relation = AlbumArtist(album=album, artist=artist, artist_order=index)
                session.add(relation)
            else:
                relation.artist_order = index

        # Remove stale relations
        for artist_id, relation in list(existing_relations.items()):
            if artist_id not in new_artist_ids:
                if inspect(relation).persistent:
                    session.delete(relation)
                else:
                    album.artists.remove(relation)

    return album


def _sync_track_artists(
    session: Session,
    track: Track,
    artist_models: List[ArtistModel],
    artist_cache: dict[str, Artist],
) -> None:
    existing_relations = {
        rel.artist.spotify_id: rel for rel in track.artists if rel.artist is not None
    }
    new_artist_ids: set[str] = set()

    if artist_models:
        for index, artist_model in enumerate(artist_models):
            artist = _upsert_artist(session, artist_model, artist_cache)
            new_artist_ids.add(artist.spotify_id)
            relation = existing_relations.get(artist.spotify_id)
            if relation is None:
                relation = TrackArtist(track=track, artist=artist, artist_order=index)
                session.add(relation)
            else:
                relation.artist_order = index

        for artist_id, relation in list(existing_relations.items()):
            if artist_id not in new_artist_ids:
                if inspect(relation).persistent:
                    session.delete(relation)
                else:
                    track.artists.remove(relation)


def persist_playlist(playlist_id: str, playlist_response: PlaylistResponse) -> int:
    """Persist playlist metadata and return the number of stored tracks."""

    init_db()

    try:
        playlist_response = PlaylistResponse.model_validate(playlist_response)
    except ValidationError as exc:  # Defensive; should already be validated upstream
        raise ValueError(f"Invalid playlist payload: {exc}") from exc

    with session_scope() as session:
        playlist = session.get(Playlist, playlist_id)
        if playlist is None:
            playlist = Playlist(spotify_id=playlist_id)
            session.add(playlist)

        # Remove existing playlist tracks for idempotency
        session.execute(
            delete(PlaylistTrack).where(PlaylistTrack.playlist_id == playlist_id)
        )

        stored_tracks = 0
        album_cache: dict[str, Album] = {}
        artist_cache: dict[str, Artist] = {}
        track_cache: dict[str, Track] = {}
        for index, item in enumerate(playlist_response.items):
            track_model = item.track
            if track_model is None:
                continue

            album = _upsert_album(session, track_model.album, album_cache, artist_cache)
            track_id = _ensure_identifier(
                "track", track_model.id, track_model.uri, track_model.name
            )
            track = track_cache.get(track_id)
            if track is None:
                track = session.get(Track, track_id)
            if track is None:
                track = Track(
                    spotify_id=track_id,
                    name=track_model.name,
                    album=album,
                    duration_ms=track_model.duration_ms,
                )
                session.add(track)
            else:
                track.name = track_model.name
                track.album = album
                track.duration_ms = track_model.duration_ms
            track_cache[track_id] = track

            track.explicit = track_model.explicit
            track.is_playable = track_model.is_playable
            track.is_local = track_model.is_local
            track.popularity = track_model.popularity
            track.preview_url = track_model.preview_url
            track.track_number = track_model.track_number
            track.external_url = (track_model.external_urls or {}).get("spotify")
            track.external_id_isrc = (track_model.external_ids or {}).get("isrc")

            _sync_track_artists(session, track, track_model.artists, artist_cache)

            added_at = _parse_datetime(item.added_at)
            added_by_id = None
            added_by_name = None
            if item.added_by:
                added_by_id = item.added_by.get("id")
                added_by_name = item.added_by.get("display_name") or item.added_by.get(
                    "id"
                )

            playlist_track = PlaylistTrack(
                playlist=playlist,
                track=track,
                position=index,
                added_at=added_at,
                added_by_id=added_by_id,
                added_by_name=added_by_name,
                is_local=item.is_local,
            )
            session.add(playlist_track)
            stored_tracks += 1

        return stored_tracks


def _parse_datetime(timestamp: Optional[str]) -> Optional[datetime]:
    if not timestamp:
        return None
    try:
        # Spotify timestamps are ISO-8601 with Z suffix
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_tracks_for_playlist(playlist_id: str) -> List[TrackModel]:
    """Load playlist tracks from the database as Pydantic models."""

    init_db()

    with session_scope() as session:
        stmt = (
            select(PlaylistTrack)
            .where(PlaylistTrack.playlist_id == playlist_id)
            .order_by(PlaylistTrack.position.asc())
            .options(
                # Relationships auto-loaded when accessed thanks to expire_on_commit=False
            )
        )
        playlist_items: List[PlaylistTrack] = session.scalars(stmt).all()

        tracks: List[TrackModel] = []
        for playlist_item in playlist_items:
            track = playlist_item.track
            if track is None:
                continue
            album = track.album
            if album is None:
                continue

            artist_models = [
                ArtistModel(
                    name=relation.artist.name,
                    id=relation.artist.spotify_id,
                    href=relation.artist.href,
                    external_urls={"spotify": relation.artist.external_url}
                    if relation.artist.external_url
                    else None,
                    uri=None,
                    type=None,
                )
                for relation in sorted(track.artists, key=lambda r: r.artist_order)
            ]

            album_artist_models = [
                ArtistModel(
                    name=relation.artist.name,
                    id=relation.artist.spotify_id,
                    href=relation.artist.href,
                    external_urls={"spotify": relation.artist.external_url}
                    if relation.artist.external_url
                    else None,
                    uri=None,
                    type=None,
                )
                for relation in sorted(album.artists, key=lambda r: r.artist_order)
            ]

            album_model = AlbumModel(
                name=album.name,
                id=album.spotify_id,
                album_type=album.album_type,
                artists=album_artist_models,
                external_urls={"spotify": album.external_url}
                if album.external_url
                else None,
                href=album.href,
                images=None,
                release_date=album.release_date,
                release_date_precision=album.release_date_precision,
                total_tracks=album.total_tracks,
                type=None,
                uri=None,
            )

            track_model = TrackModel(
                name=track.name,
                id=track.spotify_id,
                artists=artist_models,
                album=album_model,
                duration_ms=track.duration_ms,
                explicit=track.explicit,
                external_ids={"isrc": track.external_id_isrc}
                if track.external_id_isrc
                else None,
                external_urls={"spotify": track.external_url}
                if track.external_url
                else None,
                href=None,
                is_local=track.is_local,
                is_playable=track.is_playable,
                popularity=track.popularity,
                preview_url=track.preview_url,
                track_number=track.track_number,
                type=None,
                uri=None,
            )
            tracks.append(track_model)

        return tracks


def record_download(
    playlist_id: str,
    track_id: str,
    query_type: Union["QueryType", str],
    youtube_id: str,
    title: Optional[str],
    file_uri: str,
) -> None:
    """Persist download metadata for auditing purposes."""

    init_db()
    with session_scope() as session:
        playlist = session.get(Playlist, playlist_id)
        track = session.get(Track, track_id)
        if playlist is None or track is None:
            return
        query_value = (
            query_type.value if hasattr(query_type, "value") else str(query_type)
        )
        download = Download(
            playlist=playlist,
            track=track,
            query_type=query_value,
            youtube_id=youtube_id,
            title=title,
            file_path=file_uri,
        )
        session.add(download)


def download_exists(
    playlist_id: str, youtube_id: str, query_type: Union["QueryType", str]
) -> bool:
    """Check whether a YouTube video has already been stored for a playlist."""

    init_db()
    with session_scope() as session:
        query_value = (
            query_type.value if hasattr(query_type, "value") else str(query_type)
        )
        stmt = (
            select(Download.id)
            .where(Download.playlist_id == playlist_id)
            .where(Download.youtube_id == youtube_id)
            .where(Download.query_type == query_value)
        )
        return session.execute(stmt).scalar_one_or_none() is not None
