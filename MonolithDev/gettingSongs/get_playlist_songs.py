#!/usr/bin/env python3
"""
Simple script to fetch and display songs from a Spotify playlist.
Usage: python get_playlist_songs.py <playlist_uri>
"""

import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from models import PlaylistResponse, PlaylistTrack, Track


def get_playlist_songs(playlist_uri):
    """
    Fetch songs from a Spotify playlist and print them.

    Args:
        playlist_uri (str): Spotify playlist URI (e.g., spotify:playlist:37i9dQZF1DXcBWIGoYBM5M)
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

        print(f"Fetching songs from playlist: {playlist_id}")
        print("-" * 50)

        # Get playlist tracks
        raw_results = sp.playlist_tracks(playlist_id)

        # Parse response using Pydantic model
        try:
            playlist_response = PlaylistResponse.model_validate(raw_results)
        except Exception as e:
            print(f"Error parsing playlist response: {e}")
            return

        if not playlist_response.items:
            print("No songs found in this playlist.")
            return

        # Print each song using Pydantic models
        for i, playlist_track in enumerate(playlist_response.items, 1):
            if playlist_track.track:
                track = playlist_track.track

                print(f"{i:3d}. {track.name}")
                print(f"     Artist(s): {track.artist_names}")
                print(f"     Album: {track.album.name}")
                print(f"     Duration: {track.duration_formatted}")
                print()

        # Print summary
        print(f"Total tracks in playlist: {playlist_response.total}")

    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify API error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python get_playlist_songs.py <playlist_uri>")
        print("\nExamples:")
        print("  python get_playlist_songs.py spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
        print(
            "  python get_playlist_songs.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        )
        sys.exit(1)

    playlist_uri = sys.argv[1]
    get_playlist_songs(playlist_uri)


if __name__ == "__main__":
    main()
