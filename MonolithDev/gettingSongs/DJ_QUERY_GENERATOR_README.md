# DJ Query Generator - AI-Powered Mix Discovery

An OpenAI-powered system that generates intelligent search queries for finding DJ mixes based on Spotify track metadata.

## Overview

The DJ Query Generator analyzes song characteristics (genre, artist, release year, popularity, etc.) and uses AI to generate diverse, effective search queries that help find relevant DJ mixes on platforms like YouTube, SoundCloud, and Mixcloud.

## Features

- **AI-Powered Query Generation**: Uses OpenAI GPT-4o-mini to generate contextually relevant search queries
- **Structured Outputs**: Uses Pydantic models for reliable, validated responses
- **Genre-Aware**: Understands different music genres and their mixing patterns
- **Diverse Query Types**: Generates various query types (genre-specific, artist-focused, era-based, mood-based, etc.)
- **Spotify Integration**: Seamlessly works with existing Spotify playlist data
- **Batch Processing**: Can process entire playlists at once

## Setup

### 1. Install Dependencies

```bash
pip install openai==1.54.3 pydantic==2.11
```

### 2. Set OpenAI API Key

Add your OpenAI API key to your `.env` file:

```bash
echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env
```

Or export it as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## Usage

### Basic Usage - Individual Track

```python
from dj_query_generator import DJQueryGenerator
from models import Track, Artist, Album

# Create track object (normally from Spotify API)
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

# Generate queries
generator = DJQueryGenerator()
queries = generator.generate_queries(track)

print(f"Generated {len(queries.queries)} queries:")
for i, query in enumerate(queries.queries, 1):
    print(f"{i}. {query}")
```

### Process Entire Playlist

```python
from dj_mix_finder import DJMixFinder

# Process a Spotify playlist
finder = DJMixFinder()
results = finder.process_playlist("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")

# Results are automatically saved to JSON files
```

### Command Line Usage

```bash
# Process a playlist and generate queries for all tracks
python dj_mix_finder.py spotify:playlist:37i9dQZF1DXcBWIGoYBM5M

# Test the system with sample data
python test_dj_queries.py
```

## Query Types Generated

The AI generates diverse query types including:

1. **Genre-Specific**: "reggaeton hits 2025", "deep house classics"
2. **Artist-Focused**: "Bad Bunny DJ mix", "Rauw Alejandro megamix"
3. **Era/Year-Based**: "2024 Latin hits", "summer 2025 reggaeton"
4. **Mood/Style**: "party reggaeton mix", "chill Latin vibes"
5. **Chart-Based**: "top 40 Latin", "Billboard Latin hits"
6. **Format-Specific**: "reggaeton megamix", "Latin trap continuous mix"
7. **Context-Based**: "workout reggaeton", "club bangers 2025"
8. **Collaboration**: "Latin pop collaborations", "reggaeton duets"
9. **Regional**: "Puerto Rico hits", "Latin America top songs"
10. **Similarity**: "songs like Todo de Ti", "similar to Rauw Alejandro"

## Example Output

For a reggaeton track like "Todo de Ti" by Rauw Alejandro, the system might generate:

```json
{
  "queries": [
    "reggaeton hits 2021 mix",
    "Rauw Alejandro DJ megamix",
    "Todo de Ti reggaeton mix",
    "Latin pop 2021 best songs",
    "Puerto Rico reggaeton classics",
    "summer reggaeton party mix",
    "Vice Versa album mix",
    "top reggaeton songs 2020s",
    "Latin urban hits DJ set",
    "perreo reggaeton mix 2021",
    "Rauw Alejandro similar artists mix"
  ],
  "reasoning": "Generated queries focusing on reggaeton genre, artist popularity, album context, and temporal relevance for optimal DJ mix discovery"
}
```

## File Structure

```
MonolithDev/gettingSongs/
├── dj_query_generator.py      # Core AI query generation logic
├── dj_mix_finder.py           # Integration with Spotify + batch processing
├── test_dj_queries.py         # Test suite with sample data
├── models.py                  # Pydantic models for Spotify data
├── config.py                  # Configuration (API keys)
└── DJ_QUERY_GENERATOR_README.md
```

## Output Files

When processing playlists, the system creates:

- `dj_queries/track_001_song_name.json` - Individual track queries
- `dj_queries/track_002_song_name.json` - Individual track queries
- `dj_queries/summary.json` - Overview of all generated queries

## Error Handling

The system gracefully handles:
- Missing OpenAI API key (with helpful error messages)
- API rate limits and errors
- Invalid track data
- Network connectivity issues

## Testing

Run the test suite to verify everything works:

```bash
python test_dj_queries.py
```

This will test the system with sample tracks representing different genres.

## Integration with Download Pipeline

The query generator integrates seamlessly with your existing Spotify workflow:

1. **Get Playlist** → `get_playlist_songs.py`
2. **Generate Queries** → `dj_query_generator.py`
3. **Find Mixes** → Use queries to search YouTube/SoundCloud
4. **Download** → Your existing download logic

## Cost Considerations

- Uses GPT-4o-mini for cost efficiency
- Structured outputs reduce token usage
- Typical cost: ~$0.001-0.002 per track
- Batch processing for better efficiency

## Troubleshooting

### "OpenAI API key not found"
- Set `OPENAI_API_KEY` in your `.env` file
- Verify the key is correct

### "Failed to generate queries"
- Check internet connection
- Verify OpenAI API key has sufficient credits
- Check for API rate limits

### Poor query quality
- Ensure track metadata is complete
- Check that genre/artist information is accurate

## Next Steps

1. Use generated queries with YouTube/SoundCloud APIs
2. Implement automatic mix downloading based on queries
3. Add query ranking/scoring system
4. Implement caching to avoid regenerating queries

## Support

For issues or questions about the DJ Query Generator, check:
1. Error messages (they're designed to be helpful)
2. Test suite output (`python test_dj_queries.py`)
3. OpenAI API status page
4. Your API key credits/limits