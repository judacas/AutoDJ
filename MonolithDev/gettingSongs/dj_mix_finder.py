#!/usr/bin/env python3
"""
DJ Mix Finder - Integrates AI-powered query generation with mix discovery.
This module combines the Spotify track analysis with OpenAI query generation
to find relevant DJ mixes.
"""

import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from get_playlist_songs import get_playlist_songs
from dj_query_generator import DJQueryGenerator, DJMixQueries
from models import Track, PlaylistResponse
from config import OPENAI_API_KEY


class DJMixSearchResults(BaseModel):
    """Results from DJ mix search for a track."""
    
    track_info: Dict[str, Any] = Field(..., description="Original track metadata")
    generated_queries: DJMixQueries = Field(..., description="AI-generated search queries")
    search_timestamp: str = Field(..., description="When the search was performed")


class DJMixFinder:
    """
    Main class for finding DJ mixes based on playlist tracks using AI-generated queries.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the DJ Mix Finder.
        
        Args:
            openai_api_key: OpenAI API key for query generation
        """
        self.api_key = openai_api_key or OPENAI_API_KEY
        self.query_generator = None
        
        if self.api_key:
            try:
                self.query_generator = DJQueryGenerator(self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize query generator: {e}")
        else:
            print("Warning: No OpenAI API key provided. Query generation disabled.")
    
    def process_playlist(self, playlist_uri: str, output_dir: str = "dj_queries") -> List[DJMixSearchResults]:
        """
        Process all tracks in a playlist and generate DJ mix queries for each.
        
        Args:
            playlist_uri: Spotify playlist URI
            output_dir: Directory to save query results
            
        Returns:
            List of search results for each track
        """
        print(f"Processing playlist: {playlist_uri}")
        
        # Get playlist data
        playlist_response = get_playlist_songs(playlist_uri)
        if not playlist_response:
            raise ValueError("Failed to fetch playlist data")
        
        print(f"Found {len(playlist_response.items)} tracks in playlist")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # Process each track
        for i, playlist_track in enumerate(playlist_response.items, 1):
            if not playlist_track.track:
                print(f"Skipping track {i}: No track data available")
                continue
            
            track = playlist_track.track
            print(f"\nProcessing track {i}: {track.name} by {track.artist_names}")
            
            try:
                result = self.process_track(track)
                results.append(result)
                
                # Save individual result
                self._save_track_queries(result, output_path, i)
                
                print(f"✓ Generated {len(result.generated_queries.queries)} queries for '{track.name}'")
                
            except Exception as e:
                print(f"✗ Error processing track '{track.name}': {e}")
                continue
        
        # Save summary
        self._save_summary(results, output_path, playlist_uri)
        
        print(f"\n✓ Processing complete! Generated queries for {len(results)} tracks")
        print(f"Results saved to: {output_path.absolute()}")
        
        return results
    
    def process_track(self, track: Track) -> DJMixSearchResults:
        """
        Process a single track and generate DJ mix queries.
        
        Args:
            track: Spotify track object
            
        Returns:
            Search results with generated queries
        """
        if not self.query_generator:
            raise RuntimeError("Query generator not initialized. Check OpenAI API key.")
        
        # Generate queries using AI
        queries = self.query_generator.generate_queries(track)
        
        # Prepare track info
        track_info = {
            "title": track.name,
            "artists": [artist.name for artist in track.artists],
            "album": track.album.name,
            "release_year": track.album.release_date[:4] if track.album.release_date else "Unknown",
            "duration": track.duration_formatted,
            "popularity": track.popularity,
            "explicit": track.explicit,
            "spotify_uri": track.uri
        }
        
        # Create result object
        from datetime import datetime
        result = DJMixSearchResults(
            track_info=track_info,
            generated_queries=queries,
            search_timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def _save_track_queries(self, result: DJMixSearchResults, output_path: Path, track_num: int):
        """Save queries for a single track."""
        filename = f"track_{track_num:03d}_{self._sanitize_filename(result.track_info['title'])}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.model_dump_json(indent=2))
    
    def _save_summary(self, results: List[DJMixSearchResults], output_path: Path, playlist_uri: str):
        """Save a summary of all generated queries."""
        summary = {
            "playlist_uri": playlist_uri,
            "total_tracks_processed": len(results),
            "generation_timestamp": results[0].search_timestamp if results else None,
            "tracks": []
        }
        
        for i, result in enumerate(results, 1):
            track_summary = {
                "track_number": i,
                "title": result.track_info["title"],
                "artists": result.track_info["artists"],
                "query_count": len(result.generated_queries.queries),
                "reasoning": result.generated_queries.reasoning,
                "top_5_queries": result.generated_queries.queries[:5]
            }
            summary["tracks"].append(track_summary)
        
        filepath = output_path / "summary.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe saving."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        return filename[:50]
    
    def print_track_queries(self, result: DJMixSearchResults):
        """
        Print formatted queries for a track.
        
        Args:
            result: Search results to display
        """
        track_info = result.track_info
        queries = result.generated_queries
        
        print(f"\n{'='*60}")
        print(f"TRACK: {track_info['title']}")
        print(f"ARTIST(S): {', '.join(track_info['artists'])}")
        print(f"ALBUM: {track_info['album']}")
        print(f"YEAR: {track_info['release_year']}")
        print(f"{'='*60}")
        
        print(f"\nREASONING:")
        print(f"{queries.reasoning}")
        
        print(f"\nGENERATED QUERIES ({len(queries.queries)} total):")
        for i, query in enumerate(queries.queries, 1):
            print(f"{i:2d}. {query}")
        
        print(f"\n{'='*60}")


def main():
    """Main function for command-line usage."""
    if len(sys.argv) != 2:
        print("Usage: python dj_mix_finder.py <playlist_uri>")
        print("\nExample:")
        print("  python dj_mix_finder.py spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
        sys.exit(1)
    
    playlist_uri = sys.argv[1]
    
    try:
        finder = DJMixFinder()
        results = finder.process_playlist(playlist_uri)
        
        # Print results for first few tracks as preview
        print(f"\n{'='*80}")
        print(f"PREVIEW: First 3 tracks with generated queries")
        print(f"{'='*80}")
        
        for result in results[:3]:
            finder.print_track_queries(result)
        
        if len(results) > 3:
            print(f"\n... and {len(results) - 3} more tracks. Check the saved files for complete results.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()