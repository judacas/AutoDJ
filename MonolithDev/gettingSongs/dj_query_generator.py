#!/usr/bin/env python3
"""
DJ Mix Query Generator using OpenAI API with structured outputs.
Generates relevant search queries for DJ mixes based on song metadata.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from models import Track, Artist, Album


class DJMixQueries(BaseModel):
    """Structured output model for DJ mix queries."""
    
    queries: List[str] = Field(
        ..., 
        min_length=10,
        description="List of at least 10 search queries for finding DJ mixes related to the input song"
    )
    reasoning: str = Field(
        ..., 
        description="Brief explanation of the query generation strategy based on the song's characteristics"
    )


class DJQueryGenerator:
    """
    OpenAI-powered generator for creating DJ mix search queries based on song metadata.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DJ Query Generator.
        
        Args:
            api_key: OpenAI API key. If None, will look for OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_queries(self, track: Track) -> DJMixQueries:
        """
        Generate search queries for DJ mixes based on track metadata.
        
        Args:
            track: Spotify track object with metadata
            
        Returns:
            DJMixQueries: Object containing generated queries and reasoning
        """
        # Prepare track information for the prompt
        track_info = self._prepare_track_info(track)
        
        # Create the system prompt
        system_prompt = self._create_system_prompt()
        
        # Create the user prompt with track information
        user_prompt = self._create_user_prompt(track_info)
        
        try:
            # Call OpenAI API with structured output
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=DJMixQueries,
                temperature=0.7,
                max_tokens=1500
            )
            
            return completion.choices[0].message.parsed
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate queries: {str(e)}")
    
    def _prepare_track_info(self, track: Track) -> dict:
        """
        Extract relevant information from track metadata.
        
        Args:
            track: Spotify track object
            
        Returns:
            Dictionary with formatted track information
        """
        return {
            "title": track.name,
            "artists": [artist.name for artist in track.artists],
            "album": track.album.name,
            "release_year": track.album.release_date[:4] if track.album.release_date else "Unknown",
            "duration": track.duration_formatted,
            "popularity": track.popularity,
            "explicit": track.explicit
        }
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM."""
        return """You are a DJ mix query generation specialist. Your job is to analyze song metadata and generate diverse, effective search queries that would help find DJ mixes containing that song or similar music.

Your expertise includes:
- Understanding music genres, subgenres, and their evolution
- Recognizing popular DJ mix formats and naming conventions
- Identifying temporal trends in music (decades, years, seasons)
- Understanding regional music scenes and cultural contexts
- Recognizing chart patterns and hit song characteristics

For each song, generate at least 10 diverse search queries that would likely return relevant DJ mixes. Consider:
1. Genre-specific searches (e.g., "reggaeton hits 2025", "deep house classics")
2. Artist-focused searches (e.g., "Bad Bunny DJ mix", "Rauw Alejandro megamix")
3. Era/year-based searches (e.g., "2024 Latin hits", "summer 2025 reggaeton")
4. Mood/style searches (e.g., "party reggaeton mix", "chill Latin vibes")
5. Chart-based searches (e.g., "top 40 Latin", "Billboard Latin hits")
6. DJ/mix format searches (e.g., "reggaeton megamix", "Latin trap continuous mix")
7. Event/context searches (e.g., "workout reggaeton", "club bangers 2025")
8. Collaboration searches (e.g., "Latin pop collaborations", "reggaeton duets")
9. Regional searches (e.g., "Puerto Rico hits", "Latin America top songs")
10. Similarity searches (e.g., "songs like [title]", "similar to [artist]")

Make queries natural and search-engine friendly. Avoid overly complex or niche terms that wouldn't yield results."""
    
    def _create_user_prompt(self, track_info: dict) -> str:
        """
        Create the user prompt with track information.
        
        Args:
            track_info: Dictionary containing track metadata
            
        Returns:
            Formatted prompt string
        """
        artists_str = ", ".join(track_info["artists"])
        
        return f"""Generate search queries for DJ mixes based on this song:

**Song Details:**
- Title: {track_info["title"]}
- Artist(s): {artists_str}
- Album: {track_info["album"]}
- Release Year: {track_info["release_year"]}
- Duration: {track_info["duration"]}
- Popularity Score: {track_info["popularity"]}/100
- Explicit: {track_info["explicit"]}

Based on this information, analyze the song's characteristics and generate at least 10 diverse search queries that would help find DJ mixes containing this song or similar music. Consider the genre, artist popularity, release timing, and musical style.

Provide a mix of specific and broad queries that would work well on platforms like YouTube, SoundCloud, or Mixcloud."""


def main():
    """Example usage of the DJ Query Generator."""
    # This is just for testing - you'd normally get this from your Spotify integration
    from models import Track, Artist, Album
    
    # Example track data (this would come from Spotify)
    artist = Artist(name="Rauw Alejandro")
    album = Album(name="Vice Versa", release_date="2021-06-25")
    track = Track(
        name="Todo de Ti",
        artists=[artist],
        album=album,
        duration_ms=196000,
        popularity=85,
        explicit=False
    )
    
    try:
        generator = DJQueryGenerator()
        queries = generator.generate_queries(track)
        
        print(f"Generated queries for: {track.name} by {track.artist_names}")
        print(f"\nReasoning: {queries.reasoning}")
        print(f"\nQueries ({len(queries.queries)} total):")
        for i, query in enumerate(queries.queries, 1):
            print(f"{i:2d}. {query}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()