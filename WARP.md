# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repo overview
- Language/tooling: Python (3.13). Testing via pytest (+ pytest-asyncio, pytest-cov). Formatting/linting via Black, isort, Flake8, MyPy, Pylint. FastAPI and Uvicorn are included for a future API layer. Azure SDKs (Blob Storage, Functions) and PostgreSQL stack (psycopg2 + SQLAlchemy + pydantic) are present. FFmpeg is required for audio processing.
- Purpose (from README): “app that mixes songs together automatically.”
- Rules (from .cursor/.cursorrules): Project follows an 8-stage pipeline (source → related mixes → blob storage → fingerprinting → recognition → transition detection → transition extraction → transition graph). Python standards: type hints, Black (88 cols), dataclasses, async I/O, pathlib, logging. Separate MVP vs Full implementations; Azure-specific code in azure/; configuration in config/. Storage: PostgreSQL for structured data; Azure Blob for audio.

Common commands (PowerShell on Windows)
- Environment setup
```powershell path=null start=null
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```
- Format and lint
```powershell path=null start=null
# Format
black .
isort .

# Lint
flake8 .
# Static type check
mypy .
# Optional additional linter
pylint graphStuff MonolithDev
```
- Tests
```powershell path=null start=null
# Run all tests quietly
pytest -q

# With coverage (adjust targets as code grows)
pytest --cov=graphStuff --cov-report=term-missing -q

# Run a single test
pytest tests/test_graph.py::test_add_transition -q

# Filter by keyword
pytest -k "graph and transition" -q
```
- FastAPI (when API module exists)
```powershell path=null start=null
# Replace app.main:app with the actual module:var when added
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Notes
  - Ensure FFmpeg is installed and available on PATH before running audio-related steps.

High-level architecture and structure
- Pipeline (big picture)
  1) Get Source Song (YouTube/multi-source search)
  2) Find Related Mixes (preset → LLM-generated queries)
  3) Store audio in Azure Blob Storage
  4) Fingerprinting (DejaVu)
  5) Song-in-Mix Recognition (DejaVu + AUDAlign)
  6) Transition Detection (heuristics → quality metrics)
  7) Transition Extraction (local → Azure Functions)
  8) Transition Graph (nodes=songs, edges=transitions)

- Current code focus
  - graphStuff/graph.py exposes a simple, in-memory directed graph for transitions:
    - SongNode: id + metadata
    - TransitionEdge: source/target song_id, timestamp, mix_id, confidence, extra
    - DirectedSongGraph: add_song, add_transition, get_neighbors, get_out_edges, get_song
  - MonolithDev/gettingSongs/scrapper.py is a placeholder for future ingestion.

- Intended layout (from Cursor rules)
  - Keep MVP (local, simple) and Full (Azure Functions, multi-source) in separate modules.
  - Use clear module names per stage (e.g., song_search.py, fingerprinting.py, transition_graph.py).
  - Place Azure-specific code in azure/ and configuration in config/.
  - Use PostgreSQL (SQLAlchemy + psycopg2) for structured data; avoid raw SQL where possible.

- Data flow (conceptual)
  - Ingestion → Storage (Azure Blob) → Processing (fingerprinting/recognition) → Transition Extraction → Graph update (DirectedSongGraph and, later, persisted DB model).

- Testing approach (from Cursor rules)
  - Unit tests for core functions (e.g., graph operations, detection logic units).
  - Integration tests across pipeline boundaries; mock external services (YouTube, Azure).
  - Include pytest-asyncio for async I/O code.

References
- README.md: brief description.
- .cursor/.cursorrules: canonical source for pipeline stages, coding standards, and directory conventions.
