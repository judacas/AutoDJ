import React from 'react';
import { Clock, Calendar } from 'lucide-react';
import SongRow from './SongRow';

const SongList = ({ 
  playlist,
  songs, 
  currentTrack, 
  isPlaying, 
  onTrackSelect,
  onPlayPause 
}) => {
  if (!songs || songs.length === 0) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="text-6xl mb-4">🎵</div>
          <h3 className="text-xl text-spotify-light mb-2">No songs found</h3>
          <p className="text-spotify-light">Try loading a playlist with some tracks.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-6">
      {/* Playlist Header */}
      {playlist && (
        <div className="flex flex-col md:flex-row gap-6 mb-8 p-6 bg-gradient-to-b from-spotify-gray/50 to-transparent rounded-lg">
          <div className="flex-shrink-0">
            <img 
              src={playlist.images?.[0]?.url || '/api/placeholder/200/200'}
              alt={playlist.name}
              className="w-48 h-48 object-cover rounded-lg shadow-lg"
              onError={(e) => {
                e.target.src = '/api/placeholder/200/200';
              }}
            />
          </div>
          
          <div className="flex flex-col justify-end">
            <p className="text-sm font-semibold text-spotify-light uppercase tracking-wider mb-2">
              Playlist
            </p>
            <h1 className="text-3xl md:text-5xl font-bold text-white mb-4 leading-tight">
              {playlist.name}
            </h1>
            {playlist.description && (
              <p className="text-spotify-light mb-4 max-w-2xl">
                {playlist.description}
              </p>
            )}
            <div className="flex items-center text-sm text-spotify-light">
              <span className="font-semibold text-white">{playlist.owner?.display_name}</span>
              <span className="mx-1">•</span>
              <span>{songs.length} songs</span>
              <span className="mx-1">•</span>
              <span>
                {Math.floor(songs.reduce((total, song) => total + (song.track?.duration_ms || 0), 0) / 60000)} min
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center gap-4 mb-6 px-4">
        <button 
          onClick={() => currentTrack ? onPlayPause() : onTrackSelect(songs[0].track, 0)}
          className="w-14 h-14 bg-spotify-green rounded-full flex items-center justify-center hover:bg-green-400 hover:scale-105 transition-all duration-200 shadow-lg"
        >
          {isPlaying ? (
            <svg className="w-6 h-6 text-black" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
            </svg>
          ) : (
            <svg className="w-6 h-6 text-black ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          )}
        </button>
      </div>

      {/* Song List Header */}
      <div className="sticky top-0 z-10 bg-spotify-dark/95 backdrop-blur-sm border-b border-white/10 mb-2">
        <div className="grid grid-cols-[16px_1fr_1fr_1fr_minmax(120px,1fr)] gap-4 px-4 py-3 text-sm font-medium text-spotify-light uppercase tracking-wider">
          <div className="flex items-center justify-center">#</div>
          <div>Title</div>
          <div>Album</div>
          <div className="hidden md:block">
            <Calendar className="w-4 h-4" />
          </div>
          <div className="flex items-center justify-end">
            <Clock className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Songs List */}
      <div className="space-y-1">
        {songs.map((item, index) => {
          const song = item.track || item;
          const isCurrentTrack = currentTrack?.id === song?.id;
          
          return (
            <SongRow
              key={`${song?.id || index}-${index}`}
              song={song}
              index={index}
              isCurrentTrack={isCurrentTrack}
              isPlaying={isCurrentTrack && isPlaying}
              onTrackSelect={onTrackSelect}
              onPlayPause={onPlayPause}
            />
          );
        })}
      </div>

      {/* Footer info */}
      <div className="mt-8 pt-6 border-t border-white/10">
        <p className="text-spotify-light text-sm text-center">
          {new Date().toLocaleDateString()} • {songs.length} songs
        </p>
      </div>
    </div>
  );
};

export default SongList;