import React, { useState } from 'react';
import { Search, Link } from 'lucide-react';

const PlaylistInput = ({ onPlaylistSubmit, isLoading }) => {
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [error, setError] = useState('');

  const isValidPlaylistUrl = (url) => {
    // Check for Spotify playlist URLs
    const spotifyPattern = /^https:\/\/open\.spotify\.com\/playlist\/[a-zA-Z0-9]+(\?.*)?$/;
    return spotifyPattern.test(url);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!playlistUrl.trim()) {
      setError('Please enter a playlist URL');
      return;
    }

    if (!isValidPlaylistUrl(playlistUrl)) {
      setError('Please enter a valid Spotify playlist URL');
      return;
    }

    onPlaylistSubmit(playlistUrl);
  };

  const handleInputChange = (e) => {
    setPlaylistUrl(e.target.value);
    if (error) setError(''); // Clear error when user starts typing
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
          AutoDJ
        </h1>
        <p className="text-spotify-light text-lg">
          Paste your Spotify playlist link to get started
        </p>
      </div>

      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Link className="h-5 w-5 text-spotify-light" />
          </div>
          
          <input
            type="text"
            value={playlistUrl}
            onChange={handleInputChange}
            placeholder="https://open.spotify.com/playlist/..."
            className={`w-full pl-12 pr-20 py-4 bg-spotify-gray border rounded-lg text-white placeholder-spotify-light focus:outline-none focus:ring-2 focus:ring-spotify-green focus:border-spotify-green transition-all duration-200 ${
              error ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-600'
            }`}
            disabled={isLoading}
          />
          
          <button
            type="submit"
            disabled={isLoading || !playlistUrl.trim()}
            className="absolute inset-y-0 right-0 px-6 flex items-center bg-spotify-green text-black font-semibold rounded-r-lg hover:bg-green-400 focus:outline-none focus:ring-2 focus:ring-spotify-green focus:ring-offset-2 focus:ring-offset-spotify-gray disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-black border-t-transparent" />
            ) : (
              <Search className="h-5 w-5" />
            )}
          </button>
        </div>

        {error && (
          <div className="mt-2 text-red-400 text-sm flex items-center">
            <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}
      </form>

      <div className="mt-6 text-center">
        <p className="text-spotify-light text-sm">
          Example: https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF
        </p>
      </div>
    </div>
  );
};

export default PlaylistInput;