# AutoDJ Playlist Data Model Migration Plan

## Existing Data Elements

The current implementation serializes Spotify playlist metadata to JSON using
Pydantic models located in `MonolithDev/gettingSongs/models.py`. The JSON files
contain the following nested entities:

- **Playlist**: id, name, description, collaborative flag, owner, snapshot id,
  images, followers, tracks response, etc.
- **Playlist Items**: wrapper objects containing each track plus metadata such as
  `added_at`, `added_by`, and `is_local`.
- **Track**: id, name, artists, album, duration, explicit flag, popularity,
  preview URL, Spotify/external identifiers, and playback flags.
- **Album**: id, name, album type, artists, images, release date, total tracks,
  and Spotify metadata (href, uri, URLs).
- **Artist**: id, name, href, URI, external URLs, and type.

All of these entities are embedded within a single JSON file. The downloader
later loads the JSON back into memory to iterate through tracks. No relational
separation exists between playlists, tracks, albums, or artists, and there is no
persistence beyond the single JSON document per playlist. Mix downloads are not
recorded separately from original track downloads.

## Target Relational Schema (3NF)

To normalize the data while keeping the implementation lightweight, the
following schema will be introduced. Each table has a minimal set of columns
necessary for the pipeline and avoids redundant storage.

```text
Playlist (spotify_id PK, name, description, collaborative, public,
          snapshot_id, href, external_url)

PlaylistTrack (id PK, playlist_id FK -> Playlist.spotify_id,
               track_id FK -> Track.spotify_id,
               added_at, added_by_id, added_by_name, is_local)

Track (spotify_id PK, name, album_id FK -> Album.spotify_id,
       duration_ms, explicit, is_playable, is_local,
       popularity, preview_url, track_number, external_url, external_id_isrc)

Album (spotify_id PK, name, album_type, release_date,
       release_date_precision, total_tracks, href, external_url)

Artist (spotify_id PK, name, href, external_url)

TrackArtist (track_id FK -> Track.spotify_id,
             artist_id FK -> Artist.spotify_id,
             primary key (track_id, artist_id),
             artist_order)

AlbumArtist (album_id FK -> Album.spotify_id,
             artist_id FK -> Artist.spotify_id,
             primary key (album_id, artist_id),
             artist_order)

Download (id PK, track_id FK -> Track.spotify_id,
          playlist_id FK -> Playlist.spotify_id,
          query_type ENUM['song','mix'],
          youtube_id, title, file_path, downloaded_at)
```

### Normalization Rationale

- **1NF**: Each table stores atomic values (e.g., external URL strings instead
  of nested dictionaries). Lists such as artists are represented through join
  tables (`TrackArtist`, `AlbumArtist`).
- **2NF**: Non-key attributes depend on the whole primary key. For example,
  playlist metadata depends on the playlist identifier; join tables only store
  relationship-specific attributes (order, timestamps).
- **3NF**: No transitive dependencies remain. Track popularity or explicit flag
  stay with the track entity; download metadata references both playlist and
  track without duplicating playlist details.

### Implementation Notes

- Spotify IDs already function as stable keys, so they are used directly as
  primary keys. When Spotify omits an ID (e.g., for local tracks), the pipeline
  will synthesize a deterministic identifier to keep referential integrity.
- SQLAlchemy with the `psycopg2-binary` driver will manage persistence.
- Pydantic models continue to validate and coerce Spotify API responses before
  storing them in the database.
- The downloader will read playlist contents via the database rather than JSON
  files, and downloaded audio will be written under `downloads/originals/` and
  `downloads/mixes/` subdirectories.

This structure keeps the schema normalized, avoids unnecessary complexity, and
provides enough flexibility for future extensions (e.g., tracking download
history) without over-engineering the MVP.
