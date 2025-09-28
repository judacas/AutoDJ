# Getting Songs Scripts

This folder contains scripts for fetching and working with Spotify playlist data.

## Files

- `models.py` - Pydantic models for Spotify data structures (Track, Artist, Album, Playlist)
- `get_playlist_songs.py` - Script to fetch and display playlist songs using Pydantic models
- `download_all_songs.py` - Script to download all songs from a playlist using YouTube via yt-dlp
- `config.py` - Configuration for Spotify API credentials

## get_playlist_songs.py

A simple script that takes a Spotify playlist URI as an argument and prints out all the songs in the playlist. The script uses Pydantic models for type safety and data validation.

### Usage

```bash
python get_playlist_songs.py <playlist_uri>
```

### Examples

```bash
# Using Spotify URI format
python get_playlist_songs.py spotify:playlist:37i9dQZF1DXcBWIGoYBM5M

# Using Spotify URL format
python get_playlist_songs.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

### Prerequisites

1. Make sure you have set up your Spotify API credentials in a `.env` file (see `SPOTIFY_SETUP.md` in the project root)
2. Install dependencies: `pip install -r requirements.txt`

### Features

- **Type Safety**: Uses Pydantic models for data validation and type safety
- **Clean Data Access**: Access track properties through clean, typed attributes
- **Error Handling**: Robust error handling for API responses and data parsing
- **Formatted Output**: Clean, readable output with proper formatting

### Output

The script will display:
- Song name
- Artist(s)
- Album name
- Duration (in MM:SS format)
- Total number of tracks in the playlist

### Error Handling

The script handles:
- Invalid playlist URIs
- Network errors
- Spotify API errors
- Empty playlists

## download_all_songs.py

A script that downloads all songs from a Spotify playlist by searching YouTube and downloading the audio files. The script reads from existing playlist JSON files created by `get_playlist_songs.py`.

### Usage

```bash
python download_all_songs.py <playlist_id>
```

### Examples

```bash
# Download all songs from a playlist
python download_all_songs.py 5evvXuuNDgAHbPDmojLZgD

# Download all songs from another playlist
python download_all_songs.py 37i9dQZF1DXcBWIGoYBM5M
```

### Prerequisites

1. First run `get_playlist_songs.py` to create the playlist JSON file
2. Install dependencies: `pip install -r requirements.txt`
3. Install ffmpeg for audio conversion

### Features

- **Idempotent Downloads**: Already downloaded tracks are skipped
- **YouTube Search**: Automatically searches YouTube for each track
- **Audio Conversion**: Downloads and converts to MP3 format (192kbps)
- **Progress Tracking**: Shows progress and summary statistics
- **Error Handling**: Continues downloading even if individual tracks fail

### Azure Blob Storage Configuration

Downloaded audio is now staged locally and then uploaded to Azure Blob Storage.
Set the following environment variables before running any download commands:

| Variable | Description |
| --- | --- |
| `AZURE_BLOB_CONTAINER` | Name of the blob container where audio files will be stored. |
| `AZURE_BLOB_ROOT_PATH` | Optional prefix inside the container (defaults to `playlists`). |
| `AZURE_STORAGE_CONNECTION_STRING` | Full connection string for the storage account (preferred). |
| `AZURE_STORAGE_ACCOUNT_URL` | Account URL when not using a connection string (e.g. `https://<account>.blob.core.windows.net`). |
| `AZURE_STORAGE_SAS_TOKEN` / `AZURE_STORAGE_ACCOUNT_KEY` | Authentication credentials when using `AZURE_STORAGE_ACCOUNT_URL`. |

If neither a connection string nor an account URL with credentials is provided, the downloader will abort with an informative error.

#### Option A – Provisioning via Azure Portal

1. Create a **Storage Account** (Standard V2) in the Azure Portal.
2. Inside the storage account, create a **Blob Container** for AutoDJ audio (e.g. `autodj-audio`).
3. Generate credentials:
   - Either copy the **Connection string** from **Access keys**, or
   - Generate a **SAS token** from the container (ensure `Create` and `Write` permissions).
4. Export the variables locally:

```bash
export AZURE_BLOB_CONTAINER="autodj-audio"
export AZURE_STORAGE_CONNECTION_STRING="<portal-connection-string>"
# Optional: override the folder prefix inside the container
export AZURE_BLOB_ROOT_PATH="playlists"
```

5. Run the playlist pipeline as usual. The Postgres `downloads` table now stores the blob URL instead of a local file path.

#### Option B – Provisioning via Azure CLI

```bash
# Log in and choose a subscription
az login
az account set --subscription "<subscription-name-or-id>"

# Variables
RESOURCE_GROUP="autodj-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="autodjstorage$RANDOM"
CONTAINER="autodj-audio"

# Create resource group & storage
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
az storage account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$STORAGE_ACCOUNT" \
  --sku Standard_LRS \
  --kind StorageV2

# Create container and fetch connection string
az storage container create \
  --name "$CONTAINER" \
  --account-name "$STORAGE_ACCOUNT"

CONNECTION_STRING=$(az storage account show-connection-string \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query connectionString -o tsv)

export AZURE_BLOB_CONTAINER="$CONTAINER"
export AZURE_STORAGE_CONNECTION_STRING="$CONNECTION_STRING"
```

You can substitute the connection string with a SAS token instead:

```bash
SAS_TOKEN=$(az storage container generate-sas \
  --name "$CONTAINER" \
  --account-name "$STORAGE_ACCOUNT" \
  --permissions acdlrw \
  --expiry "$(date -u -d '+30 days' +%Y-%m-%dT%H:%MZ)" \
  -o tsv)

export AZURE_STORAGE_ACCOUNT_URL="https://$STORAGE_ACCOUNT.blob.core.windows.net"
export AZURE_STORAGE_SAS_TOKEN="?$SAS_TOKEN"
```

### Output

The script will:
- Upload MP3 files to Azure Blob Storage under `<root_path>/<playlist_id>/<query_type>/`
- Store the resulting blob URL in Postgres for traceability
- Show progress for each track
- Display a final summary with success/failure counts
