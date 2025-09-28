import React, { useState, useEffect, useCallback } from 'react';
import PlaylistInput from './components/PlaylistInput';
import SongList from './components/SongList';
import PlayerControls from './components/PlayerControls';

// Mock API function - replace with actual backend integration
const mockFetchPlaylist = async (playlistUrl) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Mock playlist data
  return {
    playlist: {
      id: '37i9dQZEVXbMDoHDwVN2tF',
      name: 'Global Top 50',
      description: 'Your daily update of the most played tracks right now - Global.',
      images: [
        { url: 'https://i.scdn.co/image/ab67706f000000023dadf31c2e4bca63f5b9ba8a' }
      ],
      owner: {
        display_name: 'Spotify'
      }
    },
    tracks: {
      items: [
        {
          track: {
            id: '1',
            name: 'Anti-Hero',
            artists: [{ name: 'Taylor Swift' }],
            album: {
              name: 'Midnights',
              images: [
                { url: 'https://i.scdn.co/image/ab67616d0000b273bb54dde68cd23e2a268ae0f5' }
              ]
            },
            duration_ms: 200000,
            preview_url: null
          }
        },
        {
          track: {
            id: '2',
            name: 'As It Was',
            artists: [{ name: 'Harry Styles' }],
            album: {
              name: 'Harry\'s House',
              images: [
                { url: 'https://i.scdn.co/image/ab67616d0000b273b46f74097655d7f353caab14' }
              ]
            },
            duration_ms: 167000,
            preview_url: null
          }
        },
        {
          track: {
            id: '3',
            name: 'Bad Habit',
            artists: [{ name: 'Steve Lacy' }],
            album: {
              name: 'Gemini Rights',
              images: [
                { url: 'https://i.scdn.co/image/ab67616d0000b273b85259a5d7dcdb64c2f98e09' }
              ]
            },
            duration_ms: 223000,
            preview_url: null
          }
        },
        {
          track: {
            id: '4',
            name: 'Unholy',
            artists: [{ name: 'Sam Smith' }, { name: 'Kim Petras' }],
            album: {
              name: 'Unholy',
              images: [
                { url: 'https://i.scdn.co/image/ab67616d0000b2732b2b82f7b6a3b5b2f4b4b6a3' }
              ]
            },
            duration_ms: 156000,
            preview_url: null
          }
        },
        {
          track: {
            id: '5',
            name: 'Flowers',
            artists: [{ name: 'Miley Cyrus' }],
            album: {
              name: 'Endless Summer Vacation',
              images: [
                { url: 'https://i.scdn.co/image/ab67616d0000b273f4b5e7e5e1c2f2e5e1e5e1e5' }
              ]
            },
            duration_ms: 200000,
            preview_url: null
          }
        }
      ]
    }
  };
};

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
      const data = await mockFetchPlaylist(playlistUrl);
      setPlaylist(data.playlist);
      setSongs(data.tracks.items);
      
      // Reset player state
      setCurrentTrack(null);
      setCurrentTrackIndex(0);
      setIsPlaying(false);
      setCurrentTime(0);
    } catch (err) {
      setError('Failed to load playlist. Please try again.');
      console.error('Error fetching playlist:', err);
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
    // In a real app, you would seek the audio player here
  }, []);

  // Handle volume change
  const handleVolumeChange = useCallback((newVolume) => {
    setVolume(newVolume);
    // In a real app, you would update the audio player volume here
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
    <div className="min-h-screen bg-spotify-dark text-white">
      <div className="pb-24"> {/* Add padding bottom for player controls */}
        
        {/* Show playlist input if no playlist loaded */}
        {!playlist && (
          <div className="min-h-screen flex items-center justify-center">
            <PlaylistInput 
              onPlaylistSubmit={handlePlaylistSubmit}
              isLoading={isLoading}
            />
          </div>
        )}

        {/* Show error if any */}
        {error && (
          <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50">
            {error}
          </div>
        )}

        {/* Show loading state */}
        {isLoading && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-spotify-gray p-6 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-spotify-green border-t-transparent" />
                <span>Loading playlist...</span>
              </div>
            </div>
          </div>
        )}

        {/* Show playlist and songs */}
        {playlist && songs.length > 0 && (
          <>
            {/* Add a button to load a new playlist */}
            <div className="fixed top-4 right-4 z-40">
              <button
                onClick={() => {
                  setPlaylist(null);
                  setSongs([]);
                  setCurrentTrack(null);
                  setIsPlaying(false);
                }}
                className="bg-spotify-gray hover:bg-white/20 text-white px-4 py-2 rounded-full text-sm font-medium transition-colors"
              >
                Load New Playlist
              </button>
            </div>

            <SongList
              playlist={playlist}
              songs={songs}
              currentTrack={currentTrack}
              isPlaying={isPlaying}
              onTrackSelect={handleTrackSelect}
              onPlayPause={handlePlayPause}
            />
          </>
        )}
      </div>

      {/* Player Controls (always at bottom) */}
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
  );
}

export default App;