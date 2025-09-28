import { Calendar, Clock, Pause, Play } from 'lucide-react';
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
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="text-center space-y-6 animate-fadeIn">
          <div className="glass-morphism rounded-3xl p-12 max-w-md mx-auto">
            <div className="text-6xl mb-6 animate-pulse">🎵</div>
            <h3 className="text-2xl font-semibold text-white mb-3">No songs found</h3>
            <p className="text-gray-400 leading-relaxed">
              Try loading a playlist with some tracks to get started.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const totalDuration = Math.floor(
    songs.reduce((total, song) => total + (song.track?.duration_ms || 0), 0) / 60000
  );

  return (
    <div className="w-full max-w-7xl mx-auto px-6 pt-8 pb-8">
      {/* Premium Playlist Header */}
      {playlist && (
        <div className="mb-12">
          <div className="glass-morphism rounded-3xl p-8 md:p-12 overflow-hidden relative">
            {/* Apple-inspired Background Gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/5" />

            <div className="relative flex flex-col lg:flex-row gap-8 items-start lg:items-end">
              {/* Playlist Image */}
              <div className="flex-shrink-0 group">
                <div className="relative">
                  <img
                    src={playlist.images?.[0]?.url || '/api/placeholder/280/280'}
                    alt={playlist.name}
                    className="w-60 h-60 lg:w-72 lg:h-72 object-cover rounded-2xl shadow-strong group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      e.target.src = '/api/placeholder/280/280';
                    }}
                  />
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-t from-black/20 via-transparent to-transparent" />

                  {/* Apple-inspired Hover Glow */}
                  <div className="absolute -inset-4 bg-gradient-to-r from-blue-500/20 via-transparent to-purple-500/20 rounded-3xl opacity-0 group-hover:opacity-100 blur-xl transition-all duration-700 pointer-events-none" />
                </div>
              </div>

              {/* Playlist Info */}
              <div className="flex-1 space-y-6 min-w-0">
                <div className="space-y-3">
                  <p className="text-sm font-bold text-blue-400 uppercase tracking-wider">
                    Playlist
                  </p>
                  <h1 className="text-4xl lg:text-6xl xl:text-7xl font-black text-white leading-tight break-words">
                    {playlist.name}
                  </h1>
                </div>

                {playlist.description && (
                  <p className="text-gray-300 text-lg leading-relaxed max-w-2xl">
                    {playlist.description}
                  </p>
                )}

                <div className="flex items-center gap-2 text-gray-400 flex-wrap">
                  <span className="font-semibold text-white hover:underline cursor-pointer">
                    {playlist.owner?.display_name}
                  </span>
                  <span>•</span>
                  <span className="font-medium">{songs.length.toLocaleString()} songs</span>
                  <span>•</span>
                  <span>{totalDuration} min</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Apple-inspired Controls Section */}
      <div className="mb-8 px-2">
        <div className="flex items-center gap-6">
          {/* Main Play Button - Apple Blue */}
          <button
            onClick={() => currentTrack ? onPlayPause() : onTrackSelect(songs[0].track, 0)}
            className="group relative w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center hover:bg-blue-400 hover:scale-110 active:scale-105 transition-all duration-200 shadow-strong hover:shadow-blue"
          >
            {isPlaying && currentTrack ? (
              <Pause className="w-7 h-7 text-white ml-0" />
            ) : (
              <Play className="w-7 h-7 text-white ml-1" />
            )}

            {/* Apple-inspired Glow Effect */}
            <div className="absolute inset-0 rounded-full bg-blue-500 opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-200" />
          </button>

          {/* Additional Controls */}
          <div className="flex items-center gap-4 text-gray-400">
            <button className="hover:text-white transition-colors p-2 rounded-full hover:bg-white/5">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
              </svg>
            </button>

            <button className="hover:text-white transition-colors p-2 rounded-full hover:bg-white/5">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Premium Song List */}
      <div className="glass-morphism rounded-2xl overflow-hidden">
        {/* Table Header */}
        <div className="sticky top-0 z-20 glass-morphism-strong border-b border-white/5">
          <div className="grid grid-cols-[auto_1fr_1fr_auto_auto] gap-4 px-6 py-4 text-sm font-medium text-gray-400 uppercase tracking-wider">
            <div className="w-8 text-center">#</div>
            <div>Title</div>
            <div className="hidden md:block">Album</div>
            <div className="hidden md:flex items-center justify-center w-8">
              <Calendar className="w-4 h-4" />
            </div>
            <div className="flex items-center justify-end w-12">
              <Clock className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* Songs List */}
        <div className="divide-y divide-white/5">
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
      </div>

      {/* Footer */}
      <div className="mt-12 text-center">
        <div className="glass-morphism rounded-xl p-6 max-w-md mx-auto">
          <p className="text-gray-400 text-sm">
            <span className="font-medium">{new Date().toLocaleDateString()}</span>
            <span className="mx-2">•</span>
            <span>{songs.length.toLocaleString()} songs</span>
            <span className="mx-2">•</span>
            <span>{totalDuration} minutes</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SongList;