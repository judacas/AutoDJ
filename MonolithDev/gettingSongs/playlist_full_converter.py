#!/usr/bin/env python3
"""Interactive helper that drives the full AutoDJ playlist pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from logging_config import get_module_logger

from playlist_pipeline import PlaylistPipeline
from models import PlaylistResponse
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
    parser.add_argument(
        "--offline-json",
        help="Path to a cached playlist JSON file for offline development.",
    )
    parser.add_argument(
        "playlist_url",
        nargs="?",
        help="Spotify playlist URL to process. If omitted, you will be prompted.",
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

    playlist_url = args.playlist_url or get_playlist_url()

    offline_playlist = None
    if args.offline_json:
        offline_path = Path(args.offline_json)
        if not offline_path.exists():
            logger.error("Offline JSON file not found: %s", offline_path)
            sys.exit(1)
        try:
            playlist_data = json.loads(offline_path.read_text(encoding="utf-8"))
            offline_playlist = PlaylistResponse.model_validate(playlist_data)
        except Exception as exc:  # pragma: no cover - defensive parsing
            logger.error("Failed to load offline playlist data: %s", exc)
            sys.exit(1)

    try:
        result = pipeline.run(
            playlist_url,
            mixes_per_track=args.mixes_per_track,
            download_songs=not args.skip_songs,
            download_mixes=not args.skip_mixes,
            preloaded_playlist=offline_playlist,
        )
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)

    print(f"\n✅ Successfully fetched {result.playlist.total} tracks from Spotify")
    print(
        f"💾 Stored {result.persisted_tracks} tracks for playlist {result.playlist_id} in the database"
    )

    for query_type, summary in result.download_summaries.items():
        print()
        print_download_summary(summary, label=query_type.value)

    print("\n🎉 Playlist conversion completed!")
    print(
        "📁 Downloaded files are in the 'downloads/originals' and 'downloads/mixes' directories"
    )


if __name__ == "__main__":
    main()
