# Spotify Integration Setup Guide

This guide will help you set up Spotify authentication and start extracting playlist data for AutoDJ.

## Prerequisites

1. **Spotify Developer Account**: You need a Spotify Developer account to get API credentials
2. **Python Environment**: Make sure you have Python 3.7+ installed

## Step 1: Create Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the app details:
   - **App name**: `AutoDJ` (or any name you prefer)
   - **App description**: `Music mixing application`
   - **Website**: `http://localhost:8888` (or your domain)
   - **Redirect URI**: `http://127.0.0.1:8000/callback`
5. Click "Save"
6. Note down your **Client ID** and **Client Secret**

## Step 2: Set Up Environment Variables

Create a `.env` file in the project root with your Spotify credentials:

```env
# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback
SPOTIFY_CACHE_PATH=.spotify_cache
```

**Important**: Replace `your_client_id_here` and `your_client_secret_here` with your actual credentials from Step 1.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```