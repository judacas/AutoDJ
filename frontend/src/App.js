import { useCallback, useEffect, useState } from 'react';
import PlayerControls from './components/PlayerControls';
import PlaylistInput from './components/PlaylistInput';
import SongList from './components/SongList';
import { APIError, APIService } from './services/api';

function App() {
  // Playlist and songs state
  const [playlist, setPlaylist] = useState(null);
  const [songs, setSongs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Player state
  const [currentTrack, setCurrentTrack] = useState(null);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isShuffle, setIsShuffle] = useState(false);
  const [repeatMode, setRepeatMode] = useState('off'); // 'off', 'all', 'one'

  // Handle playlist submission
  const handlePlaylistSubmit = async (playlistUrl) => {
    setIsLoading(true);
    setError('');

    try {
      // First check if backend is reachable
      const isHealthy = await APIService.checkHealth();
      if (!isHealthy) {
        throw new APIError('Backend server is not running. Please start the server first.', 0);
      }

      // Fetch playlist data from the real backend
      const data = await APIService.fetchPlaylistTracks(playlistUrl);
      setPlaylist(data.playlist);
      setSongs(data.tracks.items);

      // Reset player state
      setCurrentTrack(null);
      setCurrentTrackIndex(0);
      setIsPlaying(false);
      setCurrentTime(0);
    } catch (err) {
      console.error('Error fetching playlist:', err);

      if (err instanceof APIError) {
        if (err.status === 0) {
          setError('Cannot connect to backend server. Please make sure it is running on http://127.0.0.1:8001');
        } else if (err.status === 404) {
          setError('Playlist not found. Please check the URL and try again.');
        } else if (err.status === 400) {
          setError('Invalid playlist URL. Please enter a valid Spotify playlist link.');
        } else {
          setError(err.message);
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle track selection
  const handleTrackSelect = useCallback((track, index) => {
    setCurrentTrack(track);
    setCurrentTrackIndex(index);
    setCurrentTime(0);
    setDuration(track.duration_ms || 0);
    setIsPlaying(true);
  }, []);

  // Handle play/pause
  const handlePlayPause = useCallback(() => {
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  // Handle previous track
  const handlePrevious = useCallback(() => {
    if (songs.length === 0) return;

    let newIndex;
    if (isShuffle) {
      newIndex = Math.floor(Math.random() * songs.length);
    } else {
      newIndex = currentTrackIndex > 0 ? currentTrackIndex - 1 : songs.length - 1;
    }

    const newTrack = songs[newIndex]?.track || songs[newIndex];
    handleTrackSelect(newTrack, newIndex);
  }, [songs, currentTrackIndex, isShuffle, handleTrackSelect]);

  // Handle next track
  const handleNext = useCallback(() => {
    if (songs.length === 0) return;

    let newIndex;
    if (isShuffle) {
      newIndex = Math.floor(Math.random() * songs.length);
    } else {
      newIndex = currentTrackIndex < songs.length - 1 ? currentTrackIndex + 1 : 0;
    }

    const newTrack = songs[newIndex]?.track || songs[newIndex];
    handleTrackSelect(newTrack, newIndex);
  }, [songs, currentTrackIndex, isShuffle, handleTrackSelect]);

  // Handle seek
  const handleSeek = useCallback((time) => {
    setCurrentTime(time);
  }, []);

  // Handle volume change
  const handleVolumeChange = useCallback((newVolume) => {
    setVolume(newVolume);
  }, []);

  // Handle shuffle toggle
  const handleToggleShuffle = useCallback(() => {
    setIsShuffle(!isShuffle);
  }, [isShuffle]);

  // Handle repeat toggle
  const handleToggleRepeat = useCallback(() => {
    const modes = ['off', 'all', 'one'];
    const currentIndex = modes.indexOf(repeatMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    setRepeatMode(modes[nextIndex]);
  }, [repeatMode]);

  // Mock time progress (in real app this would be handled by audio player)
  useEffect(() => {
    let interval;

    if (isPlaying && currentTrack && duration > 0) {
      interval = setInterval(() => {
        setCurrentTime(prev => {
          const newTime = prev + 1000;

          // Auto advance to next track when current track ends
          if (newTime >= duration) {
            if (repeatMode === 'one') {
              return 0; // Restart current track
            } else {
              handleNext();
              return 0;
            }
          }

          return newTime;
        });
      }, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isPlaying, currentTrack, duration, repeatMode, handleNext]);

  return (
    <div className="min-h-screen text-white relative overflow-hidden">
      {/* Apple-inspired Premium Background Layer */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-br from-gray-900 via-black to-gray-900" />

      {/* Main Content Container */}
      <div className="relative z-10">
        <main className="pb-32">
          {/* Show playlist input if no playlist loaded */}
          {!playlist && (
            <div className="min-h-screen flex items-center justify-center px-6">
              <div className="w-full max-w-2xl animate-entrance">
                <PlaylistInput
                  onPlaylistSubmit={handlePlaylistSubmit}
                  isLoading={isLoading}
                />
              </div>
            </div>
          )}

          {/* Show error if any */}
          {error && (
            <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50 animate-entrance">
              <div className="glass-morphism-strong px-6 py-4 rounded-2xl shadow-strong border border-red-500/20 max-w-md">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-red-200 font-medium">{error}</span>
                </div>
              </div>
            </div>
          )}

          {/* Show loading state */}
          {isLoading && (
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
              <div className="glass-morphism-strong p-8 rounded-3xl shadow-strong animate-scaleIn">
                <div className="flex flex-col items-center gap-6">
                  <div className="relative">
                    <div className="w-16 h-16 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin" />
                    <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-blue-500/30 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '2s' }} />
                  </div>
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-white mb-2">Loading playlist...</h3>
                    <p className="text-gray-400">Fetching your music</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Show playlist and songs */}
          {playlist && songs.length > 0 && (
            <div className="animate-entrance">
              {/* Premium Load New Playlist Button */}
              <div className="fixed top-6 right-6 z-40 animate-entrance-delay-1">
                <button
                  onClick={() => {
                    setPlaylist(null);
                    setSongs([]);
                    setCurrentTrack(null);
                    setIsPlaying(false);
                  }}
                  className="glass-morphism px-6 py-3 rounded-2xl text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 transition-all duration-300 hover:shadow-glow hover:scale-105 group"
                >
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 transition-transform group-hover:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Load New Playlist
                  </div>
                </button>
              </div>

              <div className="animate-entrance-delay-2">
                <SongList
                  playlist={playlist}
                  songs={songs}
                  currentTrack={currentTrack}
                  isPlaying={isPlaying}
                  onTrackSelect={handleTrackSelect}
                  onPlayPause={handlePlayPause}
                />
              </div>
            </div>
          )}
        </main>

        {/* Premium Player Controls - Always at bottom */}
        <div className="animate-entrance-delay-3">
          <PlayerControls
            currentTrack={currentTrack}
            isPlaying={isPlaying}
            currentTime={currentTime}
            duration={duration}
            volume={volume}
            isShuffle={isShuffle}
            repeatMode={repeatMode}
            onPlayPause={handlePlayPause}
            onPrevious={handlePrevious}
            onNext={handleNext}
            onSeek={handleSeek}
            onVolumeChange={handleVolumeChange}
            onToggleShuffle={handleToggleShuffle}
            onToggleRepeat={handleToggleRepeat}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
