import { Heart, Pause, Play, Repeat, Shuffle, SkipBack, SkipForward, Volume2, VolumeX } from 'lucide-react';
import { useEffect, useState } from 'react';

const PlayerControls = ({ currentTrack, isPlaying, currentTime, duration, volume, isShuffle, repeatMode, onPlayPause, onPrevious, onNext, onSeek, onVolumeChange, onToggleShuffle, onToggleRepeat, onToggleLike }) => {
  const [isLiked, setIsLiked] = useState(false);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);

  useEffect(() => {
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

  if (!currentTrack) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50">
      <div className="glass-morphism-strong border-t border-white/10 backdrop-blur-xl">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between max-w-screen-2xl mx-auto gap-6">
            {/* Track Info Section */}
            <div className="flex items-center gap-4 min-w-0 flex-1 max-w-sm">
              <img
                src={currentTrack.album?.images?.[2]?.url || '/api/placeholder/64/64'}
                alt="Album cover"
                className="w-16 h-16 rounded-xl object-cover shadow-md"
                onError={(e) => { e.target.src = '/api/placeholder/64/64'; }}
              />
              <div className="min-w-0 flex-1">
                <div className="text-white text-base font-semibold truncate">{currentTrack.name}</div>
                <div className="text-gray-400 text-sm truncate">{currentTrack.artists?.map(a => a.name).join(', ')}</div>
              </div>
              <button
                onClick={() => setIsLiked(!isLiked)}
                className="p-2 rounded-full hover:bg-white/5 transition-all duration-200 hover:scale-110"
              >
                <Heart className={`w-5 h-5 transition-colors ${isLiked ? 'text-pink-500 fill-current' : 'text-gray-400 hover:text-pink-400'}`} />
              </button>
            </div>

            {/* Player Controls Section */}
            <div className="flex flex-col items-center gap-3 flex-1 max-w-2xl">
              <div className="flex items-center gap-4">
                <button
                  onClick={onToggleShuffle}
                  className="p-2 rounded-full hover:bg-white/5 transition-all duration-200 hover:scale-110"
                >
                  <Shuffle className={`w-4 h-4 transition-colors ${isShuffle ? 'text-blue-500' : 'text-gray-400 hover:text-blue-400'}`} />
                </button>

                <button
                  onClick={onPrevious}
                  className="p-2 rounded-full hover:bg-white/5 transition-all duration-200 hover:scale-110"
                >
                  <SkipBack className="w-5 h-5 text-gray-400 hover:text-white transition-colors" />
                </button>

                <button
                  onClick={onPlayPause}
                  className="w-12 h-12 bg-blue-500 hover:bg-blue-400 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110 shadow-blue"
                >
                  {isPlaying ?
                    <Pause className="w-5 h-5 text-white" /> :
                    <Play className="w-5 h-5 text-white ml-0.5" />
                  }
                </button>

                <button
                  onClick={onNext}
                  className="p-2 rounded-full hover:bg-white/5 transition-all duration-200 hover:scale-110"
                >
                  <SkipForward className="w-5 h-5 text-gray-400 hover:text-white transition-colors" />
                </button>

                <button
                  onClick={onToggleRepeat}
                  className="p-2 rounded-full hover:bg-white/5 transition-all duration-200 hover:scale-110"
                >
                  <Repeat className={`w-4 h-4 transition-colors ${repeatMode !== 'off' ? 'text-blue-500' : 'text-gray-400 hover:text-blue-400'}`} />
                </button>
              </div>

              {/* Progress Bar */}
              <div className="flex items-center gap-3 w-full">
                <span className="text-xs text-gray-400 font-medium tabular-nums">
                  {formatTime(currentTime)}
                </span>

                <div className="flex-1 h-1.5 bg-gray-600 rounded-full cursor-pointer group" onClick={handleSeek}>
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all duration-150 group-hover:bg-blue-400"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>

                <span className="text-xs text-gray-400 font-medium tabular-nums">
                  {formatTime(duration)}
                </span>
              </div>
            </div>

            {/* Volume Control Section */}
            <div className="flex justify-end max-w-32">
              <button
                className="p-2 text-gray-400 hover:text-white transition-all duration-200 hover:scale-110 rounded-full hover:bg-white/5"
              >
                {volume === 0 ?
                  <VolumeX className="w-5 h-5" /> :
                  <Volume2 className="w-5 h-5" />
                }
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerControls;
