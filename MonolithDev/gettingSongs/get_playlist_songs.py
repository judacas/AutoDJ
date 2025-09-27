#!/usr/bin/env python3
"""
Simple script to fetch and display songs from a Spotify playlist.
Usage: python get_playlist_songs.py <playlist_uri>
"""

import sys
import json
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from models import PlaylistResponse, PlaylistTrack, Track
from logging_config import get_module_logger

# Set up logger for this module
logger = get_module_logger(__name__)


def get_playlist_songs(playlist_uri):
    """
    Fetch songs from a Spotify playlist and return them.

    Args:
        playlist_uri (str): Spotify playlist URI (e.g., spotify:playlist:37i9dQZF1DXcBWIGoYBM5M)

    Returns:
        PlaylistResponse: The playlist response containing all tracks, or None if error
    """
    try:
        # Initialize Spotify client with client credentials
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Extract playlist ID from URI
        if playlist_uri.startswith("spotify:playlist:"):
            playlist_id = playlist_uri.split(":")[-1]
        elif "spotify.com/playlist/" in playlist_uri:
            playlist_id = playlist_uri.split("/")[-1].split("?")[0]
        else:
            playlist_id = playlist_uri

        # Get playlist tracks with pagination to collect all pages
        all_tracks = []
        offset = 0
        limit = 100  # Spotify's maximum per request
        last_response = None

        while True:
            raw_results = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)

            # Store the last valid response for metadata
            if raw_results:
                last_response = raw_results

            # Add tracks from this page
            if raw_results and raw_results.get("items"):
                all_tracks.extend(raw_results["items"])

            # Check if there are more pages
            if not raw_results or not raw_results.get("next"):
                break

            # Update offset for next page
            offset += limit

        # Create aggregated response with all tracks
        aggregated_response = {
            "href": last_response.get("href", "") if last_response else "",
            "items": all_tracks,
            "limit": last_response.get("limit", limit) if last_response else limit,
            "next": None,  # No more pages
            "offset": 0,  # Reset offset since we have all items
            "previous": None,
            "total": len(all_tracks),
        }

        # Parse response using Pydantic model
        try:
            playlist_response = PlaylistResponse.model_validate(aggregated_response)
        except Exception as e:
            logger.error(f"Error parsing playlist response: {e}")
            return None

        if not playlist_response.items:
            logger.warning("No songs found in this playlist.")
            return None

        return playlist_response

    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


def save_playlist_to_json(playlist_response, playlist_id, output_dir="output"):
    """
    Save playlist data to JSON file using Pydantic's natural serialization.

    Args:
        playlist_response (PlaylistResponse): The playlist response to save
        playlist_id (str): The playlist ID for filename
        output_dir (str): Directory to save the JSON file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create filename with playlist ID
    filename = f"playlist_{playlist_id}.json"
    filepath = output_path / filename

    # Use Pydantic's model_dump_json for natural serialization
    json_data = playlist_response.model_dump_json(indent=2)

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_data)

    logger.info(f"Playlist data saved to: {filepath}")
    return filepath


def log_playlist_songs(playlist_response):
    """
    Log playlist songs in a formatted way using Pydantic's toString methods.

    Args:
        playlist_response (PlaylistResponse): The playlist response to log
    """
    logger.info("-" * 50)

    # Log each song using Pydantic models' toString methods
    for i, playlist_track in enumerate(playlist_response.items, 1):
        if playlist_track.track:
            # Use the detailed string method for better formatting
            track_details = playlist_track.track.to_detailed_string()
            logger.info(f"{i:3d}. {track_details}")

    # Log summary
    logger.info(f"Total tracks in playlist: {playlist_response.total}")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        logger.error("Usage: python get_playlist_songs.py <playlist_uri>")
        logger.info("\nExamples:")
        logger.info("  python get_playlist_songs.py spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
        logger.info(
            "  python get_playlist_songs.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        )
        sys.exit(1)

    playlist_uri = sys.argv[1]

    # Extract playlist ID for saving
    if playlist_uri.startswith("spotify:playlist:"):
        playlist_id = playlist_uri.split(":")[-1]
    elif "spotify.com/playlist/" in playlist_uri:
        playlist_id = playlist_uri.split("/")[-1].split("?")[0]
    else:
        playlist_id = playlist_uri

    logger.info(f"Fetching songs from playlist: {playlist_id}")

    # Get playlist songs
    if playlist_response := get_playlist_songs(playlist_uri):
        # Log the songs
        log_playlist_songs(playlist_response)

        # Save to JSON file
        save_playlist_to_json(playlist_response, playlist_id)
    else:
        logger.error("Failed to fetch playlist data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
