#!/usr/bin/env python3
"""
Example usage of the DJ Query Generator.
Shows how to integrate the AI-powered query generation into your workflow.
"""

import os
from models import Track, Artist, Album
from dj_query_generator import DJQueryGenerator


def example_single_track():
    """Example: Generate queries for a single track."""
    print("=" * 60)
    print("EXAMPLE 1: Single Track Query Generation")
    print("=" * 60)
    
    # Create a sample track (in real usage, this would come from Spotify API)
    artist = Artist(name="Bad Bunny")
    album = Album(name="Un Verano Sin Ti", release_date="2022-05-06")
    track = Track(
        name="Tití Me Preguntó",
        artists=[artist],
        album=album,
        duration_ms=236000,
        popularity=90,
        explicit=True
    )
    
    print(f"Track: {track.name}")
    print(f"Artist: {track.artist_names}")
    print(f"Album: {track.album.name}")
    print(f"Year: {track.album.release_date[:4]}")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Set OPENAI_API_KEY to see AI-generated queries")
        print("Here's what the output would look like:")
        print("\nSample queries that would be generated:")
        sample_queries = [
            "Bad Bunny reggaeton mix 2022",
            "Tití Me Preguntó DJ mix",
            "Un Verano Sin Ti album mix",
            "reggaeton hits 2022 summer",
            "Latin trap megamix 2022",
            "Puerto Rico reggaeton 2020s",
            "perreo reggaeton mix",
            "Bad Bunny similar artists",
            "top reggaeton songs 2022",
            "Latin urban hits DJ set"
        ]
        for i, query in enumerate(sample_queries, 1):
            print(f"  {i:2d}. {query}")
        return
    
    try:
        # Generate queries using AI
        generator = DJQueryGenerator()
        result = generator.generate_queries(track)
        
        print(f"\n✅ Generated {len(result.queries)} DJ mix queries:")
        print(f"\nReasoning: {result.reasoning}")
        print(f"\nQueries:")
        for i, query in enumerate(result.queries, 1):
            print(f"  {i:2d}. {query}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_workflow_integration():
    """Example: How to integrate into your existing workflow."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Workflow Integration")
    print("=" * 60)
    
    print("""
TYPICAL WORKFLOW:

1. GET PLAYLIST DATA (existing code):
   from get_playlist_songs import get_playlist_songs
   playlist = get_playlist_songs("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")

2. GENERATE QUERIES FOR EACH TRACK (new code):
   from dj_query_generator import DJQueryGenerator
   generator = DJQueryGenerator()
   
   for playlist_track in playlist.items:
       if playlist_track.track:
           queries = generator.generate_queries(playlist_track.track)
           # Now you have 10+ targeted search queries for this song

3. SEARCH FOR MIXES (your code):
   for query in queries.queries:
       # Search YouTube: f"https://www.youtube.com/results?search_query={query}"
       # Search SoundCloud: f"https://soundcloud.com/search?q={query}"
       # Search Mixcloud: f"https://www.mixcloud.com/search/?q={query}"
       pass

4. DOWNLOAD MIXES (your existing download code):
   # Use your existing download logic with the found mixes
   pass
""")


def example_different_genres():
    """Example: Show how different genres generate different queries."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Genre-Specific Query Generation")
    print("=" * 60)
    
    # Different genre examples
    genres_examples = [
        {
            "name": "Reggaeton/Latin Trap",
            "artist": "Bad Bunny",
            "song": "Tití Me Preguntó",
            "sample_queries": [
                "reggaeton hits 2022",
                "Bad Bunny DJ mix",
                "Latin trap megamix",
                "perreo reggaeton mix",
                "Puerto Rico music 2020s"
            ]
        },
        {
            "name": "Deep House/Electronic",
            "artist": "Disclosure",
            "song": "Latch",
            "sample_queries": [
                "deep house classics",
                "UK garage house mix",
                "electronic dance mix 2010s",
                "Disclosure similar artists",
                "house music continuous mix"
            ]
        },
        {
            "name": "Hip-Hop/Rap",
            "artist": "Drake",
            "song": "God's Plan",
            "sample_queries": [
                "Drake hits megamix",
                "hip hop 2018 hits",
                "rap songs like God's Plan",
                "Toronto hip hop mix",
                "mainstream rap DJ set"
            ]
        }
    ]
    
    for example in genres_examples:
        print(f"\n🎵 {example['name']}:")
        print(f"   Example: {example['song']} by {example['artist']}")
        print(f"   Sample queries that would be generated:")
        for i, query in enumerate(example['sample_queries'], 1):
            print(f"     {i}. {query}")


def main():
    """Run all examples."""
    print("🎵 AutoDJ - DJ Query Generator Examples")
    
    # Example 1: Single track
    example_single_track()
    
    # Example 2: Workflow integration
    example_workflow_integration()
    
    # Example 3: Different genres
    example_different_genres()
    
    print("\n\n" + "=" * 60)
    print("GETTING STARTED")
    print("=" * 60)
    print("1. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print("")
    print("2. For Spotify integration, also set:")
    print("   export SPOTIFY_CLIENT_ID='your-spotify-client-id'")
    print("   export SPOTIFY_CLIENT_SECRET='your-spotify-client-secret'")
    print("")
    print("3. Use the query generator in your code:")
    print("   from dj_query_generator import DJQueryGenerator")
    print("   generator = DJQueryGenerator()")
    print("   queries = generator.generate_queries(track)")
    print("")
    print("4. Process entire playlists:")
    print("   python3 dj_mix_finder.py spotify:playlist:YOUR_PLAYLIST_ID")


if __name__ == "__main__":
    main()