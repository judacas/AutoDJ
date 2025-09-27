#!/usr/bin/env python3
"""
Shared utilities for YouTube downloading functionality.
Contains common functions used by both song and mix downloaders.
"""

import json
from pathlib import Path
from enum import Enum
import yt_dlp
from dj_LLM import DJQueryGenerator
from models import PlaylistResponse
from logging_config import get_module_logger
import sys

# Set up logger for this module
logger = get_module_logger(__name__)
from models import PlaylistResponse, Track


class QueryType(str, Enum):
    """Pydantic-compatible enum for different types of YouTube search queries."""

    SONG = "song"
    MIX = "mix"


def get_all_tracks_from_file(playlist_id):
    """
    Fetch all tracks from a saved playlist JSON file.

    Args:
        playlist_id (str): Spotify playlist ID (e.g., 5evvXuuNDgAHbPDmojLZgD)

    Returns:
        List[Track]: List of all tracks from the playlist, or None if error
    """
    try:
        # Construct file path
        file_path = Path("output") / f"playlist_{playlist_id}.json"

        if not file_path.exists():
            logger.error(f"Playlist file not found: {file_path}")
            logger.info(
                "Make sure you have run get_playlist_songs.py first to generate the playlist file."
            )
            return None

        # Read and parse the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            playlist_data = json.load(f)

        # Parse using Pydantic model
        playlist_response = PlaylistResponse.model_validate(playlist_data)

        if not playlist_response.items:
            logger.warning("No songs found in this playlist file.")
            return None

        # Extract all available tracks
        tracks = []
        for playlist_track in playlist_response.items:
            if playlist_track.track:
                tracks.append(playlist_track.track)
            else:
                logger.debug(
                    f"Skipping unavailable track at position {len(tracks) + 1}"
                )

        if not tracks:
            logger.warning("No available tracks found in playlist.")
            return None

        logger.info(f"Found {len(tracks)} tracks in playlist")
        return tracks

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading playlist file: {e}")
        return None


def create_search_queries(track, query_type=QueryType.SONG) -> list[str]:
    """
    Create a search query for YouTube based on track and query type.

    Args:
        track (Track): The track to search for
        query_type (QueryType): Type of search - QueryType.SONG or QueryType.MIX

    Returns:
        str: Formatted search query
    """
    if query_type == QueryType.SONG:
        # TODO: Improve search queries - currently finds funky results sometimes
        # (e.g., clean versions instead of normal, still gets covers/remixes occasionally)
        # Consider:
        # - Adding more exclusion terms (-clean -radio -edit -version -remaster)
        # - Prioritizing official channels/verified artists
        # - Using multiple search strategies with fallbacks
        # - Analyzing video duration to match track length
        # - Checking video metadata for better matching

        return [
            f"{track.artist_names} - {track.name} -video -karaoke -cover -instrumental -remix -live -acapella -concert -lyrics"
        ]

    elif query_type == QueryType.MIX:
        query_generator = DJQueryGenerator()
        return query_generator.generate_queries(track).queries
    else:
        raise ValueError(
            f"Unknown query_type: {query_type}. Must be QueryType.SONG or QueryType.MIX"
        )


def search_youtube_for_track(track, query_type=QueryType.SONG):
    """
    Search YouTube for a track and return the best match URL.

    Args:
        track (Track): The track to search for
        query_type (QueryType): Type of search - QueryType.SONG or QueryType.MIX

    Returns:
        str: YouTube URL of the best match, or None if not found
    """
    search_queries = create_search_queries(track, query_type)

    logger.info(
        f"Searching YouTube with {len(search_queries)} queries: {search_queries}"
    )

    # Configure yt-dlp for search
    ydl_opts = {
        "quiet": False,
        "no_warnings": False,
        "extract_flat": True,
        "default_search": "ytsearch1:",  # Search YouTube and get top result
    }
    # Try each query until we find a result
    for i, search_query in enumerate(search_queries):
        try:
            logger.info(f"Trying query {i+1}/{len(search_queries)}: {search_query}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for the track
                search_url = f"ytsearch1:{search_query}"
                info = ydl.extract_info(search_url, download=False)

                if info and "entries" in info and info["entries"]:
                    # Get the first (best) result
                    best_match = info["entries"][0]
                    video_url = best_match.get("webpage_url") or best_match.get("url")

                    if video_url:
                        logger.info(
                            f"Found YouTube video with query {i+1}: {best_match.get('title', 'Unknown title')}"
                        )
                        logger.debug(f"URL: {video_url}")
                        if downloaded_file := download_audio_from_youtube(video_url):
                            logger.info(
                                f"✅ Successfully downloaded: {downloaded_file}"
                            )
                        else:
                            logger.warning(
                                f"❌ Failed to download audio for: {video_url}"
                            )
                        return video_url
                    else:
                        logger.warning(
                            f"No valid URL found in search results for query {i+1}"
                        )
                        continue
                else:
                    logger.warning(f"No search results found for query {i+1}")
                    continue

        except Exception as e:
            logger.warning(f"Error with query {i+1} '{search_query}': {e}")
            continue

    logger.warning(
        f"No YouTube results found for any of the {len(search_queries)} queries"
    )
    return None


def is_track_downloaded(youtube_id, output_dir="downloads"):
    """
    Check if a track is already downloaded based on YouTube ID.

    Args:
        youtube_id (str): YouTube video ID
        output_dir (str): Directory to check for downloads

    Returns:
        bool: True if track is already downloaded
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        return False

    # Look for any file with this YouTube ID
    id_files = list(output_path.glob(f"{youtube_id}__*"))
    return len(id_files) > 0


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
        logger.info(f"Downloading audio from: {video_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to get the filename
            info = ydl.extract_info(video_url, download=False)
            if info is None:
                logger.error("Failed to extract video info.")
                return None
            title = info.get("title", "unknown")

            # Download the audio
            ydl.download([video_url])

            # Look for files with this specific YouTube ID
            id_files = list(output_path.glob(f"{youtube_id}__*"))
            if id_files:
                # Get the most recently created file
                downloaded_file = max(id_files, key=lambda f: f.stat().st_mtime)
                logger.info(f"Successfully downloaded: {downloaded_file}")
                return str(downloaded_file)

            logger.warning("Download completed but file not found")
            return None

    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        return None


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        logger.error("Usage: python download_all_songs.py <playlist_id>")
        logger.error("\nExamples:")
        logger.error("  python download_all_songs.py 5evvXuuNDgAHbPDmojLZgD")
        logger.error("  python download_all_songs.py 37i9dQZF1DXcBWIGoYBM5M")
        logger.error("\nNote: The playlist file must exist in output/ directory.")
        logger.error("Run get_playlist_songs.py first to generate the playlist file.")
        sys.exit(1)


def download_tracks_from_playlist(playlist_id, query_type=QueryType.SONG):
    """
    Download all tracks from a playlist using the specified query type.

    Args:
        playlist_id (str): Spotify playlist ID
        query_type (QueryType): Type of search - QueryType.SONG or QueryType.MIX

    logger.info(f"Reading all songs from playlist file: playlist_{playlist_id}.json")
    Returns:
        dict: Summary of download results
    """
    print(f"Reading all songs from playlist file: playlist_{playlist_id}.json")

    # Get all tracks from the playlist file
    tracks = get_all_tracks_from_file(playlist_id)
    if not tracks:
        logger.error("Failed to read tracks from playlist file.")
        sys.exit(1)

    logger.info(f"Starting download of {len(tracks)} tracks...")

    successful_downloads = 0
    skipped_downloads = 0
    failed_downloads = 0

    for i, track in enumerate(tracks, 1):
        logger.info(f"\n--- Track {i}/{len(tracks)}: {track} ---")

        # Search YouTube for the track
        video_url = search_youtube_for_track(track, query_type)
        if not video_url:
            logger.error(f"❌ Failed to find track on YouTube: {track}")
            failed_downloads += 1
            continue

        # Check if already downloaded
        youtube_id = extract_youtube_id(video_url)
        if is_track_downloaded(youtube_id):
            logger.info(f"⏭️  Already downloaded, skipping: {track}")
            skipped_downloads += 1
            continue

        # Download the audio
        downloaded_file = download_audio_from_youtube(video_url)
        if downloaded_file:
            logger.info(f"✅ Successfully downloaded: {downloaded_file}")
            successful_downloads += 1
        else:
            logger.error(f"❌ Failed to download: {track}")
            failed_downloads += 1

    # Log summary
    logger.info(f"\n{'='*50}")
    logger.info(f"DOWNLOAD SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Total tracks: {len(tracks)}")
    logger.info(f"✅ Successfully downloaded: {successful_downloads}")
    logger.info(f"⏭️  Skipped (already downloaded): {skipped_downloads}")
    logger.info(f"❌ Failed: {failed_downloads}")
    logger.info(f"{'='*50}")

    # Return summary
    return {
        "total_tracks": len(tracks),
        "successful_downloads": successful_downloads,
        "skipped_downloads": skipped_downloads,
        "failed_downloads": failed_downloads,
    }


if __name__ == "__main__":
    main()


def print_download_summary(summary):
    """
    Print a formatted download summary.

    Args:
        summary (dict): Summary dictionary from download_tracks_from_playlist
    """
    print(f"\n{'='*50}")
    print(f"DOWNLOAD SUMMARY")
    print(f"{'='*50}")
    print(f"Total tracks: {summary['total_tracks']}")
    print(f"✅ Successfully downloaded: {summary['successful_downloads']}")
    print(f"⏭️  Skipped (already downloaded): {summary['skipped_downloads']}")
    print(f"❌ Failed: {summary['failed_downloads']}")
    print(f"{'='*50}")
