#!/usr/bin/env python3
"""
Script to download tracks from a saved Spotify playlist JSON file using YouTube via yt-dlp.
Usage: python download_tracks.py <playlist_id> <query_type>

The playlist JSON file must exist in the output/ directory with naming scheme: playlist_{playlist_id}.json
Downloads are idempotent - already downloaded tracks will be skipped.

Query types:
- "song": Downloads original songs (prefers official audio, avoids remixes, covers, etc.)
- "mix": Downloads mixes that may include the songs from the playlist

Examples:
  python download_tracks.py 5evvXuuNDgAHbPDmojLZgD song
  python download_tracks.py 37i9dQZF1DXcBWIGoYBM5M mix
"""

import sys
from youtube_utils import (
    download_tracks_from_playlist,
    print_download_summary,
    QueryType,
)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 3:
        print("Usage: python download_tracks.py <playlist_id> <query_type>")
        print("\nQuery types:")
        print("  song - Downloads original songs (prefers official audio)")
        print("  mix  - Downloads mixes that may include the songs")
        print("\nExamples:")
        print("  python download_tracks.py 5evvXuuNDgAHbPDmojLZgD song")
        print("  python download_tracks.py 37i9dQZF1DXcBWIGoYBM5M mix")
        print("\nNote: The playlist file must exist in output/ directory.")
        print("Run get_playlist_songs.py first to generate the playlist file.")
        sys.exit(1)

    playlist_id = sys.argv[1]
    query_type_str = sys.argv[2].lower()

    # Convert string to enum and validate
    try:
        query_type = QueryType(query_type_str)
    except ValueError:
        print(f"Error: Invalid query_type '{query_type_str}'. Must be 'song' or 'mix'.")
        print("\nQuery types:")
        print("  song - Downloads original songs (prefers official audio)")
        print("  mix  - Downloads mixes that may include the songs")
        sys.exit(1)

    # Download tracks using the shared utility function
    summary = download_tracks_from_playlist(playlist_id, query_type=query_type)

    if summary is None:
        print("Failed to download tracks.")
        sys.exit(1)

    # Print the download summary
    print_download_summary(summary)


if __name__ == "__main__":
    main()
