"""
Configuration file for AutoDJ Spotify integration.

This module provides configuration loading with lazy initialization.
Use init_config() explicitly or access the constants which auto-initialize.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Global flag to track initialization
_initialized = False


def init_config() -> None:
    """
    Initialize configuration by loading environment variables.

    This function is safe to call multiple times - it will only
    load the environment once.

    Raises:
        ValueError: If required Spotify credentials are missing.
    """
    global _initialized
    if _initialized:
        return

    # Load .env file
    load_dotenv()
    _initialized = True

    # Validate required credentials
    if not os.getenv("SPOTIFY_CLIENT_ID") or not os.getenv("SPOTIFY_CLIENT_SECRET"):
        raise ValueError(
            "Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file. "
            "Get these from https://developer.spotify.com/dashboard"
        )


# Auto-initializing getters
def get_spotify_client_id() -> str:
    """Get Spotify Client ID (auto-initializes config if needed)."""
    init_config()
    return os.getenv("SPOTIFY_CLIENT_ID", "")


def get_spotify_client_secret() -> str:
    """Get Spotify Client Secret (auto-initializes config if needed)."""
    init_config()
    return os.getenv("SPOTIFY_CLIENT_SECRET", "")


def get_spotify_redirect_uri() -> str:
    """Get Spotify Redirect URI (auto-initializes config if needed)."""
    init_config()
    return os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")


def get_spotify_cache_path() -> str:
    """Get Spotify Cache Path (auto-initializes config if needed)."""
    init_config()
    return os.getenv("SPOTIFY_CACHE_PATH", ".spotify_cache")


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API Key (auto-initializes config if needed)."""
    init_config()
    return os.getenv("OPENAI_API_KEY")


# Constants for backward compatibility (lazy-loaded)
SPOTIFY_CLIENT_ID = get_spotify_client_id()
SPOTIFY_CLIENT_SECRET = get_spotify_client_secret()
SPOTIFY_REDIRECT_URI = get_spotify_redirect_uri()
SPOTIFY_CACHE_PATH = get_spotify_cache_path()
OPENAI_API_KEY = get_openai_api_key()
