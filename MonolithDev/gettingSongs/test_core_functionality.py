#!/usr/bin/env python3
"""
Core functionality test for DJ Query Generator.
Tests the AI-powered query generation without requiring Spotify credentials.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import Track, Artist, Album
from dj_query_generator import DJQueryGenerator


def create_sample_tracks():
    """Create sample tracks for testing."""
    tracks = []
    
    # Sample 1: Reggaeton - Rauw Alejandro
    artist1 = Artist(name="Rauw Alejandro")
    album1 = Album(name="Vice Versa", release_date="2021-06-25")
    track1 = Track(
        name="Todo de Ti",
        artists=[artist1],
        album=album1,
        duration_ms=196000,
        popularity=85,
        explicit=False
    )
    tracks.append(track1)
    
    # Sample 2: Bad Bunny - Latin Trap
    artist2 = Artist(name="Bad Bunny")
    album2 = Album(name="Un Verano Sin Ti", release_date="2022-05-06")
    track2 = Track(
        name="Tití Me Preguntó",
        artists=[artist2],
        album=album2,
        duration_ms=236000,
        popularity=90,
        explicit=True
    )
    tracks.append(track2)
    
    return tracks


def test_models():
    """Test that Pydantic models work correctly."""
    print("Testing Pydantic Models")
    print("=" * 40)
    
    try:
        sample_tracks = create_sample_tracks()
        
        for i, track in enumerate(sample_tracks, 1):
            print(f"\nTrack {i}:")
            print(f"  Title: {track.name}")
            print(f"  Artist(s): {track.artist_names}")
            print(f"  Album: {track.album.name}")
            print(f"  Duration: {track.duration_formatted}")
            print(f"  Popularity: {track.popularity}")
            print(f"  Release Year: {track.album.release_date[:4] if track.album.release_date else 'Unknown'}")
        
        print(f"\n✅ Pydantic models working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False


def test_query_generator():
    """Test the DJ Query Generator with sample tracks."""
    print("\n\nTesting DJ Query Generator")
    print("=" * 40)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables.")
        print("\nTo test the full functionality, set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nSkipping AI query generation test...")
        return False
    
    try:
        generator = DJQueryGenerator(api_key)
        sample_tracks = create_sample_tracks()
        
        for i, track in enumerate(sample_tracks, 1):
            print(f"\n{'-'*50}")
            print(f"TEST {i}: {track.name} by {track.artist_names}")
            print(f"{'-'*50}")
            
            try:
                result = generator.generate_queries(track)
                
                print(f"✅ Successfully generated {len(result.queries)} queries")
                print(f"\nReasoning: {result.reasoning}")
                print(f"\nSample queries:")
                for j, query in enumerate(result.queries[:5], 1):
                    print(f"  {j}. {query}")
                if len(result.queries) > 5:
                    print(f"  ... and {len(result.queries) - 5} more queries")
                
            except Exception as e:
                print(f"❌ Error generating queries for '{track.name}': {e}")
                return False
        
        print(f"\n{'='*50}")
        print("✅ DJ Query Generator test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize DJ Query Generator: {e}")
        return False


def test_without_openai():
    """Test the basic structure without calling OpenAI API."""
    print("\n\nTesting Core Structure (No API calls)")
    print("=" * 50)
    
    try:
        from dj_query_generator import DJMixQueries
        
        # Test creating a queries object manually
        sample_queries = DJMixQueries(
            queries=[
                "reggaeton hits 2021",
                "Rauw Alejandro mix",
                "Todo de Ti remix",
                "Latin pop 2021",
                "Puerto Rico music",
                "summer reggaeton",
                "Vice Versa album",
                "top reggaeton 2020s",
                "Latin urban mix",
                "perreo reggaeton",
                "Rauw Alejandro similar"
            ],
            reasoning="Test reasoning for sample queries"
        )
        
        print(f"✅ Created DJMixQueries object with {len(sample_queries.queries)} queries")
        print(f"Reasoning: {sample_queries.reasoning}")
        print("\nSample queries:")
        for i, query in enumerate(sample_queries.queries[:5], 1):
            print(f"  {i}. {query}")
        
        # Test JSON serialization
        json_output = sample_queries.model_dump_json(indent=2)
        print(f"\n✅ JSON serialization works (length: {len(json_output)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing core structure: {e}")
        return False


def main():
    """Run all tests."""
    print("🎵 AutoDJ - DJ Query Generator Core Test Suite")
    print("=" * 60)
    
    # Test 1: Pydantic Models
    models_success = test_models()
    
    # Test 2: Core Structure
    structure_success = test_without_openai()
    
    # Test 3: Query Generator with API (if available)
    api_success = test_query_generator()
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Pydantic Models:  {'✅ PASS' if models_success else '❌ FAIL'}")
    print(f"Core Structure:   {'✅ PASS' if structure_success else '❌ FAIL'}")
    print(f"OpenAI API Test:  {'✅ PASS' if api_success else '⚠️ SKIPPED (no API key)'}")
    
    if models_success and structure_success:
        print(f"\n🎉 Core functionality is working!")
        if api_success:
            print(f"🎉 Full AI functionality is working!")
            print(f"\nYou can now use:")
            print(f"1. dj_query_generator.py for individual tracks")
            print(f"2. dj_mix_finder.py for processing playlists")
        else:
            print(f"\n⚠️  To test AI functionality, set OPENAI_API_KEY environment variable")
            print(f"   export OPENAI_API_KEY='your-api-key-here'")
    else:
        print(f"\n❌ Some core tests failed. Check the error messages above.")
    
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET (optional)")
    print("3. Use the DJ Query Generator in your project:")
    print("   from dj_query_generator import DJQueryGenerator")
    print("   generator = DJQueryGenerator()")
    print("   queries = generator.generate_queries(track)")


if __name__ == "__main__":
    main()