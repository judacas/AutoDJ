import React from 'react';
import { Play, Pause } from 'lucide-react';

const SongRow = ({ 
  song, 
  index, 
  isCurrentTrack, 
  isPlaying, 
  onTrackSelect,
  onPlayPause 
}) => {
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

  return (
    <div 
      className={`group grid grid-cols-[16px_1fr_1fr_1fr_minmax(120px,1fr)] gap-4 px-4 py-2 rounded-md hover:bg-white/10 cursor-pointer transition-all duration-200 ${
        isCurrentTrack ? 'bg-white/10' : ''
      }`}
      onClick={handleRowClick}
    >
      {/* Track number / Play button */}
      <div className="flex items-center justify-center text-spotify-light group-hover:text-white">
        {isCurrentTrack && isPlaying ? (
          <button 
            onClick={handlePlayButtonClick}
            className="w-4 h-4 flex items-center justify-center hover:scale-110 transition-transform"
          >
            <Pause className="w-4 h-4 text-spotify-green" />
          </button>
        ) : (
          <>
            <span className={`text-sm group-hover:hidden ${isCurrentTrack ? 'text-spotify-green' : ''}`}>
              {(index + 1).toString().padStart(2, '0')}
            </span>
            <button 
              onClick={handlePlayButtonClick}
              className="hidden group-hover:flex w-4 h-4 items-center justify-center hover:scale-110 transition-transform"
            >
              <Play className="w-4 h-4" />
            </button>
          </>
        )}
      </div>

      {/* Album cover, title & artist */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="relative flex-shrink-0">
          <img 
            src={song.album?.images?.[2]?.url || song.album?.images?.[0]?.url || '/api/placeholder/40/40'} 
            alt={song.album?.name || 'Album cover'}
            className="w-10 h-10 rounded object-cover"
            onError={(e) => {
              e.target.src = '/api/placeholder/40/40';
            }}
          />
          {isCurrentTrack && (
            <div className="absolute inset-0 bg-black/50 rounded flex items-center justify-center">
              <div className="w-3 h-3 bg-spotify-green rounded-full animate-pulse" />
            </div>
          )}
        </div>
        
        <div className="min-w-0 flex-1">
          <div className={`font-medium truncate ${isCurrentTrack ? 'text-spotify-green' : 'text-white'}`}>
            {song.name}
          </div>
          <div className="text-sm text-spotify-light truncate">
            {song.artists?.map(artist => artist.name).join(', ') || 'Unknown Artist'}
          </div>
        </div>
      </div>

      {/* Album name */}
      <div className="flex items-center min-w-0">
        <span className="text-sm text-spotify-light truncate hover:text-white cursor-pointer">
          {song.album?.name || 'Unknown Album'}
        </span>
      </div>

      {/* Date added (mock for now) */}
      <div className="hidden md:flex items-center">
        <span className="text-sm text-spotify-light">
          {song.added_at ? new Date(song.added_at).toLocaleDateString() : '2 days ago'}
        </span>
      </div>

      {/* Duration */}
      <div className="flex items-center justify-end">
        <span className="text-sm text-spotify-light">
          {formatDuration(song.duration_ms || 0)}
        </span>
      </div>
    </div>
  );
};

export default SongRow;