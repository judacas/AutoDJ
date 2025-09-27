#!/usr/bin/env python3
"""
Script to download the first song from a saved Spotify playlist JSON file using YouTube via yt-dlp.
Usage: python download_first_song.py <playlist_id>

The playlist JSON file must exist in the output/ directory with naming scheme: playlist_{playlist_id}.json
"""

import sys
import json
from pathlib import Path
import yt_dlp
from models import PlaylistResponse, PlaylistTrack, Track


def get_first_track_from_file(playlist_id):
    """
    Fetch the first track from a saved playlist JSON file.

    Args:
        playlist_id (str): Spotify playlist ID (e.g., 5evvXuuNDgAHbPDmojLZgD)

    Returns:
        Track: The first track from the playlist, or None if error
    """
    try:
        # Construct file path
        file_path = Path("output") / f"playlist_{playlist_id}.json"

        if not file_path.exists():
            print(f"Playlist file not found: {file_path}")
            print(
                "Make sure you have run get_playlist_songs.py first to generate the playlist file."
            )
            return None

        # Read and parse the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            playlist_data = json.load(f)

        # Parse using Pydantic model
        playlist_response = PlaylistResponse.model_validate(playlist_data)

        if not playlist_response.items:
            print("No songs found in this playlist file.")
            return None

        # Get the first track
        first_playlist_track = playlist_response.items[0]

        if not first_playlist_track.track:
            print("First track in playlist is not available.")
            return None

        return first_playlist_track.track

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return None
    except Exception as e:
        print(f"Error reading playlist file: {e}")
        return None


def search_youtube_for_track(track):
    """
    Search YouTube for a track and return the best match URL.

    Args:
        track (Track): The track to search for

    Returns:
        str: YouTube URL of the best match, or None if not found
    """
    # Create search query to prefer official audio, avoid music videos and karaoke
    search_query = f"{track.artist_names} - {track.name} audio NOT music video NOT karaoke NOT cover"

    print(f"Searching YouTube for: {search_query}")

    # Configure yt-dlp for search
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "default_search": "ytsearch1:",  # Search YouTube and get top result
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search for the track
            search_url = f"ytsearch1:{search_query}"
            info = ydl.extract_info(search_url, download=False)

            if info and "entries" in info and info["entries"]:
                # Get the first (best) result
                best_match = info["entries"][0]
                video_url = best_match.get("webpage_url") or best_match.get("url")

                if video_url:
                    print(
                        f"Found YouTube video: {best_match.get('title', 'Unknown title')}"
                    )
                    print(f"URL: {video_url}")
                    return video_url
                else:
                    print("No valid URL found in search results")
                    return None
            else:
                print("No search results found")
                return None

    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return None


def extract_youtube_id(video_url):
    """
    Extract YouTube video ID from URL for idempotency.

    Args:
        video_url (str): YouTube video URL

    Returns:
        str: YouTube video ID
    """
    import re

    # Handle different YouTube URL formats
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)",
        r"youtube\.com/v/([^&\n?#]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)

    return "unknown_id"


def download_audio_from_youtube(video_url, output_dir="downloads"):
    """
    Download audio from YouTube video using yt-dlp.

    Args:
        video_url (str): YouTube video URL
        output_dir (str): Directory to save the downloaded file

    Returns:
        str: Path to downloaded file, or None if error
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Extract YouTube ID for idempotent filename
    youtube_id = extract_youtube_id(video_url)

    # Configure yt-dlp for audio download with YouTube ID-based filename
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
        "postprocessor_args": [
            "-ar",
            "44100",  # Set sample rate to 44.1kHz
        ],
        "extractaudio": True,
        "audioformat": "mp3",
    }

    try:
        print(f"Downloading audio from: {video_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to get the filename
            info = ydl.extract_info(video_url, download=False)
            if info is None:
                print("Failed to extract video info.")
                return None
            title = info.get("title", "unknown")

            # Download the audio
            ydl.download([video_url])

            # Look for files with this specific YouTube ID
            id_files = list(output_path.glob(f"{youtube_id}__*"))
            if id_files:
                # Get the most recently created file
                downloaded_file = max(id_files, key=lambda f: f.stat().st_mtime)
                print(f"Successfully downloaded: {downloaded_file}")
                return str(downloaded_file)

            print("Download completed but file not found")
            return None

    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python download_first_song.py <playlist_id>")
        print("\nExamples:")
        print("  python download_first_song.py 5evvXuuNDgAHbPDmojLZgD")
        print("  python download_first_song.py 37i9dQZF1DXcBWIGoYBM5M")
        print("\nNote: The playlist file must exist in output/ directory.")
        print("Run get_playlist_songs.py first to generate the playlist file.")
        sys.exit(1)

    playlist_id = sys.argv[1]

    print(f"Reading first song from playlist file: playlist_{playlist_id}.json")

    # Get the first track from the playlist file
    track = get_first_track_from_file(playlist_id)
    if not track:
        print("Failed to read track from playlist file.")
        sys.exit(1)

    print(f"First track: {track}")

    # Search YouTube for the track
    video_url = search_youtube_for_track(track)
    if not video_url:
        print("Failed to find track on YouTube.")
        sys.exit(1)

    # Download the audio
    downloaded_file = download_audio_from_youtube(video_url)
    if not downloaded_file:
        print("Failed to download audio.")
        sys.exit(1)

    print(f"\n✅ Successfully downloaded: {downloaded_file}")


if __name__ == "__main__":
    main()
