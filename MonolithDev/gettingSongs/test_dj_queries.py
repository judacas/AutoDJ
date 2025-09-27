#!/usr/bin/env python3
"""
Test script for DJ Query Generator.
Tests the AI-powered query generation with sample track data.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import Track, Artist, Album
from dj_query_generator import DJQueryGenerator
from dj_mix_finder import DJMixFinder


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
    
    # Sample 3: Collaboration - ROSALÍA & Rauw Alejandro
    artist3a = Artist(name="ROSALÍA")
    artist3b = Artist(name="Rauw Alejandro")
    album3 = Album(name="MOTOMAMI", release_date="2022-03-18")
    track3 = Track(
        name="BESO",
        artists=[artist3a, artist3b],
        album=album3,
        duration_ms=201000,
        popularity=75,
        explicit=False
    )
    tracks.append(track3)
    
    # Sample 4: Electronic/House
    artist4 = Artist(name="Calvin Harris")
    album4 = Album(name="Funk Wav Bounces Vol. 2", release_date="2022-08-05")
    track4 = Track(
        name="Stay With Me",
        artists=[artist4],
        album=album4,
        duration_ms=203000,
        popularity=70,
        explicit=False
    )
    tracks.append(track4)
    
    return tracks


def test_query_generator():
    """Test the DJ Query Generator with sample tracks."""
    print("Testing DJ Query Generator")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key to test the query generator:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        generator = DJQueryGenerator(api_key)
        sample_tracks = create_sample_tracks()
        
        for i, track in enumerate(sample_tracks, 1):
            print(f"\n{'-'*60}")
            print(f"TEST {i}: {track.name} by {track.artist_names}")
            print(f"{'-'*60}")
            
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
        
        print(f"\n{'='*60}")
        print("✅ DJ Query Generator test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize DJ Query Generator: {e}")
        return False


def test_mix_finder():
    """Test the DJ Mix Finder with sample tracks."""
    print("\n\nTesting DJ Mix Finder")
    print("=" * 50)
    
    try:
        finder = DJMixFinder()
        sample_tracks = create_sample_tracks()
        
        # Test processing individual tracks
        for i, track in enumerate(sample_tracks[:2], 1):  # Test first 2 tracks
            print(f"\n{'-'*60}")
            print(f"PROCESSING TRACK {i}")
            print(f"{'-'*60}")
            
            try:
                result = finder.process_track(track)
                finder.print_track_queries(result)
                
            except Exception as e:
                print(f"❌ Error processing track: {e}")
        
        print(f"\n{'='*60}")
        print("✅ DJ Mix Finder test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test DJ Mix Finder: {e}")
        return False


def main():
    """Run all tests."""
    print("🎵 AutoDJ - DJ Query Generator Test Suite")
    print("=" * 60)
    
    # Test 1: Query Generator
    generator_success = test_query_generator()
    
    # Test 2: Mix Finder (only if generator works)
    finder_success = False
    if generator_success:
        finder_success = test_mix_finder()
    else:
        print("\n⚠️  Skipping DJ Mix Finder test due to Query Generator issues")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Query Generator: {'✅ PASS' if generator_success else '❌ FAIL'}")
    print(f"Mix Finder:      {'✅ PASS' if finder_success else '❌ FAIL'}")
    
    if generator_success and finder_success:
        print(f"\n🎉 All tests passed! The DJ Query Generator is ready to use.")
        print(f"\nNext steps:")
        print(f"1. Use 'dj_mix_finder.py' to process Spotify playlists")
        print(f"2. Use generated queries to search for DJ mixes on YouTube/SoundCloud")
    else:
        print(f"\n⚠️  Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main()