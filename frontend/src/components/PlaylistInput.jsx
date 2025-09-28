import { Link, Search } from 'lucide-react';
import { useState } from 'react';

const PlaylistInput = ({ onPlaylistSubmit, isLoading }) => {
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [error, setError] = useState('');
  const [isFocused, setIsFocused] = useState(false);

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
    <div className="w-full max-w-4xl mx-auto px-6">
      {/* Premium Hero Section */}
      <div className="text-center mb-12 space-y-6">
        <div className="space-y-4">
          <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-b from-white to-zinc-400 bg-clip-text text-transparent leading-tight">
            AutoDJ
          </h1>
          <div className="w-24 h-1 bg-gradient-to-r from-green-500 to-emerald-400 rounded-full mx-auto" />
        </div>

        <div className="space-y-2">
          <p className="text-xl text-zinc-300 font-medium">
            Transform your Spotify playlists
          </p>
          <p className="text-zinc-500 max-w-lg mx-auto leading-relaxed">
            Paste your Spotify playlist link below to discover new music and create the perfect mix
          </p>
        </div>
      </div>

      {/* Premium Input Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="relative group">
          {/* Input Container */}
          <div className={`relative overflow-hidden rounded-2xl transition-all duration-300 ${isFocused
              ? 'ring-2 ring-green-500/30 shadow-glow'
              : 'ring-1 ring-white/10'
            }`}>

            {/* Glass Background */}
            <div className="absolute inset-0 glass-morphism" />

            {/* Input Icon */}
            <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none z-10">
              <Link className={`h-5 w-5 transition-colors duration-200 ${isFocused ? 'text-green-400' : 'text-zinc-500'
                }`} />
            </div>

            {/* Input Field */}
            <input
              type="text"
              value={playlistUrl}
              onChange={handleInputChange}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="https://open.spotify.com/playlist/..."
              className={`relative z-10 w-full pl-16 pr-20 py-6 bg-transparent text-white placeholder-zinc-500 focus:outline-none transition-all duration-200 text-lg ${error ? 'text-red-300' : ''
                }`}
              disabled={isLoading}
            />

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !playlistUrl.trim()}
              className="absolute inset-y-0 right-0 px-8 flex items-center z-10 group-disabled"
            >
              <div className={`
                flex items-center justify-center w-12 h-12 rounded-xl transition-all duration-200
                ${isLoading || !playlistUrl.trim()
                  ? 'bg-zinc-700 text-zinc-500 cursor-not-allowed'
                  : 'bg-green-500 text-black hover:bg-green-400 hover:scale-105 active:scale-95 cursor-pointer shadow-lg hover:shadow-green-500/25'
                }
              `}>
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Search className="h-5 w-5" />
                )}
              </div>
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="glass-morphism rounded-xl p-4 border border-red-500/20 animate-fadeIn">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-red-200 font-medium">{error}</span>
            </div>
          </div>
        )}
      </form>

      {/* Example Link */}
      <div className="mt-8 text-center">
        <div className="glass-morphism rounded-xl p-6 max-w-2xl mx-auto">
          <p className="text-zinc-400 text-sm mb-3 font-medium">
            Need an example? Try this playlist:
          </p>
          <button
            onClick={() => {
              const exampleUrl = "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF";
              setPlaylistUrl(exampleUrl);
              setError('');
            }}
            className="text-green-400 hover:text-green-300 font-mono text-sm bg-zinc-800/50 px-4 py-2 rounded-lg hover:bg-zinc-800/80 transition-all duration-200"
          >
            https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF
          </button>
        </div>
      </div>

      {/* Feature Highlights */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        {[
          {
            icon: "🎵",
            title: "Smart Analysis",
            description: "AI-powered playlist analysis and recommendations"
          },
          {
            icon: "⚡",
            title: "Lightning Fast",
            description: "Instant playlist processing and track discovery"
          },
          {
            icon: "🔊",
            title: "High Quality",
            description: "Premium audio streaming and seamless playback"
          }
        ].map((feature, index) => (
          <div
            key={index}
            className="glass-morphism rounded-2xl p-6 text-center space-y-3 hover:bg-white/5 transition-all duration-300 group"
          >
            <div className="text-3xl mb-2 group-hover:scale-110 transition-transform duration-200">
              {feature.icon}
            </div>
            <h3 className="text-white font-semibold text-lg">{feature.title}</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">{feature.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlaylistInput;