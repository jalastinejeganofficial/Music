/**
 * YouTube Music Web Player - Frontend Application
 * Features: Home (All Music), Real-time Typing Search Filtering, Custom User Playlists,
 * Mobile Responsive UI with Full-Screen Mobile Music Player (Loop, Next, Prev, Shuffle, Scrub).
 */

const state = {
  homeTracks: [],
  currentTracks: [],
  currentIndex: -1,
  isPlaying: false,
  isShuffle: false,
  isRepeat: false,
  isMuted: false,
  previousVolume: 0.8,
  viewMode: 'list', // 'list' | 'grid'
  activeTab: 'home', // 'home' | 'search' | 'playlist'
  activePlaylistId: null,
  userPlaylists: [],
  searchDebounceTimer: null,
  trackPendingSave: null
};

// DOM Elements
const audio = document.getElementById('global-audio');
const searchInput = document.getElementById('search-input');
const searchClearBtn = document.getElementById('search-clear-btn');
const tracksContainer = document.getElementById('tracks-container');
const loadingSpinner = document.getElementById('loading-spinner');
const loadingText = document.getElementById('loading-text');

// Hero Elements
const heroCover = document.getElementById('hero-cover');
const heroBadge = document.getElementById('hero-badge');
const heroTitle = document.getElementById('hero-title');
const heroDesc = document.getElementById('hero-desc');
const heroOwner = document.getElementById('hero-owner');
const heroTracksCount = document.getElementById('hero-tracks-count');
const btnHeroAction = document.getElementById('btn-hero-action');

// Mini Player Elements (Bottom Bar)
const playerThumb = document.getElementById('player-thumb');
const playerTitle = document.getElementById('player-title');
const playerArtist = document.getElementById('player-artist');
const playPauseIcon = document.getElementById('play-pause-icon');
const playerFavBtn = document.getElementById('player-fav-btn');
const timeCurrent = document.getElementById('time-current');
const timeTotal = document.getElementById('time-total');
const progressFill = document.getElementById('progress-fill');
const progressThumb = document.getElementById('progress-thumb');
const volumeSlider = document.getElementById('volume-slider');
const volumeIcon = document.getElementById('volume-icon');

// Full-Screen Mobile Music Player Elements
const mobilePlayerOverlay = document.getElementById('mobile-player-overlay');
const mobilePlayerArt = document.getElementById('mobile-player-art');
const mobilePlayerSongTitle = document.getElementById('mobile-player-song-title');
const mobilePlayerSongArtist = document.getElementById('mobile-player-song-artist');
const mobilePlayerHeartBtn = document.getElementById('mobile-player-heart-btn');
const mobileTimeCurrent = document.getElementById('mobile-time-current');
const mobileTimeTotal = document.getElementById('mobile-time-total');
const mobileProgressFill = document.getElementById('mobile-progress-fill');
const mobileProgressThumb = document.getElementById('mobile-progress-thumb');
const mobilePlayPauseIcon = document.getElementById('mobile-play-pause-icon');
const mobileBtnShuffle = document.getElementById('mobile-btn-shuffle');
const mobileBtnRepeat = document.getElementById('mobile-btn-repeat');
const mobilePlayerContext = document.getElementById('mobile-player-context');

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
  setupAudioListeners();
  setupSearchInput();
  initUserPlaylists();
  loadHomeMusic();
});

// Setup Audio Listeners
function setupAudioListeners() {
  audio.addEventListener('timeupdate', onAudioTimeUpdate);
  audio.addEventListener('play', () => {
    state.isPlaying = true;
    updatePlayPauseUI();
  });
  audio.addEventListener('pause', () => {
    state.isPlaying = false;
    updatePlayPauseUI();
  });
  audio.addEventListener('ended', onAudioEnded);
  audio.addEventListener('loadedmetadata', () => {
    const formatted = formatTime(audio.duration);
    if (timeTotal) timeTotal.textContent = formatted;
    if (mobileTimeTotal) mobileTimeTotal.textContent = formatted;
  });
}

// ========================================================
// MOBILE FULL-SCREEN PLAYER CONTROLS
// ========================================================
function handleMiniPlayerBarClick(event) {
  // If user clicked directly on an interactive button, do not open overlay
  if (event.target.closest('button') || event.target.closest('input') || event.target.closest('.progress-bar-wrapper')) {
    return;
  }
  openMobileFullPlayer();
}

function openMobileFullPlayer() {
  if (!mobilePlayerOverlay) return;
  mobilePlayerOverlay.classList.remove('hidden');
  syncMobilePlayerState();
}

function closeMobileFullPlayer() {
  if (!mobilePlayerOverlay) return;
  mobilePlayerOverlay.classList.add('hidden');
}

function syncMobilePlayerState() {
  if (state.currentIndex >= 0 && state.currentTracks[state.currentIndex]) {
    const track = state.currentTracks[state.currentIndex];
    const coverUrl = track.cover_image_large || track.cover_image || 'https://music.youtube.com/img/favicon_144.png';
    if (mobilePlayerArt) mobilePlayerArt.src = coverUrl;
    if (mobilePlayerSongTitle) mobilePlayerSongTitle.textContent = track.title || 'Untitled';
    if (mobilePlayerSongArtist) mobilePlayerSongArtist.textContent = track.artist_display || 'Unknown Artist';

    // Playing from context
    if (mobilePlayerContext) {
      if (state.activeTab === 'playlist') {
        const pl = state.userPlaylists.find(p => p.id === state.activePlaylistId);
        mobilePlayerContext.textContent = pl ? pl.name : 'My Playlist';
      } else if (state.activeTab === 'search') {
        mobilePlayerContext.textContent = 'Search Results';
      } else {
        mobilePlayerContext.textContent = 'All Music (Home)';
      }
    }

    // Like status
    const likedPl = state.userPlaylists.find(p => p.id === 'liked_songs');
    const isLiked = likedPl && likedPl.tracks.some(t => t.id === track.id);
    if (mobilePlayerHeartBtn) {
      mobilePlayerHeartBtn.classList.toggle('active', Boolean(isLiked));
      mobilePlayerHeartBtn.querySelector('i').className = isLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
    }
  }

  // Sync controls (Repeat, Shuffle, Play/Pause)
  if (mobileBtnShuffle) mobileBtnShuffle.classList.toggle('active', state.isShuffle);
  if (mobileBtnRepeat) mobileBtnRepeat.classList.toggle('active', state.isRepeat);
  if (mobilePlayPauseIcon) {
    mobilePlayPauseIcon.className = state.isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play';
  }
}

function seekAudioMobile(event) {
  const wrapper = document.getElementById('mobile-progress-wrapper');
  if (!wrapper || !audio.duration) return;
  const rect = wrapper.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const width = rect.width;
  const percent = Math.max(0, Math.min(1, clickX / width));
  audio.currentTime = percent * audio.duration;
}

// ========================================================
// USER PLAYLISTS MANAGEMENT (Local Storage)
// ========================================================
function initUserPlaylists() {
  const saved = localStorage.getItem('ytm_user_playlists');
  if (saved) {
    try {
      state.userPlaylists = JSON.parse(saved);
    } catch (e) {
      state.userPlaylists = [];
    }
  }

  if (!state.userPlaylists.some(pl => pl.id === 'liked_songs')) {
    state.userPlaylists.unshift({
      id: 'liked_songs',
      name: 'Liked Songs ❤️',
      isDefault: true,
      tracks: []
    });
    saveUserPlaylists();
  }

  renderPlaylists();
}

function saveUserPlaylists() {
  localStorage.setItem('ytm_user_playlists', JSON.stringify(state.userPlaylists));
  renderPlaylists();
}

function renderPlaylists() {
  const sidebarList = document.getElementById('sidebar-playlists-list');
  const mobileList = document.getElementById('mobile-playlists-list');

  const html = state.userPlaylists.map(pl => {
    const isActive = (state.activeTab === 'playlist' && state.activePlaylistId === pl.id);
    const count = pl.tracks ? pl.tracks.length : 0;
    
    let iconHtml = '';
    if (pl.cover_image) {
      iconHtml = `<img src="${escapeHtml(pl.cover_image)}" class="playlist-thumb-img" alt="" onerror="this.outerHTML='<i class=\\'fa-brands fa-spotify\\' style=\\'color:#1db954\\'></i>'">`;
    } else if (pl.source === 'spotify') {
      iconHtml = `<i class="fa-brands fa-spotify" style="color: #1db954"></i>`;
    } else if (pl.isDefault) {
      iconHtml = `<i class="fa-solid fa-heart"></i>`;
    } else {
      iconHtml = `<i class="fa-solid fa-music"></i>`;
    }

    return `
      <div class="playlist-sidebar-item ${isActive ? 'active' : ''}" onclick="openPlaylistView('${pl.id}')">
        <div class="playlist-icon-thumb">
          ${iconHtml}
        </div>
        <div class="playlist-info">
          <div class="playlist-name">${escapeHtml(pl.name)}</div>
          <div class="playlist-count">${count} ${count === 1 ? 'song' : 'songs'}${pl.source === 'spotify' ? ' • Spotify' : ''}</div>
        </div>
      </div>
    `;
  }).join('');

  if (sidebarList) sidebarList.innerHTML = html;
  if (mobileList) mobileList.innerHTML = html;
}

// Modal Tabs Switcher
function switchCreateModalTab(tab) {
  const tabBtnSpotify = document.getElementById('tab-btn-spotify');
  const tabBtnCustom = document.getElementById('tab-btn-custom');
  const paneSpotify = document.getElementById('tab-pane-spotify');
  const paneCustom = document.getElementById('tab-pane-custom');
  const errorEl = document.getElementById('spotify-modal-error');
  if (errorEl) errorEl.classList.add('hidden');

  if (tab === 'spotify') {
    tabBtnSpotify.classList.add('active');
    tabBtnCustom.classList.remove('active');
    paneSpotify.classList.remove('hidden');
    paneCustom.classList.add('hidden');
    setTimeout(() => {
      const input = document.getElementById('spotify-playlist-url');
      if (input) input.focus();
    }, 50);
  } else {
    tabBtnCustom.classList.add('active');
    tabBtnSpotify.classList.remove('active');
    paneCustom.classList.remove('hidden');
    paneSpotify.classList.add('hidden');
    setTimeout(() => {
      const input = document.getElementById('new-playlist-name');
      if (input) input.focus();
    }, 50);
  }
}

// Open / Close Create & Import Playlist Modal
function openCreatePlaylistModal() {
  switchCreateModalTab('spotify');
  
  const urlInput = document.getElementById('spotify-playlist-url');
  if (urlInput) urlInput.value = '';
  
  const nameInput = document.getElementById('new-playlist-name');
  if (nameInput) nameInput.value = '';

  const statusEl = document.getElementById('spotify-import-status');
  if (statusEl) statusEl.classList.add('hidden');

  const errorEl = document.getElementById('spotify-modal-error');
  if (errorEl) errorEl.classList.add('hidden');

  const btnImport = document.getElementById('btn-import-spotify');
  if (btnImport) btnImport.disabled = false;

  document.getElementById('create-playlist-modal').classList.remove('hidden');

  loadSpotifyModalPresets();
}

function closeCreatePlaylistModal() {
  document.getElementById('create-playlist-modal').classList.add('hidden');
}

// Load presets for Spotify 1-click import
async function loadSpotifyModalPresets() {
  const container = document.getElementById('spotify-preset-chips');
  if (!container) return;

  if (state.spotifyPresets && state.spotifyPresets.length > 0) {
    renderSpotifyPresets(state.spotifyPresets);
    return;
  }

  try {
    const res = await fetch('/api/spotify_presets');
    const data = await res.json();
    if (data.presets && data.presets.length > 0) {
      state.spotifyPresets = data.presets;
      renderSpotifyPresets(data.presets);
    }
  } catch (err) {
    console.error("Could not fetch Spotify presets:", err);
  }
}

function renderSpotifyPresets(presets) {
  const container = document.getElementById('spotify-preset-chips');
  if (!container) return;
  container.innerHTML = presets.map(p => {
    const label = p.title || p.name || 'Playlist';
    const tag = p.tag || p.description || '';
    return `
      <button type="button" class="spotify-chip" onclick="selectSpotifyPreset('${escapeHtml(p.url)}')" title="${escapeHtml(tag)}">
        <i class="fa-brands fa-spotify"></i>
        <span>${escapeHtml(label)}</span>
      </button>
    `;
  }).join('');
}

function selectSpotifyPreset(url) {
  const urlInput = document.getElementById('spotify-playlist-url');
  if (urlInput) {
    urlInput.value = url;
  }
  submitSpotifyImport();
}

function handleSpotifyImportKeyPress(e) {
  if (e.key === 'Enter') submitSpotifyImport();
}

async function submitSpotifyImport() {
  const urlInput = document.getElementById('spotify-playlist-url');
  const url = urlInput ? urlInput.value.trim() : '';
  const errorEl = document.getElementById('spotify-modal-error');
  const statusEl = document.getElementById('spotify-import-status');
  const statusTitle = document.getElementById('spotify-status-title');
  const statusDesc = document.getElementById('spotify-status-desc');
  const btnImport = document.getElementById('btn-import-spotify');

  if (!url) {
    if (errorEl) {
      errorEl.textContent = 'Please paste a valid Spotify playlist URL or ID.';
      errorEl.classList.remove('hidden');
    }
    return;
  }

  if (errorEl) errorEl.classList.add('hidden');
  if (statusEl) statusEl.classList.remove('hidden');
  if (statusTitle) statusTitle.textContent = 'Scraping Spotify Playlist...';
  if (statusDesc) statusDesc.textContent = 'Extracting tracklist, matching on YouTube Music & fetching audio streams';
  if (btnImport) btnImport.disabled = true;

  try {
    const res = await fetch('/api/import_spotify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url, limit: 50 })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.detail || data.error || data.message || 'Failed to import Spotify playlist.');
    }

    if (!data.tracks || data.tracks.length === 0) {
      throw new Error('No songs could be matched from this Spotify playlist.');
    }

    const newPlaylist = {
      id: 'pl_' + Date.now(),
      name: data.playlist_name || 'Imported Spotify Playlist',
      description: data.description || `Imported Spotify playlist with ${data.tracks.length} songs.`,
      cover_image: data.cover || (data.tracks[0] ? data.tracks[0].cover_image_large : ''),
      source: 'spotify',
      isDefault: false,
      tracks: data.tracks
    };

    state.userPlaylists.push(newPlaylist);
    saveUserPlaylists();
    closeCreatePlaylistModal();
    closeMobilePlaylistsDrawer();

    openPlaylistView(newPlaylist.id);
    showToast(`Imported "${newPlaylist.name}" with ${newPlaylist.tracks.length} songs!`, 'success');

  } catch (err) {
    console.error("Spotify import error:", err);
    if (errorEl) {
      errorEl.textContent = err.message || 'Failed to import Spotify playlist. Please check the URL and try again.';
      errorEl.classList.remove('hidden');
    }
    if (statusEl) statusEl.classList.add('hidden');
    if (btnImport) btnImport.disabled = false;
  }
}

function handleCreatePlaylistKeyPress(e) {
  if (e.key === 'Enter') confirmCreatePlaylist();
}

function confirmCreatePlaylist() {
  const nameInput = document.getElementById('new-playlist-name');
  const name = nameInput.value.trim();
  if (!name) {
    showToast("Please enter a playlist name", "error");
    return;
  }

  const newPlaylist = {
    id: 'pl_' + Date.now(),
    name: name,
    description: `Custom playlist with 0 songs. Saved in your music player.`,
    cover_image: '',
    source: 'custom',
    isDefault: false,
    tracks: []
  };

  state.userPlaylists.push(newPlaylist);
  saveUserPlaylists();
  closeCreatePlaylistModal();
  closeMobilePlaylistsDrawer();

  openPlaylistView(newPlaylist.id);
  showToast(`Playlist "${newPlaylist.name}" created!`, "success");
}

function openPlaylistView(playlistId) {
  const pl = state.userPlaylists.find(p => p.id === playlistId);
  if (!pl) return;

  state.activeTab = 'playlist';
  state.activePlaylistId = playlistId;
  updateNavUI();
  closeMobilePlaylistsDrawer();

  if (pl.source === 'spotify') {
    heroBadge.textContent = 'SPOTIFY PLAYLIST';
    heroOwner.innerHTML = `<i class="fa-brands fa-spotify" style="color: #1DB954;"></i> Imported from Spotify`;
  } else {
    heroBadge.textContent = 'YOUR PLAYLIST';
    heroOwner.innerHTML = `<i class="fa-solid fa-user"></i> My Library`;
  }

  heroTitle.textContent = pl.name;
  heroDesc.textContent = pl.description || `Playlist with ${pl.tracks.length} songs. Saved in your music player.`;
  heroTracksCount.textContent = `${pl.tracks.length} ${pl.tracks.length === 1 ? 'song' : 'songs'}`;

  if (pl.cover_image) {
    heroCover.src = pl.cover_image;
  } else if (pl.tracks.length > 0 && pl.tracks[0].cover_image_large) {
    heroCover.src = pl.tracks[0].cover_image_large;
  } else {
    heroCover.src = 'https://music.youtube.com/img/favicon_144.png';
  }

  btnHeroAction.innerHTML = `<i class="fa-solid fa-trash"></i> Delete`;
  btnHeroAction.onclick = () => deletePlaylist(playlistId);

  state.currentTracks = pl.tracks || [];
  document.getElementById('content-heading').textContent = pl.name;
  document.getElementById('track-counter').textContent = `${state.currentTracks.length} saved songs`;

  renderTracks();
}

function deletePlaylist(playlistId) {
  const pl = state.userPlaylists.find(p => p.id === playlistId);
  if (!pl) return;
  if (pl.isDefault) {
    showToast("Default 'Liked Songs' playlist cannot be deleted.", "error");
    return;
  }

  if (confirm(`Are you sure you want to delete the playlist "${pl.name}"?`)) {
    state.userPlaylists = state.userPlaylists.filter(p => p.id !== playlistId);
    saveUserPlaylists();
    showToast(`Deleted playlist "${pl.name}"`, "info");
    switchTab('home');
  }
}

// Add/Save Song to Playlist Modal
function openSaveToPlaylistModal(trackIndex) {
  const track = state.currentTracks[trackIndex];
  if (!track) return;
  state.trackPendingSave = track;

  const preview = document.getElementById('saving-track-preview');
  preview.textContent = `Add "${track.title}" to playlist:`;

  const choicesList = document.getElementById('playlists-choice-list');
  choicesList.innerHTML = state.userPlaylists.map(pl => {
    const isAlreadySaved = pl.tracks.some(t => t.id === track.id);
    return `
      <div class="playlist-choice-item" onclick="toggleSaveToPlaylist('${pl.id}')">
        <span class="playlist-choice-name">${escapeHtml(pl.name)}</span>
        <span class="playlist-choice-tag" style="color: ${isAlreadySaved ? 'var(--ytm-red)' : 'var(--text-muted)'}">
          ${isAlreadySaved ? '<i class="fa-solid fa-check"></i> Added' : '<i class="fa-solid fa-plus"></i> Add'}
        </span>
      </div>
    `;
  }).join('');

  document.getElementById('save-to-playlist-modal').classList.remove('hidden');
}

function closeSaveToPlaylistModal() {
  document.getElementById('save-to-playlist-modal').classList.add('hidden');
  state.trackPendingSave = null;
}

function toggleSaveToPlaylist(playlistId) {
  const track = state.trackPendingSave;
  if (!track) return;

  const pl = state.userPlaylists.find(p => p.id === playlistId);
  if (!pl) return;

  const exists = pl.tracks.some(t => t.id === track.id);
  if (exists) {
    pl.tracks = pl.tracks.filter(t => t.id !== track.id);
  } else {
    pl.tracks.push(track);
  }

  saveUserPlaylists();
  closeSaveToPlaylistModal();

  if (state.activeTab === 'playlist' && state.activePlaylistId === playlistId) {
    openPlaylistView(playlistId);
  } else {
    renderTracks();
  }
}

// Toggle Favorite on current playing song
function togglePlayerFavorite() {
  if (state.currentIndex < 0 || !state.currentTracks[state.currentIndex]) return;
  const currentSong = state.currentTracks[state.currentIndex];
  const likedPl = state.userPlaylists.find(p => p.id === 'liked_songs');
  if (!likedPl) return;

  const isLiked = likedPl.tracks.some(t => t.id === currentSong.id);
  if (isLiked) {
    likedPl.tracks = likedPl.tracks.filter(t => t.id !== currentSong.id);
    updateLikeUI(false);
  } else {
    likedPl.tracks.push(currentSong);
    updateLikeUI(true);
  }

  saveUserPlaylists();
  if (state.activeTab === 'playlist' && state.activePlaylistId === 'liked_songs') {
    openPlaylistView('liked_songs');
  }
}

function updateLikeUI(isLiked) {
  if (playerFavBtn) {
    playerFavBtn.classList.toggle('active', isLiked);
    playerFavBtn.querySelector('i').className = isLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
  }
  if (mobilePlayerHeartBtn) {
    mobilePlayerHeartBtn.classList.toggle('active', isLiked);
    mobilePlayerHeartBtn.querySelector('i').className = isLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
  }
}

function openSaveToPlaylistForCurrent() {
  if (state.currentIndex >= 0 && state.currentTracks[state.currentIndex]) {
    openSaveToPlaylistModal(state.currentIndex);
  }
}

// ========================================================
// HOME MUSIC LOADING
// ========================================================
async function loadHomeMusic() {
  showLoading("Loading music...");
  try {
    const res = await fetch('/api/home');
    const data = await res.json();
    if (data.success && data.tracks && data.tracks.length > 0) {
      state.homeTracks = data.tracks;
      if (state.activeTab === 'home') {
        showHomeView();
      }
    } else {
      showFallbackSearch();
    }
  } catch (err) {
    console.error("Home music error:", err);
    showFallbackSearch();
  } finally {
    hideLoading();
  }
}

async function showFallbackSearch() {
  try {
    const res = await fetch('/api/search?q=Top%20Hits%202024');
    const data = await res.json();
    state.homeTracks = data.results || [];
    if (state.activeTab === 'home') {
      showHomeView();
    }
  } catch (e) {
    console.warn("Fallback failed:", e);
  }
}

function showHomeView() {
  state.activeTab = 'home';
  state.activePlaylistId = null;
  state.currentTracks = [...state.homeTracks];
  updateNavUI();

  heroBadge.textContent = 'DISCOVER';
  heroTitle.textContent = 'All Music';
  heroDesc.textContent = 'Explore all top tracks, save to your custom playlists, and stream instantly.';
  heroOwner.innerHTML = `<i class="fa-solid fa-wave-square"></i> Music Library`;
  heroTracksCount.textContent = `${state.currentTracks.length} songs`;
  
  if (state.currentTracks.length > 0 && state.currentTracks[0].cover_image_large) {
    heroCover.src = state.currentTracks[0].cover_image_large;
  }

  btnHeroAction.innerHTML = `<i class="fa-solid fa-plus"></i> New Playlist`;
  btnHeroAction.onclick = openCreatePlaylistModal;

  document.getElementById('content-heading').textContent = 'All Songs';
  document.getElementById('track-counter').textContent = `Showing ${state.currentTracks.length} songs`;

  renderTracks();
}

// ========================================================
// SEARCH & REAL-TIME TYPING FILTERING
// ========================================================
function setupSearchInput() {
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value;
    
    if (query.trim().length > 0) {
      searchClearBtn.classList.remove('hidden');
      performRealtimeFiltering(query.trim());
    } else {
      searchClearBtn.classList.add('hidden');
      if (state.activeTab === 'search') {
        showHomeView();
      }
    }
  });

  searchInput.addEventListener('focus', () => {
    if (state.activeTab !== 'search') {
      switchTab('search');
    }
  });
}

function clearSearch() {
  searchInput.value = '';
  searchClearBtn.classList.add('hidden');
  showHomeView();
}

function performRealtimeFiltering(query) {
  state.activeTab = 'search';
  state.activePlaylistId = null;
  updateNavUI();

  heroBadge.textContent = 'LIVE SEARCH & FILTER';
  heroTitle.textContent = `Search: "${query}"`;
  heroDesc.textContent = `Instant real-time search results matching "${query}".`;
  heroOwner.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> Live Filter`;

  const lowerQuery = query.toLowerCase();
  const localMatches = state.homeTracks.filter(track => {
    const t = (track.title || '').toLowerCase();
    const a = (track.artist_display || (track.artists || []).join(' ')).toLowerCase();
    return t.includes(lowerQuery) || a.includes(lowerQuery);
  });

  state.currentTracks = localMatches;
  document.getElementById('content-heading').textContent = `Results for "${query}"`;
  document.getElementById('track-counter').textContent = `${localMatches.length} matching locally`;
  renderTracks();

  clearTimeout(state.searchDebounceTimer);
  state.searchDebounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      if (data.success && data.results && data.results.length > 0) {
        const existingIds = new Set(localMatches.map(t => t.id));
        const newResults = data.results.filter(t => !existingIds.has(t.id));
        state.currentTracks = [...localMatches, ...newResults];
        
        if (state.currentTracks.length > 0 && state.currentTracks[0].cover_image_large) {
          heroCover.src = state.currentTracks[0].cover_image_large;
        }

        heroTracksCount.textContent = `${state.currentTracks.length} songs`;
        document.getElementById('track-counter').textContent = `${state.currentTracks.length} results found`;
        renderTracks();
      }
    } catch (err) {
      console.warn("Live search error:", err);
    }
  }, 350);
}

// ========================================================
// NAVIGATION & TABS
// ========================================================
function switchTab(tab) {
  if (tab === 'home') {
    searchInput.value = '';
    searchClearBtn.classList.add('hidden');
    showHomeView();
  } else if (tab === 'search') {
    state.activeTab = 'search';
    state.activePlaylistId = null;
    updateNavUI();
    searchInput.focus();
    if (searchInput.value.trim()) {
      performRealtimeFiltering(searchInput.value.trim());
    } else {
      document.getElementById('content-heading').textContent = 'Search Songs';
      document.getElementById('track-counter').textContent = 'Type in search bar to filter music';
    }
  }
}

function updateNavUI() {
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  if (state.activeTab === 'home') {
    document.getElementById('nav-home')?.classList.add('active');
  } else if (state.activeTab === 'search') {
    document.getElementById('nav-search')?.classList.add('active');
  }

  document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
  if (state.activeTab === 'home') {
    document.getElementById('mob-nav-home')?.classList.add('active');
  } else if (state.activeTab === 'search') {
    document.getElementById('mob-nav-search')?.classList.add('active');
  } else if (state.activeTab === 'playlist') {
    document.getElementById('mob-nav-library')?.classList.add('active');
  }

  renderPlaylists();
}

function openMobilePlaylistsDrawer() {
  document.getElementById('mobile-playlists-overlay').classList.remove('hidden');
}

function closeMobilePlaylistsDrawer(event) {
  if (!event || event.target.id === 'mobile-playlists-overlay' || event.target.closest('.drawer-close') || event.target.closest('.playlist-sidebar-item')) {
    document.getElementById('mobile-playlists-overlay').classList.add('hidden');
  }
}

function closeModalOnOverlay(e, modalId) {
  if (e.target.id === modalId) {
    document.getElementById(modalId).classList.add('hidden');
  }
}

// ========================================================
// TRACKS RENDERING (List / Grid)
// ========================================================
function setViewMode(mode) {
  state.viewMode = mode;
  document.getElementById('view-list-btn').classList.toggle('active', mode === 'list');
  document.getElementById('view-grid-btn').classList.toggle('active', mode === 'grid');
  renderTracks();
}

function renderTracks() {
  if (!state.currentTracks || state.currentTracks.length === 0) {
    tracksContainer.innerHTML = `
      <div class="loading-state" style="padding: 40px 0;">
        <i class="fa-solid fa-music" style="font-size: 32px; color: var(--text-muted); margin-bottom: 12px;"></i>
        <p style="color: var(--text-muted); font-size: 14px;">No songs found. Try a different search term or add songs to this playlist!</p>
      </div>
    `;
    return;
  }

  if (state.viewMode === 'list') {
    renderTracksList();
  } else {
    renderTracksGrid();
  }
}

function renderTracksList() {
  tracksContainer.className = 'tracks-container view-mode-list';
  const likedPl = state.userPlaylists.find(p => p.id === 'liked_songs');

  tracksContainer.innerHTML = state.currentTracks.map((track, idx) => {
    const isCurrent = (idx === state.currentIndex);
    const cover = track.cover_image || track.cover_image_large || heroCover.src;
    const dur = track.duration_str || '3:30';
    const isLiked = likedPl && likedPl.tracks.some(t => t.id === track.id);

    return `
      <div class="track-row ${isCurrent ? 'playing' : ''}" onclick="playTrack(${idx})">
        <div class="track-index">
          <span class="number">${idx + 1}</span>
          <i class="fa-solid fa-play play-icon"></i>
        </div>
        <img class="track-thumb" src="${cover}" alt="Art" loading="lazy">
        <div class="track-title-col">
          <div class="track-title" title="${escapeHtml(track.title)}">${escapeHtml(track.title)}</div>
          <div class="track-artists" title="${escapeHtml(track.artist_display || '')}">
            ${escapeHtml(track.artist_display || '')}
          </div>
        </div>
        <div class="track-duration">${dur}</div>
        <div class="track-actions" onclick="event.stopPropagation()">
          <button class="track-action-btn ${isLiked ? 'active' : ''}" title="Save to Liked Songs" onclick="quickToggleLike(${idx})">
            <i class="${isLiked ? 'fa-solid' : 'fa-regular'} fa-heart"></i>
          </button>
          <button class="track-action-btn" title="Add to Playlist" onclick="openSaveToPlaylistModal(${idx})">
            <i class="fa-solid fa-plus"></i>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderTracksGrid() {
  tracksContainer.className = 'tracks-container view-mode-grid';
  tracksContainer.innerHTML = state.currentTracks.map((track, idx) => {
    const cover = track.cover_image || track.cover_image_large || heroCover.src;
    const dur = track.duration_str || '3:30';

    return `
      <div class="grid-card" onclick="playTrack(${idx})">
        <div class="grid-cover-wrapper">
          <img src="${cover}" alt="Cover" loading="lazy">
          <div class="grid-play-btn">
            <i class="fa-solid fa-play"></i>
          </div>
        </div>
        <div class="grid-title" title="${escapeHtml(track.title)}">${escapeHtml(track.title)}</div>
        <div class="grid-artist" title="${escapeHtml(track.artist_display || '')}">${escapeHtml(track.artist_display || '')}</div>
        <div class="grid-meta">
          <span>${dur}</span>
          <button class="track-action-btn" title="Add to Playlist" onclick="event.stopPropagation(); openSaveToPlaylistModal(${idx})">
            <i class="fa-solid fa-plus"></i>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function quickToggleLike(trackIdx) {
  const track = state.currentTracks[trackIdx];
  if (!track) return;
  const likedPl = state.userPlaylists.find(p => p.id === 'liked_songs');
  if (!likedPl) return;

  const exists = likedPl.tracks.some(t => t.id === track.id);
  if (exists) {
    likedPl.tracks = likedPl.tracks.filter(t => t.id !== track.id);
  } else {
    likedPl.tracks.push(track);
  }

  saveUserPlaylists();
  renderTracks();

  // If currently playing, sync button
  if (trackIdx === state.currentIndex) {
    updateLikeUI(!exists);
  }
}

// ========================================================
// AUDIO STREAM PLAYBACK
// ========================================================
async function playTrack(index) {
  if (index < 0 || index >= state.currentTracks.length) return;

  state.currentIndex = index;
  const track = state.currentTracks[index];

  // Update Mini Player UI
  playerTitle.textContent = track.title || 'Untitled';
  playerArtist.textContent = track.artist_display || 'Unknown Artist';
  const coverUrl = track.cover_image_large || track.cover_image || heroCover.src;
  playerThumb.src = coverUrl;
  playerThumb.classList.add('playing');

  // Update Full-Screen Mobile Player UI
  if (mobilePlayerSongTitle) mobilePlayerSongTitle.textContent = track.title || 'Untitled';
  if (mobilePlayerSongArtist) mobilePlayerSongArtist.textContent = track.artist_display || 'Unknown Artist';
  if (mobilePlayerArt) mobilePlayerArt.src = coverUrl;

  // Check like state
  const likedPl = state.userPlaylists.find(p => p.id === 'liked_songs');
  const isLiked = likedPl && likedPl.tracks.some(t => t.id === track.id);
  updateLikeUI(Boolean(isLiked));

  // Resolve audio stream if needed
  let audioUrl = track.audio_url;
  if (!audioUrl) {
    try {
      showLoading(`Extracting audio stream for "${track.title}"...`);
      const res = await fetch(`/api/stream?video_id=${encodeURIComponent(track.id)}`);
      const data = await res.json();
      if (data.success && data.audio_url) {
        audioUrl = data.audio_url;
        track.audio_url = audioUrl; // Cache stream
      }
    } catch (e) {
      console.warn("Stream extraction error:", e);
    } finally {
      hideLoading();
    }
  }

  if (audioUrl) {
    audio.src = audioUrl;
    audio.play().catch(err => console.log("Autoplay:", err));
  } else {
    alert("Audio stream could not be loaded for this track.");
  }

  renderTracks();
}

function playFirstTrack() {
  if (state.currentTracks.length > 0) {
    playTrack(0);
  }
}

function togglePlayPause() {
  if (!audio.src) {
    if (state.currentTracks.length > 0) playTrack(0);
    return;
  }
  if (audio.paused) {
    audio.play();
  } else {
    audio.pause();
  }
}

function updatePlayPauseUI() {
  const iconName = state.isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play';
  if (playPauseIcon) playPauseIcon.className = iconName;
  if (mobilePlayPauseIcon) mobilePlayPauseIcon.className = iconName;

  if (state.isPlaying) {
    playerThumb.classList.add('playing');
  } else {
    playerThumb.classList.remove('playing');
  }
}

function playNextTrack() {
  if (state.currentTracks.length === 0) return;
  if (state.isShuffle) {
    const randomIndex = Math.floor(Math.random() * state.currentTracks.length);
    playTrack(randomIndex);
  } else {
    const nextIndex = (state.currentIndex + 1) % state.currentTracks.length;
    playTrack(nextIndex);
  }
}

function playPreviousTrack() {
  if (state.currentTracks.length === 0) return;
  if (audio.currentTime > 3) {
    audio.currentTime = 0;
  } else {
    const prevIndex = (state.currentIndex - 1 + state.currentTracks.length) % state.currentTracks.length;
    playTrack(prevIndex);
  }
}

function onAudioEnded() {
  // Loop / Repeat Logic: if isRepeat is true, replay current song!
  if (state.isRepeat) {
    audio.currentTime = 0;
    audio.play();
  } else {
    playNextTrack();
  }
}

function onAudioTimeUpdate() {
  if (!audio.duration) return;
  const current = audio.currentTime;
  const total = audio.duration;
  const percent = (current / total) * 100;
  const currentFormatted = formatTime(current);

  // Update Mini Player
  if (timeCurrent) timeCurrent.textContent = currentFormatted;
  if (progressFill) progressFill.style.width = `${percent}%`;
  if (progressThumb) progressThumb.style.left = `${percent}%`;

  // Update Full-Screen Mobile Player
  if (mobileTimeCurrent) mobileTimeCurrent.textContent = currentFormatted;
  if (mobileProgressFill) mobileProgressFill.style.width = `${percent}%`;
  if (mobileProgressThumb) mobileProgressThumb.style.left = `${percent}%`;
}

function seekAudio(event) {
  const wrapper = document.getElementById('progress-wrapper');
  if (!wrapper || !audio.duration) return;
  const rect = wrapper.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const width = rect.width;
  const percent = Math.max(0, Math.min(1, clickX / width));
  audio.currentTime = percent * audio.duration;
}

function changeVolume(val) {
  audio.volume = val;
  state.isMuted = (val == 0);
  updateVolumeIcon(val);
}

function toggleMute() {
  if (state.isMuted) {
    audio.volume = state.previousVolume || 0.8;
    if (volumeSlider) volumeSlider.value = audio.volume;
    state.isMuted = false;
  } else {
    state.previousVolume = audio.volume;
    audio.volume = 0;
    if (volumeSlider) volumeSlider.value = 0;
    state.isMuted = true;
  }
  updateVolumeIcon(audio.volume);
}

function updateVolumeIcon(vol) {
  if (!volumeIcon) return;
  if (vol == 0) {
    volumeIcon.className = 'fa-solid fa-volume-xmark';
  } else if (vol < 0.5) {
    volumeIcon.className = 'fa-solid fa-volume-low';
  } else {
    volumeIcon.className = 'fa-solid fa-volume-high';
  }
}

function toggleShuffle() {
  state.isShuffle = !state.isShuffle;
  document.getElementById('btn-shuffle')?.classList.toggle('active', state.isShuffle);
  if (mobileBtnShuffle) mobileBtnShuffle.classList.toggle('active', state.isShuffle);
}

function toggleRepeat() {
  state.isRepeat = !state.isRepeat;
  document.getElementById('btn-repeat')?.classList.toggle('active', state.isRepeat);
  if (mobileBtnRepeat) mobileBtnRepeat.classList.toggle('active', state.isRepeat);
}

// Helpers
function showLoading(msg) {
  if (loadingText) loadingText.textContent = msg;
  loadingSpinner?.classList.remove('hidden');
}

function hideLoading() {
  loadingSpinner?.classList.add('hidden');
}

function formatTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info');
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
