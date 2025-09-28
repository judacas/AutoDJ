import { useState } from 'react';


const PlaylistInput = ({ onPlaylistSubmit, loading }) => {
  const [playlistUrl, setPlaylistUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (playlistUrl.trim()) {
      onPlaylistSubmit(playlistUrl.trim());
    }
  };

  return (
    <div className="text-center space-y-8 animate-entrance">
      {/* Hero Section */}
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-none">
            <span className="bg-gradient-to-b from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
              Auto
            </span>
            <span className="bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 bg-clip-text text-transparent">
              DJ
            </span>
          </h1>
        </div>
      </div>

      {/* Input Section */}
      <div className="max-w-2xl mx-auto space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative group">
            <input
              type="text"
              value={playlistUrl}
              onChange={(e) => setPlaylistUrl(e.target.value)}
              placeholder="Enter Spotify playlist URL..."
              className="input-premium text-lg py-5"
              disabled={loading}
            />

            {/* Input Enhancement Ring */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/20 via-transparent to-purple-500/20 opacity-0 group-hover:opacity-100 transition-all duration-700 pointer-events-none blur-sm"></div>
          </div>

          <div className="flex justify-center">
            <button
              type="submit"
              disabled={loading || !playlistUrl.trim()}
              className="btn-primary text-lg py-4 px-8 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-3">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Processing...</span>
                </div>
              ) : (
                <span className="flex items-center space-x-2">
                  <span>Generate Playlist</span>
                  <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              )}
            </button>
          </div>
        </form>

        {/* Help Text */}
        <div className="text-center space-y-3">
          <p className="text-base text-gray-400 leading-relaxed">
            Paste a Spotify playlist link and let our AutoDJ create something extraordinary
          </p>
        </div>
      </div>

      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-32 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 -right-32 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl"></div>
      </div>
    </div>
  );
};

export default PlaylistInput;