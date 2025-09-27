#!/usr/bin/env python3
"""Interactive helper that drives the full AutoDJ playlist pipeline."""

from __future__ import annotations

import argparse
import sys

from logging_config import get_module_logger

from playlist_pipeline import PlaylistPipeline
from youtube_utils import print_download_summary

logger = get_module_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a Spotify playlist and download its tracks and mixes."
    )
    parser.add_argument(
        "--mixes-per-track",
        type=int,
        default=10,
        help="Number of mix downloads to attempt per track (default: 10)",
    )
    parser.add_argument(
        "--skip-songs",
        action="store_true",
        help="Skip downloading the original songs.",
    )
    parser.add_argument(
        "--skip-mixes",
        action="store_true",
        help="Skip downloading DJ mixes.",
    )
    return parser.parse_args()


def get_playlist_url() -> str:
    """Prompt the user for a Spotify playlist URL."""

    print("\n🎵 Enter a Spotify playlist URL:")
    print("Example: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

    while True:
        url = input("\nPlaylist URL: ").strip()

        if not url:
            print("Please enter a URL")
            continue

        if "spotify.com/playlist/" not in url and not url.startswith(
            "spotify:playlist:"
        ):
            print("❌ Please enter a valid Spotify playlist URL")
            continue

        return url


def main() -> None:
    args = parse_args()
    pipeline = PlaylistPipeline()

    print("🎧 AutoDJ Playlist Pipeline")
    print("=" * 50)

    playlist_url = get_playlist_url()

    try:
        result = pipeline.run(
            playlist_url,
            mixes_per_track=args.mixes_per_track,
            download_songs=not args.skip_songs,
            download_mixes=not args.skip_mixes,
        )
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)

    print(f"\n✅ Successfully fetched {result.playlist.total} tracks from Spotify")
    print(f"💾 Playlist data saved to: {result.playlist_json}")

    for query_type, summary in result.download_summaries.items():
        print()
        print_download_summary(summary, label=query_type.value)

    print("\n🎉 Playlist conversion completed!")
    print("📁 Downloaded files are in the 'downloads/' directory")


if __name__ == "__main__":
    main()
