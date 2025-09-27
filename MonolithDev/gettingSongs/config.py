"""
Configuration file for AutoDJ Spotify integration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"
)
SPOTIFY_CACHE_PATH = os.getenv("SPOTIFY_CACHE_PATH", ".spotify_cache")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate required credentials
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError(
        "Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file. "
        "Get these from https://developer.spotify.com/dashboard"
    )
