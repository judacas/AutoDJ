# AutoDJ Frontend-Backend Integration Guide

This guide explains how to run both the AutoDJ backend and React frontend together.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ and npm installed
- **A Spotify Developer Account** (for API credentials)

### 1. Spotify API Setup (REQUIRED)

Before running the backend, you need Spotify API credentials:

1. **Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)**
2. **Log in with your Spotify account**
3. **Click "Create App"**
4. **Fill in the app details:**
   - App name: `AutoDJ`
   - App description: `Music mixing application`
   - Website: `http://localhost:3000`
   - Redirect URI: `http://127.0.0.1:8000/callback`
5. **Click "Save"**
6. **Copy your Client ID and Client Secret**

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use any text editor
```

Update your `.env` file with your Spotify credentials:
```env
SPOTIFY_CLIENT_ID=your_actual_client_id_here
SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback
SPOTIFY_CACHE_PATH=.spotify_cache
```

### 3. Backend Setup

```bash
# Navigate to the project root
cd /path/to/AutoDJ

# Create and activate a virtual environment (if not done already)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn MonolithDev.gettingSongs.api:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at: **http://127.0.0.1:8000**
- API documentation: **http://127.0.0.1:8000/docs**

### 4. Frontend Setup

In a new terminal window, set up and start the React frontend:

```bash
# Navigate to the frontend directory
cd /path/to/AutoDJ/frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will be available at: **http://localhost:3000**

## 🔧 Troubleshooting Common Issues

### Backend Issues

1. **"ValueError: Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET"**
   - Make sure you created the `.env` file in the project root
   - Verify your Spotify credentials are correct
   - Ensure the `.env` file is not in `.gitignore`

2. **"ModuleNotFoundError: No module named 'gettingSongs'"**
   - This has been fixed in the updated code
   - Make sure you're running from the project root directory

3. **"Port already in use" error:**
   ```bash
   # Change the port
   python -m uvicorn MonolithDev.gettingSongs.api:app --host 127.0.0.1 --port 8001 --reload
   # Then update API_BASE_URL in frontend/src/services/api.js
   ```

### Frontend Issues

1. **"Cannot connect to backend server"**
   - Make sure the backend is running on port 8000
   - Check that the backend shows no errors in the terminal
   - Verify the API_BASE_URL in `frontend/src/services/api.js` matches your backend URL

2. **"npm install" fails:**
   ```bash
   # Clear npm cache and try again
   npm cache clean --force
   npm install
   ```

## 📋 API Endpoints

The backend exposes these main endpoints:

### GET `/playlist/tracks`
- **Purpose**: Fetch track information from a Spotify playlist
- **Parameters**: `playlist_url` (query parameter)
- **Response**: Playlist metadata and list of tracks
- **Example**: `http://127.0.0.1:8000/playlist/tracks?playlist_url=https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF`

### POST `/playlist/convert`
- **Purpose**: Convert and download playlist tracks
- **Body**: JSON with `playlist_url`, `mixes_per_track`, `download_songs`, `download_mixes`
- **Response**: Conversion results and download summaries

## 🎯 How to Use

1. **Complete the Spotify setup** (Steps 1-2 above)

2. **Start the backend server** (Step 3)
   - Should show: `Uvicorn running on http://127.0.0.1:8000`
   - No error messages about Spotify credentials

3. **Start the frontend** (Step 4)
   - Should open automatically at http://localhost:3000

4. **Test with a Spotify playlist:**
   ```
   https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF
   ```

5. **Click the search button** to fetch the playlist

6. **View and interact** with the tracks in the Spotify-style interface

## 🚨 Important Notes

- **Spotify Rate Limits**: The Spotify API has rate limits. If you get too many requests errors, wait a few minutes.
- **Public Playlists Only**: Make sure the playlist you're testing with is public.
- **Internet Connection**: Both the backend and frontend require internet access to fetch data.

## 🔍 Error Messages Guide

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Cannot connect to backend server" | Backend not running | Start backend server |
| "Playlist not found" | Invalid/private playlist | Use a public Spotify playlist URL |
| "Invalid playlist URL" | Wrong URL format | Use format: `https://open.spotify.com/playlist/ID` |
| "Spotify credentials error" | Missing/wrong API keys | Check your `.env` file |

## ✅ Success Indicators

**Backend is working when you see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
```

**Frontend is working when you see:**
```
webpack compiled successfully
Local:            http://localhost:3000
```

**Integration is working when:**
- You can paste a Spotify playlist URL
- Click search and see a loading spinner
- Tracks load and display in the interface
- No error messages appear

## 🔜 Next Steps

Once everything is working:
- Try different public Spotify playlists
- Use the player controls to navigate tracks
- Explore the `/playlist/convert` endpoint for downloading functionality
- Consider implementing user authentication for private playlists