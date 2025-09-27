# DJ Query Generator - Quick Start

## 🎵 What We Built

An AI-powered system that takes song metadata and generates smart search queries for finding DJ mixes. Instead of searching for random terms, the LLM analyzes the song's characteristics and creates targeted queries that are much more likely to find relevant DJ mixes.

## ✅ What's Ready to Use

1. **Core Query Generator** (`dj_query_generator.py`) - The AI brain that generates queries
2. **Playlist Processor** (`dj_mix_finder.py`) - Processes entire Spotify playlists
3. **Pydantic Models** - Structured, validated outputs (10+ queries per song)
4. **Integration Ready** - Works with your existing Spotify code

## 🚀 Quick Example

```python
from dj_query_generator import DJQueryGenerator
from models import Track, Artist, Album

# Create track (normally from Spotify API)
artist = Artist(name="Bad Bunny")
album = Album(name="Un Verano Sin Ti", release_date="2022-05-06")
track = Track(name="Tití Me Preguntó", artists=[artist], album=album, 
              duration_ms=236000, popularity=90, explicit=True)

# Generate queries with AI
generator = DJQueryGenerator()
result = generator.generate_queries(track)

# Use the queries to search for mixes
for query in result.queries:
    print(f"Search: {query}")
    # → "Bad Bunny reggaeton mix 2022"
    # → "Tití Me Preguntó DJ mix"
    # → "Latin trap megamix 2022"
    # → etc. (10+ total)
```

## 📋 Setup Checklist

- [x] ✅ Install dependencies (`pip install openai pydantic spotipy python-dotenv`)
- [x] ✅ Core functionality tested and working
- [ ] ⚠️ Set `OPENAI_API_KEY` environment variable
- [ ] ⚠️ Set Spotify credentials (for playlist processing)

## 🎯 Key Features

- **Smart Queries**: Generates 10+ diverse, targeted search queries per song
- **Genre Aware**: Understands reggaeton, house, hip-hop, etc. and generates appropriate queries
- **Multiple Query Types**: Artist-focused, genre-specific, era-based, mood-based, etc.
- **Structured Output**: Pydantic models ensure reliable, validated responses
- **Batch Processing**: Handle entire playlists at once

## 📁 Files Created

```
MonolithDev/gettingSongs/
├── dj_query_generator.py      # 🧠 Core AI query generation
├── dj_mix_finder.py           # 🔄 Playlist processing integration  
├── test_core_functionality.py # ✅ Test suite
├── example_usage.py           # 📖 Usage examples
├── DJ_QUERY_GENERATOR_README.md # 📚 Full documentation
└── QUICK_START.md             # 🚀 This file
```

## 🎮 How to Use

### Option 1: Single Track
```bash
# In your Python code
from dj_query_generator import DJQueryGenerator
generator = DJQueryGenerator()
queries = generator.generate_queries(track)
```

### Option 2: Entire Playlist
```bash
# Command line
python3 dj_mix_finder.py spotify:playlist:YOUR_PLAYLIST_ID
```

### Option 3: Test First
```bash
# Test without API keys
python3 test_core_functionality.py

# See examples
python3 example_usage.py
```

## 🔑 Next Steps

1. **Set OpenAI API Key**: `export OPENAI_API_KEY='sk-...'`
2. **Test with Real Data**: Try with your Spotify playlists
3. **Integrate with Search**: Use generated queries to search YouTube/SoundCloud
4. **Download Mixes**: Connect to your existing download pipeline

## 💡 Example Output

For "Todo de Ti" by Rauw Alejandro, generates queries like:
- "reggaeton hits 2021 mix"
- "Rauw Alejandro DJ megamix" 
- "Todo de Ti reggaeton mix"
- "Latin pop 2021 best songs"
- "Puerto Rico reggaeton classics"
- "summer reggaeton party mix"
- "Vice Versa album mix"
- "top reggaeton songs 2020s"
- "Latin urban hits DJ set"
- "perreo reggaeton mix 2021"
- "Rauw Alejandro similar artists mix"

Much better than just searching "Rauw Alejandro"! 🎯