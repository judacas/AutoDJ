// API service for communicating with the AutoDJ backend
const API_BASE_URL = 'http://127.0.0.1:8001';

class APIError extends Error {
    constructor(message, status) {
        super(message);
        this.name = 'APIError';
        this.status = status;
    }
}

export class APIService {
    /**
     * Fetch playlist tracks from the backend
     * @param {string} playlistUrl - Spotify playlist URL
     * @returns {Promise<{playlist_id: string, total_tracks: number, tracks: Array}>}
     */
    static async fetchPlaylistTracks(playlistUrl) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/playlist/tracks?playlist_url=${encodeURIComponent(playlistUrl)}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(
                    errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
                    response.status
                );
            }

            const data = await response.json();

            // Transform the backend data to match the frontend expectations
            return {
                playlist: {
                    id: data.playlist_id,
                    name: data.playlist_name,
                    description: data.playlist_description,
                    images: data.playlist_images || [{ url: '/api/placeholder/200/200' }],
                    owner: { display_name: data.playlist_owner?.display_name || 'Unknown' }
                },
                tracks: {
                    items: data.tracks.map((track, index) => ({
                        track: {
                            id: track.spotify_id || `track-${index}`,
                            name: track.name,
                            artists: track.artists.map(artistName => ({ name: artistName })),
                            album: {
                                name: track.album,
                                images: track.album_images || [{ url: '/api/placeholder/64/64' }]
                            },
                            duration_ms: track.duration_ms,
                            preview_url: track.preview_url,
                            external_urls: { spotify: track.spotify_url },
                            uri: track.spotify_uri,
                            explicit: track.explicit
                        },
                        added_at: track.added_at
                    }))
                }
            };
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }

            // Handle network errors
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new APIError(
                    'Unable to connect to the backend server. Please make sure it\'s running.',
                    0
                );
            }

            throw new APIError('An unexpected error occurred while fetching playlist data.', 500);
        }
    }

    /**
     * Convert/download playlist using the backend pipeline
     * @param {string} playlistUrl - Spotify playlist URL
     * @param {Object} options - Conversion options
     * @returns {Promise<Object>}
     */
    static async convertPlaylist(playlistUrl, options = {}) {
        try {
            const requestBody = {
                playlist_url: playlistUrl,
                mixes_per_track: options.mixes_per_track || 10,
                download_songs: options.download_songs !== false,
                download_mixes: options.download_mixes !== false
            };

            const response = await fetch(`${API_BASE_URL}/playlist/convert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(
                    errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
                    response.status
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }

            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new APIError(
                    'Unable to connect to the backend server. Please make sure it\'s running.',
                    0
                );
            }

            throw new APIError('An unexpected error occurred during playlist conversion.', 500);
        }
    }

    /**
     * Check if the backend is healthy/reachable
     * @returns {Promise<boolean>}
     */
    static async checkHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/docs`, {
                method: 'GET',
                timeout: 5000
            });
            return response.ok;
        } catch {
            return false;
        }
    }

    /**
     * Extract playlist name from URL (basic implementation)
     * In a real app, this would come from the Spotify API response
     * @param {string} url - Spotify playlist URL
     * @returns {string}
     */
    static extractPlaylistName(url) {
        // This is a placeholder - in reality the playlist name would come from Spotify API
        const playlistId = url.split('/playlist/')[1]?.split('?')[0];
        return playlistId ? `Playlist ${playlistId.substring(0, 8)}...` : 'Unknown Playlist';
    }
}

export { APIError };
