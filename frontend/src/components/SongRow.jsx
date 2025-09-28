import { Heart, Pause, Play } from 'lucide-react';
import { useState } from 'react';

const SongRow = ({
  song,
  index,
  isCurrentTrack,
  isPlaying,
  onTrackSelect,
  onPlayPause
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isLiked, setIsLiked] = useState(false);

  const formatDuration = (durationMs) => {
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleRowClick = () => {
    if (isCurrentTrack) {
      onPlayPause();
    } else {
      onTrackSelect(song, index);
    }
  };

  const handlePlayButtonClick = (e) => {
    e.stopPropagation();
    if (isCurrentTrack) {
      onPlayPause();
    } else {
      onTrackSelect(song, index);
    }
  };

  const handleLikeClick = (e) => {
    e.stopPropagation();
    setIsLiked(!isLiked);
  };

  return (
    <div
      className={`group grid grid-cols-[auto_1fr_1fr_auto_auto] gap-4 px-6 py-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-white/5 ${isCurrentTrack ? 'bg-white/5' : ''
        }`}
      onClick={handleRowClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Track Number / Play Button */}
      <div className="flex items-center justify-center w-8 text-gray-400 group-hover:text-white">
        {isCurrentTrack && isPlaying ? (
          <button
            onClick={handlePlayButtonClick}
            className="w-4 h-4 flex items-center justify-center hover:scale-110 transition-transform"
          >
            <Pause className="w-4 h-4 text-blue-500" />
          </button>
        ) : isHovered || isCurrentTrack ? (
          <button
            onClick={handlePlayButtonClick}
            className="w-4 h-4 flex items-center justify-center hover:scale-110 transition-transform"
          >
            <Play className="w-4 h-4 text-white" />
          </button>
        ) : (
          <span className={`text-sm font-medium ${isCurrentTrack ? 'text-blue-500' : 'text-gray-400'}`}>
            {(index + 1).toString().padStart(2, '0')}
          </span>
        )}
      </div>

      {/* Album Cover, Title & Artist */}
      <div className="flex items-center gap-4 min-w-0">
        <div className="relative flex-shrink-0 group/image">
          <img
            src={song.album?.images?.[2]?.url || song.album?.images?.[0]?.url || '/api/placeholder/48/48'}
            alt={song.album?.name || 'Album cover'}
            className="w-12 h-12 rounded-lg object-cover shadow-md group-hover/image:shadow-lg transition-shadow duration-200"
            onError={(e) => {
              e.target.src = '/api/placeholder/48/48';
            }}
          />
          {isCurrentTrack && (
            <div className="absolute inset-0 bg-black/30 rounded-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
            </div>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className={`font-semibold truncate text-base transition-colors ${isCurrentTrack ? 'text-blue-400' : 'text-white group-hover:text-blue-400'
            }`}>
            {song.name}
          </div>
          <div className="text-sm text-gray-400 truncate hover:text-gray-300 transition-colors cursor-pointer">
            {song.artists?.map(artist => artist.name).join(', ') || 'Unknown Artist'}
          </div>
        </div>
      </div>

      {/* Album Name */}
      <div className="hidden md:flex items-center min-w-0">
        <span className="text-sm text-gray-400 truncate hover:text-white hover:underline cursor-pointer transition-colors">
          {song.album?.name || 'Unknown Album'}
        </span>
      </div>

      {/* Date Added */}
      <div className="hidden md:flex items-center justify-center w-8">
        <button
          onClick={handleLikeClick}
          className={`p-1 rounded-full transition-all duration-200 hover:scale-110 ${isLiked
            ? 'text-pink-500 hover:text-pink-400'
            : 'text-gray-500 hover:text-gray-300 opacity-0 group-hover:opacity-100'
            }`}
        >
          <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
        </button>
      </div>

      {/* Duration */}
      <div className="flex items-center justify-end w-12">
        <span className="text-sm text-gray-400 font-medium">
          {formatDuration(song.duration_ms || 0)}
        </span>
      </div>
    </div>
  );
};

export default SongRow;