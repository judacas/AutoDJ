import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Shuffle, 
  Repeat,
  Volume2,
  VolumeX,
  Heart
} from 'lucide-react';

const PlayerControls = ({
  currentTrack,
  isPlaying,
  currentTime,
  duration,
  volume,
  isShuffle,
  repeatMode,
  onPlayPause,
  onPrevious,
  onNext,
  onSeek,
  onVolumeChange,
  onToggleShuffle,
  onToggleRepeat,
  onToggleLike
}) => {
  const [isLiked, setIsLiked] = useState(false);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);

  useEffect(() => {
    // Mock liked state - in real app this would come from user's liked songs
    setIsLiked(Math.random() > 0.5);
  }, [currentTrack]);

  const formatTime = (timeMs) => {
    const minutes = Math.floor(timeMs / 60000);
    const seconds = Math.floor((timeMs % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const seekTime = (clickX / width) * duration;
    onSeek(seekTime);
  };

  const handleVolumeChange = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const newVolume = Math.max(0, Math.min(1, clickX / width));
    onVolumeChange(newVolume);
  };

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;

  if (!currentTrack) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-spotify-gray border-t border-white/10 px-4 py-3 z-50">
      <div className="flex items-center justify-between max-w-screen-2xl mx-auto">
        
        {/* Currently Playing Track Info */}
        <div className="flex items-center gap-3 min-w-0 flex-1 max-w-sm">
          <div className="flex-shrink-0">
            <img 
              src={currentTrack.album?.images?.[2]?.url || currentTrack.album?.images?.[0]?.url || '/api/placeholder/56/56'}
              alt={currentTrack.album?.name || 'Album cover'}
              className="w-14 h-14 rounded object-cover"
              onError={(e) => {
                e.target.src = '/api/placeholder/56/56';
              }}
            />
          </div>
          
          <div className="min-w-0 flex-1">
            <div className="text-white text-sm font-medium truncate hover:underline cursor-pointer">
              {currentTrack.name}
            </div>
            <div className="text-spotify-light text-xs truncate hover:underline cursor-pointer">
              {currentTrack.artists?.map(artist => artist.name).join(', ') || 'Unknown Artist'}
            </div>
          </div>
          
          <button
            onClick={() => {
              setIsLiked(!isLiked);
              onToggleLike && onToggleLike(currentTrack);
            }}
            className="flex-shrink-0 p-2 hover:scale-110 transition-transform"
          >
            <Heart 
              className={`w-4 h-4 ${isLiked ? 'text-spotify-green fill-current' : 'text-spotify-light hover:text-white'}`}
            />
          </button>
        </div>

        {/* Main Player Controls */}
        <div className="flex flex-col items-center gap-2 flex-1 max-w-2xl">
          
          {/* Control Buttons */}
          <div className="flex items-center gap-4">
            <button
              onClick={onToggleShuffle}
              className={`p-2 rounded-full hover:scale-110 transition-all ${
                isShuffle ? 'text-spotify-green' : 'text-spotify-light hover:text-white'
              }`}
            >
              <Shuffle className="w-4 h-4" />
            </button>

            <button
              onClick={onPrevious}
              className="p-2 text-spotify-light hover:text-white hover:scale-110 transition-all"
            >
              <SkipBack className="w-5 h-5" />
            </button>

            <button
              onClick={onPlayPause}
              className="w-8 h-8 bg-white rounded-full flex items-center justify-center hover:scale-105 transition-all shadow-lg"
            >
              {isPlaying ? (
                <Pause className="w-4 h-4 text-black" />
              ) : (
                <Play className="w-4 h-4 text-black ml-0.5" />
              )}
            </button>

            <button
              onClick={onNext}
              className="p-2 text-spotify-light hover:text-white hover:scale-110 transition-all"
            >
              <SkipForward className="w-5 h-5" />
            </button>

            <button
              onClick={onToggleRepeat}
              className={`p-2 rounded-full hover:scale-110 transition-all ${
                repeatMode !== 'off' ? 'text-spotify-green' : 'text-spotify-light hover:text-white'
              }`}
            >
              <Repeat className="w-4 h-4" />
              {repeatMode === 'one' && (
                <span className="absolute -mt-1 -ml-1 text-xs font-bold">1</span>
              )}
            </button>
          </div>

          {/* Progress Bar */}
          <div className="flex items-center gap-2 w-full max-w-lg">
            <span className="text-xs text-spotify-light font-mono min-w-[40px]">
              {formatTime(currentTime)}
            </span>
            
            <div 
              className="flex-1 h-1 bg-gray-600 rounded-full cursor-pointer group"
              onClick={handleSeek}
            >
              <div 
                className="h-full bg-white rounded-full relative group-hover:bg-spotify-green transition-colors"
                style={{ width: `${progressPercentage}%` }}
              >
                <div className="absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity shadow-lg" />
              </div>
            </div>
            
            <span className="text-xs text-spotify-light font-mono min-w-[40px]">
              {formatTime(duration)}
            </span>
          </div>
        </div>

        {/* Volume and Additional Controls */}
        <div className="flex items-center gap-2 flex-1 justify-end max-w-sm">
          <div 
            className="relative flex items-center gap-2"
            onMouseEnter={() => setShowVolumeSlider(true)}
            onMouseLeave={() => setShowVolumeSlider(false)}
          >
            <button className="p-2 text-spotify-light hover:text-white transition-colors">
              {volume === 0 ? (
                <VolumeX className="w-4 h-4" />
              ) : (
                <Volume2 className="w-4 h-4" />
              )}
            </button>
            
            {showVolumeSlider && (
              <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-spotify-gray rounded-lg p-2 shadow-lg">
                <div 
                  className="w-20 h-1 bg-gray-600 rounded-full cursor-pointer group"
                  onClick={handleVolumeChange}
                >
                  <div 
                    className="h-full bg-white rounded-full relative group-hover:bg-spotify-green transition-colors"
                    style={{ width: `${volume * 100}%` }}
                  >
                    <div className="absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerControls;