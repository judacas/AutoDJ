# Getting Songs Scripts

This folder contains scripts and a small FastAPI service for fetching and working with Spotify playlist data.

## Files

- `models.py` - Pydantic models for Spotify data structures (Track, Artist, Album, Playlist)
- `get_playlist_songs.py` - Script to fetch and display playlist songs using Pydantic models
- `download_all_songs.py` - Script to download all songs from a playlist using YouTube via yt-dlp
- `playlist_pipeline.py` - Orchestrates fetching playlists and optional downloads
- `api.py` - FastAPI app exposing endpoints to fetch playlist tracks and run the pipeline
- `config.py` - Configuration for Spotify API credentials

## FastAPI API (how to run)

You can run the API the same way you did from PowerShell. Two supported options:

- Option A: run the script directly (what you used)

  PowerShell (from the project root):
  ```powershell
  python MonolithDev\gettingSongs\api.py
  ```

- Option B: use Uvicorn module path (also works from the project root)

  ```powershell
  python -m uvicorn MonolithDev.gettingSongs.api:app --host 127.0.0.1 --port 8000 --reload
  ```

Once running, open the interactive docs:
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

### Prerequisites for the API

1. Create a `.env` file with your Spotify credentials (same keys used elsewhere):
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
2. Install dependencies (from repo root):
   ```powershell
   pip install -r requirements.txt
   ```

## get_playlist_songs.py

A simple script that takes a Spotify playlist URI as an argument and prints out all the songs in the playlist. The script uses Pydantic models for type safety and data validation.

### Usage

```powershell
python MonolithDev\gettingSongs\get_playlist_songs.py <playlist_uri>
```

### Examples

```powershell
# Using Spotify URI format
python MonolithDev\gettingSongs\get_playlist_songs.py spotify:playlist:37i9dQZF1DXcBWIGoYBM5M

# Using Spotify URL format
python MonolithDev\gettingSongs\get_playlist_songs.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

### Prerequisites

1. Make sure you have set up your Spotify API credentials in a `.env` file (see `SPOTIFY_SETUP.md` in the project root)
2. Install dependencies: `pip install -r requirements.txt`

### Features

- **Type Safety**: Uses Pydantic models for data validation and type safety
- **Clean Data Access**: Access track properties through clean, typed attributes
- **Error Handling**: Robust error handling for API responses and data parsing
- **Formatted Output**: Clean, readable output with proper formatting

### Output

The script will display:
- Song name
- Artist(s)
- Album name
- Duration (in MM:SS format)
- Total number of tracks in the playlist

### Error Handling

The script handles:
- Invalid playlist URIs
- Network errors
- Spotify API errors
- Empty playlists

## download_all_songs.py

A script that downloads all songs from a Spotify playlist by searching YouTube and downloading the audio files. The script reads from existing playlist JSON files created by `get_playlist_songs.py`.

### Usage

```powershell
python MonolithDev\gettingSongs\download_all_songs.py <playlist_id>
```

### Examples

```powershell
# Download all songs from a playlist
python MonolithDev\gettingSongs\download_all_songs.py 5evvXuuNDgAHbPDmojLZgD

# Download all songs from another playlist
python MonolithDev\gettingSongs\download_all_songs.py 37i9dQZF1DXcBWIGoYBM5M
```

### Prerequisites

1. First run `get_playlist_songs.py` to create the playlist JSON file
2. Install dependencies: `pip install -r requirements.txt`
3. Install ffmpeg for audio conversion

### Features

- **Idempotent Downloads**: Already downloaded tracks are skipped
- **YouTube Search**: Automatically searches YouTube for each track
- **Audio Conversion**: Downloads and converts to MP3 format (192kbps)
- **Progress Tracking**: Shows progress and summary statistics
- **Error Handling**: Continues downloading even if individual tracks fail

### Output

The script will:
- Download MP3 files to the `downloads/` directory
- Use filenames with YouTube ID for uniqueness: `{youtube_id}__{title}.mp3`
- Show progress for each track
- Display a final summary with success/failure counts
