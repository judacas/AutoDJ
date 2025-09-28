# AutoDJ Frontend

A Spotify-like React frontend for the AutoDJ application that allows users to input playlist URLs and view songs in a modern, responsive interface.

## Features

- 🎵 **Playlist Input**: Clean input field with URL validation for Spotify playlists
- 📋 **Song List**: Spotify-style song rows with album covers, titles, artists, and durations  
- 🎮 **Player Controls**: Full player interface with play/pause, next/previous, shuffle, and repeat
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🎨 **Modern UI**: Dark theme with Spotify-inspired styling using TailwindCSS
- ⚡ **React Hooks**: Built with modern React functional components and hooks

## Components

### `PlaylistInput.jsx`
- Input field for playlist URL submission
- URL validation for Spotify playlist links
- Loading states and error handling
- Clean, accessible form design

### `SongRow.jsx` 
- Individual song row component
- Displays track number, album cover, song title, artist, and duration
- Hover effects and play button interactions
- Highlights currently playing track

### `SongList.jsx`
- Main container for displaying playlist songs
- Playlist header with cover art and metadata
- Sticky column headers
- Empty state handling

### `PlayerControls.jsx`
- Bottom player bar with full controls
- Play/pause, previous/next, shuffle, repeat buttons
- Progress bar with seek functionality
- Volume control with slider
- Currently playing track info

### `App.js`
- Main application component
- State management for playlist, player, and UI states
- Mock API integration (ready for backend connection)
- Handles all user interactions and data flow

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm start
```

Opens the app in development mode at [http://localhost:3000](http://localhost:3000).

## Build

```bash
npm run build
```

Builds the app for production to the `build` folder.

## Technology Stack

- **React 18** - Modern React with functional components and hooks
- **TailwindCSS** - Utility-first CSS framework for rapid styling
- **Lucide React** - Beautiful, customizable SVG icons
- **PostCSS** - CSS processing for TailwindCSS

## Styling

The app uses a custom Spotify-inspired color palette:

- **Primary Green**: `#1db954` (Spotify green)
- **Dark Background**: `#191414` (Spotify dark)
- **Gray Elements**: `#282828` (Spotify gray)
- **Light Text**: `#b3b3b3` (Spotify light gray)

## Backend Integration

The app currently uses mock data but is structured to easily integrate with a real backend:

1. Replace the `mockFetchPlaylist` function in `App.js` with real API calls
2. Update the data structure mapping if needed
3. Add authentication handling for Spotify API
4. Implement audio playback with Web Audio API or similar

## Responsive Design

The interface is fully responsive with:

- Mobile-first approach
- Flexible grid layouts
- Touch-friendly controls
- Optimized typography scaling
- Adaptive component visibility

## Future Enhancements

- [ ] Real audio playback integration
- [ ] Spotify Web API integration  
- [ ] User authentication
- [ ] Playlist creation/editing
- [ ] Search functionality
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements