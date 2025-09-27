#!/usr/bin/env python3
"""
Complete playlist converter that gets playlist URL from user and downloads all tracks.
This script combines playlist URL input with the full download process.

Usage: python playlist_full_converter.py [query_type]
Query types: song (default) or mix
"""

import sys
import os
from pathlib import Path
from get_playlist_songs import get_playlist_songs, save_playlist_to_json
from youtube_utils import (
    download_tracks_from_playlist,
    print_download_summary,
    QueryType,
)
from logging_config import get_module_logger

# Set up logger for this module
logger = get_module_logger(__name__)


def get_playlist_url():
    """Get playlist URL from user input."""
    print("\n🎵 Enter a Spotify playlist URL:")
    print("Example: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

    while True:
        url = input("\nPlaylist URL: ").strip()

        if not url:
            print("Please enter a URL")
            continue

        if "spotify.com/playlist/" not in url:
            print("❌ Please enter a valid Spotify playlist URL")
            continue

        return url


def extract_playlist_id(url):
    """Extract playlist ID from URL."""
    if url.startswith("spotify:playlist:"):
        return url.split(":")[-1]
    elif "spotify.com/playlist/" in url:
        return url.split("/")[-1].split("?")[0]
    else:
        return url


def main():
    """Main function to handle the complete playlist conversion process."""
    # Get query type from command line argument (default to 'song')
    query_type_str = sys.argv[1].lower() if len(sys.argv) > 1 else "song"

    # Validate query type
    try:
        query_type = QueryType(query_type_str)
    except ValueError:
        print(f"Error: Invalid query_type '{query_type_str}'. Must be 'song' or 'mix'.")
        print("\nUsage: python playlist_full_converter.py [query_type]")
        print("Query types:")
        print("  song - Downloads original songs (prefers official audio) [default]")
        print("  mix  - Downloads mixes that may include the songs")
        sys.exit(1)

    print(f"🎧 AutoDJ Playlist Full Converter")
    print(f"📀 Query Type: {query_type.value}")
    print("=" * 50)

    # Step 1: Get playlist URL from user
    playlist_url = get_playlist_url()
    playlist_id = extract_playlist_id(playlist_url)

    print(f"\n📋 Processing playlist ID: {playlist_id}")
    print("=" * 50)

    # Step 2: Fetch playlist data from Spotify
    print("\n🔍 Fetching playlist data from Spotify...")
    playlist_response = get_playlist_songs(playlist_url)

    if not playlist_response:
        print("❌ Failed to fetch playlist data from Spotify.")
        print("Please check your playlist URL and try again.")
        sys.exit(1)

    print(f"✅ Successfully fetched {playlist_response.total} tracks from Spotify")

    # Step 3: Save playlist to JSON file
    print("\n💾 Saving playlist data to JSON file...")
    json_filepath = save_playlist_to_json(playlist_response, playlist_id)
    print(f"✅ Playlist data saved to: {json_filepath}")

    # Step 4: Download tracks using YouTube
    print(
        f"\n🎬 Starting download of tracks using YouTube ({query_type.value} mode)..."
    )
    print("=" * 50)

    summary = download_tracks_from_playlist(playlist_id, query_type=query_type)

    if summary is None:
        print("❌ Failed to download tracks.")
        sys.exit(1)

    # Step 5: Print download summary
    print("\n" + "=" * 50)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 50)
    print_download_summary(summary)

    print(f"\n🎉 Playlist conversion completed!")
    print(f"📁 Downloaded files are in the 'downloads/' directory")
    print(f"📄 Playlist data saved to: {json_filepath}")


if __name__ == "__main__":
    main()
