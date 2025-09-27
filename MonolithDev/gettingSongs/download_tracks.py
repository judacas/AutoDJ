#!/usr/bin/env python3
"""Download tracks or mixes for a playlist stored in the database."""

import sys
from youtube_utils import QueryType, YouTubeDownloader, print_download_summary


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
        print("\nNote: Fetch the playlist first using playlist_full_converter.py.")
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

    downloader = YouTubeDownloader()
    try:
        summary = downloader.download_playlist(playlist_id, query_type)
    except ValueError as exc:
        print(f"Failed to download tracks: {exc}")
        sys.exit(1)

    # Print the download summary
    print_download_summary(summary, label=query_type.value)


if __name__ == "__main__":
    main()
