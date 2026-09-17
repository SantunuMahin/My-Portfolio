/**
 * PIN INTERAST - NEUMORPHIC AUDIO MUSIC LOUNGE & FAVORITES PLAYER
 * Santunu Kaysar Portfolio
 */
(function () {
  'use strict';

  // Player state
  let tracks = [];
  let currentIndex = 0;
  let isPlaying = false;
  let isShuffle = false;
  let isRepeat = false;
  let currentFilter = 'all'; // 'all' or 'favorites'
  const audio = new Audio();
  audio.preload = 'metadata';

  // Config & Admin status
  const isAdmin = !!(window.PIN_MUSIC_CONFIG && window.PIN_MUSIC_CONFIG.isAdmin);
  const LOCAL_FAVS_KEY = 'pin_lounge_fav_tracks_v1';

  function getLocalFavs() {
    try {
      const raw = localStorage.getItem(LOCAL_FAVS_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  function saveLocalFavs(favIds) {
    try {
      localStorage.setItem(LOCAL_FAVS_KEY, JSON.stringify(favIds));
    } catch (_) {}
  }

  // Dynamic API URL resolver
  function getApiUrl(type, id) {
    const urls = window.PIN_MUSIC_CONFIG && window.PIN_MUSIC_CONFIG.urls;
    if (urls) {
      if (type === 'list' && urls.list) return urls.list;
      if (type === 'add' && urls.add) return urls.add;
      if (type === 'favorite' && urls.favoriteTpl) return urls.favoriteTpl.replace(':id', id);
      if (type === 'delete' && urls.deleteTpl) return urls.deleteTpl.replace(':id', id);
      if (type === 'download' && urls.downloadTpl) return urls.downloadTpl.replace(':id', id);
    }
    const base = (window.location && window.location.pathname && window.location.pathname.startsWith('/pin-interast')) ? '/pin-interast' : '/pins';
    if (type === 'list') return `${base}/music/api/`;
    if (type === 'add') return `${base}/music/api/add/`;
    if (type === 'favorite') return `${base}/music/api/${id}/favorite/`;
    if (type === 'delete') return `${base}/music/api/${id}/delete/`;
    if (type === 'download') return `${base}/music/${id}/download/`;
    return `${base}/music/api/`;
  }

  // DOM Elements
  const container = document.getElementById('pin-music-lounge');
  if (!container) return;

  const playerCoverImg = document.getElementById('playerCoverImg');
  const playerTitle = document.getElementById('playerTitle');
  const playerArtist = document.getElementById('playerArtist');
  const playerGenre = document.getElementById('playerGenre');
  const playerStatusText = document.getElementById('playerStatusText');
  const liveEqBars = document.getElementById('liveEqBars');
  const vinylDisk = document.getElementById('vinylDiskWrapper');
  const turntableTonearm = document.getElementById('turntableTonearm');

  const btnPlayPause = document.getElementById('btnPlayPause');
  const playPauseIcon = document.getElementById('playPauseIcon');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnShuffle = document.getElementById('btnShuffle');
  const btnRepeat = document.getElementById('btnRepeat');
  const btnPlayerFav = document.getElementById('btnPlayerFav');
  const playerFavIcon = document.getElementById('playerFavIcon');
  const btnDownload = document.getElementById('btnDownload');
  const downloadIcon = document.getElementById('downloadIcon');

  const progressTrack = document.getElementById('progressTrack');
  const progressBarFill = document.getElementById('progressBarFill');
  const progressHandle = document.getElementById('progressHandle');
  const playerCurrentTime = document.getElementById('playerCurrentTime');
  const playerTotalDuration = document.getElementById('playerTotalDuration');

  const btnMute = document.getElementById('btnMute');
  const volumeIcon = document.getElementById('volumeIcon');
  const volTrack = document.getElementById('volTrack');
  const volBarFill = document.getElementById('volBarFill');

  const playlistItemsList = document.getElementById('playlistItemsList');
  const tabAllTracks = document.getElementById('tabAllTracks');
  const tabFavTracks = document.getElementById('tabFavTracks');
  const countAllTracks = document.getElementById('countAllTracks');
  const countFavTracks = document.getElementById('countFavTracks');
  const playlistCounter = document.getElementById('playlistCounter');

  // Modal elements
  const openAddMusicBtn = document.getElementById('openAddMusicBtn');
  const addMusicModal = document.getElementById('addMusicModal');
  const closeAddMusicModal = document.getElementById('closeAddMusicModal');
  const addMusicForm = document.getElementById('addMusicForm');
  const musicCoverUrl = document.getElementById('musicCoverUrl');
  const coverPreviewBox = document.getElementById('coverPreviewBox');
  const coverPreviewImg = document.getElementById('coverPreviewImg');
  const submitAddMusicBtn = document.getElementById('submitAddMusicBtn');

  // Format seconds to mm:ss
  function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '00:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
  }

  // Get filtered tracks based on tab
  function getFilteredTracks() {
    if (currentFilter === 'favorites') {
      return tracks.filter(t => t.is_favorite);
    }
    return tracks;
  }

  // Load a track by filtered index
  function loadTrack(index, autoPlay = false) {
    const list = getFilteredTracks();
    if (!list.length) {
      playerTitle.textContent = 'No tracks found';
      playerArtist.textContent = 'Add some music to start listening';
      playerGenre.textContent = 'Silence';
      playerCoverImg.src = 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80';
      playerCurrentTime.textContent = '00:00';
      playerTotalDuration.textContent = '00:00';
      progressBarFill.style.width = '0%';
      if (progressHandle) progressHandle.style.left = '0%';
      pauseTrack();
      return;
    }

    if (index < 0) index = list.length - 1;
    if (index >= list.length) index = 0;
    currentIndex = index;

    const track = list[currentIndex];
    playerTitle.textContent = track.title;
    playerArtist.textContent = track.artist;
    playerGenre.textContent = track.genre || 'Lo-Fi / Ambient';
    playerCoverImg.src = track.cover_art_url || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80';

    // Update favorite heart button in main player
    if (track.is_favorite) {
      btnPlayerFav.classList.add('favorited');
      playerFavIcon.setAttribute('name', 'heart');
    } else {
      btnPlayerFav.classList.remove('favorited');
      playerFavIcon.setAttribute('name', 'heart-outline');
    }

    // Set audio source
    if (track.stream_url) {
      audio.src = track.stream_url;
      audio.load();
      if (autoPlay) {
        playTrack();
      } else {
        pauseTrack();
      }
    } else {
      pauseTrack();
      playerStatusText.textContent = 'Audio URL missing';
    }

    highlightActivePlaylistItem();
  }

  function playTrack() {
    if (!audio.src) return;
    const playPromise = audio.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        isPlaying = true;
        playPauseIcon.setAttribute('name', 'pause');
        btnPlayPause.classList.add('playing');
        playerStatusText.textContent = 'Now Playing';
        if (liveEqBars) liveEqBars.classList.add('playing');
        if (vinylDisk) vinylDisk.classList.add('spinning');
        if (turntableTonearm) turntableTonearm.classList.add('active');
        highlightActivePlaylistItem();
      }).catch(err => {
        console.warn('Audio playback error / prevented:', err);
        isPlaying = false;
        playPauseIcon.setAttribute('name', 'play');
        btnPlayPause.classList.remove('playing');
        playerStatusText.textContent = 'Stream error or blocked';
        if (liveEqBars) liveEqBars.classList.remove('playing');
        if (vinylDisk) vinylDisk.classList.remove('spinning');
      });
    }
  }

  function pauseTrack() {
    audio.pause();
    isPlaying = false;
    playPauseIcon.setAttribute('name', 'play');
    btnPlayPause.classList.remove('playing');
    playerStatusText.textContent = 'Paused';
    if (liveEqBars) liveEqBars.classList.remove('playing');
    if (vinylDisk) vinylDisk.classList.remove('spinning');
    if (turntableTonearm) turntableTonearm.classList.remove('active');
    highlightActivePlaylistItem();
  }

  function togglePlay() {
    if (isPlaying) {
      pauseTrack();
    } else {
      playTrack();
    }
  }

  function prevTrack() {
    const list = getFilteredTracks();
    if (!list.length) return;
    let nextIdx = currentIndex - 1;
    if (nextIdx < 0) nextIdx = list.length - 1;
    loadTrack(nextIdx, true);
  }

  function nextTrack() {
    const list = getFilteredTracks();
    if (!list.length) return;
    let nextIdx;
    if (isShuffle) {
      nextIdx = Math.floor(Math.random() * list.length);
      if (list.length > 1 && nextIdx === currentIndex) {
        nextIdx = (nextIdx + 1) % list.length;
      }
    } else {
      nextIdx = (currentIndex + 1) % list.length;
    }
    loadTrack(nextIdx, true);
  }

  // Highlight active item in playlist DOM
  function highlightActivePlaylistItem() {
    const list = getFilteredTracks();
    const currentTrack = list[currentIndex];
    const items = playlistItemsList.querySelectorAll('.playlist-item');
    items.forEach(el => {
      const trackId = parseInt(el.dataset.trackId, 10);
      const isCurrent = currentTrack && trackId === currentTrack.id;
      el.classList.toggle('active', isCurrent);
      const idleIcon = el.querySelector('.item-icon-idle');
      const playingAnim = el.querySelector('.item-icon-playing');
      if (idleIcon && playingAnim) {
        if (isCurrent && isPlaying) {
          idleIcon.style.display = 'none';
          playingAnim.style.display = 'inline-flex';
        } else {
          idleIcon.style.display = 'block';
          playingAnim.style.display = 'none';
          idleIcon.setAttribute('name', isCurrent ? 'pause-outline' : 'play-outline');
        }
      }
    });
  }

  // Render the playlist drawer
  function renderPlaylist() {
    const list = getFilteredTracks();
    playlistItemsList.innerHTML = '';

    if (!list.length) {
      playlistItemsList.innerHTML = `
        <li class="playlist-empty-state">
          <ion-icon name="${currentFilter === 'favorites' ? 'heart-dislike-outline' : 'musical-notes-outline'}"></ion-icon>
          <p>${currentFilter === 'favorites' ? 'No favorite tracks yet. Heart any song to add it here!' : 'No tracks found. Click "Add Music" to add songs!'}</p>
        </li>
      `;
      playlistCounter.textContent = '0 Tracks';
      return;
    }

    playlistCounter.textContent = `${list.length} Track${list.length === 1 ? '' : 's'}`;

    list.forEach((track, idx) => {
      const li = document.createElement('li');
      li.className = 'playlist-item' + (idx === currentIndex ? ' active' : '');
      li.dataset.trackId = track.id;
      li.dataset.trackIndex = idx;
      li.dataset.isFav = track.is_favorite ? 'true' : 'false';

      li.innerHTML = `
        <div class="item-play-col">
          <button class="item-play-btn" data-action="play" data-index="${idx}" aria-label="Play track">
            <ion-icon name="play-outline" class="item-icon-idle"></ion-icon>
            <div class="item-icon-playing" style="display:none;">
              <span class="mini-eq-bar bar-1"></span>
              <span class="mini-eq-bar bar-2"></span>
              <span class="mini-eq-bar bar-3"></span>
            </div>
          </button>
        </div>
        <figure class="item-cover-thumb">
          <img src="${track.cover_art_url}" alt="${escapeHtml(track.title)}" loading="lazy">
        </figure>
        <div class="item-info-col">
          <h5 class="item-title">${escapeHtml(track.title)}</h5>
          <p class="item-artist">${escapeHtml(track.artist)} &bull; <span class="item-genre">${escapeHtml(track.genre || '')}</span></p>
        </div>
        <div class="item-meta-col">
          <span class="item-duration">${track.duration || '3:20'}</span>
          <button class="item-download-btn" data-action="download" data-id="${track.id}" title="Download Track" aria-label="Download ${escapeHtml(track.title)}">
            <ion-icon name="download-outline"></ion-icon>
          </button>
          <button class="item-fav-btn ${track.is_favorite ? 'favorited' : ''}" data-action="fav" data-id="${track.id}" title="Toggle Favorite" aria-label="Favorite">
            <ion-icon name="${track.is_favorite ? 'heart' : 'heart-outline'}"></ion-icon>
          </button>
          ${isAdmin ? `
          <button class="item-del-btn" data-action="del" data-id="${track.id}" title="Delete Track" aria-label="Delete">
            <ion-icon name="trash-outline"></ion-icon>
          </button>
          ` : ''}
        </div>
      `;

      // Item click event delegation
      li.addEventListener('click', (e) => {
        const favBtn = e.target.closest('[data-action="fav"]');
        const delBtn = e.target.closest('[data-action="del"]');
        const downloadBtn = e.target.closest('[data-action="download"]');
        const playBtn = e.target.closest('[data-action="play"]');

        if (downloadBtn) {
          e.stopPropagation();
          downloadTrack(track);
          return;
        }

        if (favBtn) {
          e.stopPropagation();
          toggleFavorite(track.id);
          return;
        }

        if (delBtn) {
          e.stopPropagation();
          deleteTrack(track.id, track.title);
          return;
        }

        // Play or toggle if clicking row or play button
        if (idx === currentIndex && isPlaying) {
          pauseTrack();
        } else {
          loadTrack(idx, true);
        }
      });

      playlistItemsList.appendChild(li);
    });

    highlightActivePlaylistItem();
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Update counter badges
  function updateCounts() {
    const total = tracks.length;
    const favs = tracks.filter(t => t.is_favorite).length;
    if (countAllTracks) countAllTracks.textContent = total;
    if (countFavTracks) countFavTracks.textContent = favs;
  }

  // Toggle favorite with localStorage persistence and API sync
  async function toggleFavorite(trackId) {
    const track = tracks.find(t => t.id === trackId);
    if (!track) return;

    // Optimistic UI update
    track.is_favorite = !track.is_favorite;
    const currentFavIds = tracks.filter(t => t.is_favorite).map(t => t.id);
    saveLocalFavs(currentFavIds);

    updateCounts();
    renderPlaylist();

    const list = getFilteredTracks();
    if (list[currentIndex] && list[currentIndex].id === trackId) {
      btnPlayerFav.classList.toggle('favorited', track.is_favorite);
      playerFavIcon.setAttribute('name', track.is_favorite ? 'heart' : 'heart-outline');
    }

    try {
      const csrfToken = getCsrfToken();
      await fetch(getApiUrl('favorite', trackId), {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      });
    } catch (err) {
      console.warn('Sync favorite error:', err);
    }
  }

  // Delete a track via AJAX
  async function deleteTrack(trackId, title) {
    if (!confirm(`Are you sure you want to remove "${title}" from your music list?`)) return;

    try {
      const csrfToken = getCsrfToken();
      const res = await fetch(getApiUrl('delete', trackId), {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
      });
      const data = await res.json();
      if (data.success) {
        const deletedIdx = tracks.findIndex(t => t.id === trackId);
        tracks = tracks.filter(t => t.id !== trackId);
        updateCounts();
        if (deletedIdx === currentIndex) {
          loadTrack(0, false);
        } else if (deletedIdx < currentIndex) {
          currentIndex--;
        }
        renderPlaylist();
      }
    } catch (err) {
      console.error('Error deleting track:', err);
    }
  }

  // Helper for Django CSRF
  function getCsrfToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  }

  // Download toast notification
  function showDownloadToast(message) {
    let toast = document.getElementById('musicToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'musicToast';
      toast.className = 'music-download-toast';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<ion-icon name="cloud-download-outline"></ion-icon> <span>${escapeHtml(message)}</span>`;
    toast.classList.add('visible');
    setTimeout(() => {
      toast.classList.remove('visible');
    }, 3200);
  }

  // Audio track downloader
  function downloadTrack(track) {
    if (!track) return;
    const downloadUrl = getApiUrl('download', track.id);
    const title = track.title || 'Track';
    const artist = track.artist || 'Artist';
    const filename = `${artist} - ${title}.mp3`.replace(/[\\/:*?"<>|]/g, '_');

    showDownloadToast(`Downloading "${title}"...`);

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      if (link.parentNode) link.parentNode.removeChild(link);
    }, 200);
  }

  // Audio events
  audio.addEventListener('timeupdate', () => {
    if (!audio.duration || isNaN(audio.duration)) return;
    const current = audio.currentTime;
    const total = audio.duration;
    const percent = Math.min(100, Math.max(0, (current / total) * 100));

    progressBarFill.style.width = `${percent}%`;
    if (progressHandle) {
      progressHandle.style.left = `${percent}%`;
    }
    playerCurrentTime.textContent = formatTime(current);
    playerTotalDuration.textContent = formatTime(total);
  });

  audio.addEventListener('loadedmetadata', () => {
    playerTotalDuration.textContent = formatTime(audio.duration);
  });

  audio.addEventListener('ended', () => {
    if (isRepeat) {
      audio.currentTime = 0;
      playTrack();
    } else {
      nextTrack();
    }
  });

  audio.addEventListener('waiting', () => {
    playerStatusText.textContent = 'Buffering...';
  });

  audio.addEventListener('playing', () => {
    playerStatusText.textContent = 'Now Playing';
  });

  // Scrubber seeking
  if (progressTrack) {
    let isDragging = false;

    function seekFromEvent(e) {
      const rect = progressTrack.getBoundingClientRect();
      const clientX = e.clientX !== undefined ? e.clientX : (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
      const clickX = Math.max(0, Math.min(clientX - rect.left, rect.width));
      const percentage = rect.width > 0 ? clickX / rect.width : 0;
      const percent = percentage * 100;
      if (audio.duration) {
        audio.currentTime = percentage * audio.duration;
        progressBarFill.style.width = `${percent}%`;
        if (progressHandle) {
          progressHandle.style.left = `${percent}%`;
        }
      }
    }

    progressTrack.addEventListener('mousedown', (e) => {
      isDragging = true;
      seekFromEvent(e);
    });

    window.addEventListener('mousemove', (e) => {
      if (isDragging) seekFromEvent(e);
    });

    window.addEventListener('mouseup', () => {
      if (isDragging) isDragging = false;
    });

    // Touch support for mobile devices
    progressTrack.addEventListener('touchstart', (e) => {
      const touch = e.touches[0];
      seekFromEvent(touch);
    }, { passive: true });

    progressTrack.addEventListener('touchmove', (e) => {
      const touch = e.touches[0];
      seekFromEvent(touch);
    }, { passive: true });
  }

  // Volume slider
  if (volTrack) {
    function setVolFromEvent(e) {
      const rect = volTrack.getBoundingClientRect();
      const clickX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      const vol = clickX / rect.width;
      audio.volume = vol;
      volBarFill.style.width = `${vol * 100}%`;
      if (vol === 0) {
        volumeIcon.setAttribute('name', 'volume-mute-outline');
      } else if (vol < 0.5) {
        volumeIcon.setAttribute('name', 'volume-low-outline');
      } else {
        volumeIcon.setAttribute('name', 'volume-medium-outline');
      }
    }

    volTrack.addEventListener('click', setVolFromEvent);

    if (btnMute) {
      let previousVolume = 0.8;
      btnMute.addEventListener('click', () => {
        if (audio.volume > 0) {
          previousVolume = audio.volume;
          audio.volume = 0;
          volBarFill.style.width = '0%';
          volumeIcon.setAttribute('name', 'volume-mute-outline');
        } else {
          audio.volume = previousVolume || 0.8;
          volBarFill.style.width = `${audio.volume * 100}%`;
          volumeIcon.setAttribute('name', 'volume-medium-outline');
        }
      });
    }
  }

  // Player controls
  btnPlayPause.addEventListener('click', togglePlay);
  if (vinylDisk) vinylDisk.addEventListener('click', togglePlay);
  btnPrev.addEventListener('click', prevTrack);
  btnNext.addEventListener('click', nextTrack);

  btnShuffle.addEventListener('click', () => {
    isShuffle = !isShuffle;
    btnShuffle.classList.toggle('active', isShuffle);
  });

  btnRepeat.addEventListener('click', () => {
    isRepeat = !isRepeat;
    btnRepeat.classList.toggle('active', isRepeat);
  });

  if (btnDownload) {
    btnDownload.addEventListener('click', () => {
      const list = getFilteredTracks();
      const currentTrack = list[currentIndex];
      if (!currentTrack) {
        showDownloadToast('No audio track selected to download');
        return;
      }
      btnDownload.classList.add('downloading');
      if (downloadIcon) downloadIcon.setAttribute('name', 'cloud-download-outline');
      downloadTrack(currentTrack);
      setTimeout(() => {
        btnDownload.classList.remove('downloading');
        if (downloadIcon) downloadIcon.setAttribute('name', 'download-outline');
      }, 1500);
    });
  }

  btnPlayerFav.addEventListener('click', () => {
    const list = getFilteredTracks();
    if (list[currentIndex]) {
      toggleFavorite(list[currentIndex].id);
    }
  });

  // Filter tabs
  tabAllTracks.addEventListener('click', () => {
    if (currentFilter === 'all') return;
    currentFilter = 'all';
    tabAllTracks.classList.add('active');
    tabFavTracks.classList.remove('active');
    renderPlaylist();
    highlightActivePlaylistItem();
  });

  tabFavTracks.addEventListener('click', () => {
    if (currentFilter === 'favorites') return;
    currentFilter = 'favorites';
    tabFavTracks.classList.add('active');
    tabAllTracks.classList.remove('active');
    renderPlaylist();
    highlightActivePlaylistItem();
  });

  // Modal open / close helpers
  function ensureModalsInBody() {
    const addModal = document.getElementById('addMusicModal');
    if (addModal && addModal.parentElement !== document.body) {
      document.body.appendChild(addModal);
    }
    const adminModal = document.getElementById('adminRequiredModal');
    if (adminModal && adminModal.parentElement !== document.body) {
      document.body.appendChild(adminModal);
    }
  }

  function showModal(modalEl) {
    if (!modalEl) return;
    ensureModalsInBody();
    modalEl.classList.add('active');
    document.body.classList.add('neu-modal-open');
  }

  function hideModal(modalEl) {
    if (!modalEl) return;
    modalEl.classList.remove('active');
    // Check if any modal is still active
    const anyActive = document.querySelector('.neu-modal.active');
    if (!anyActive) {
      document.body.classList.remove('neu-modal-open');
    }
  }

  if (openAddMusicBtn) {
    openAddMusicBtn.addEventListener('click', () => {
      if (isAdmin) {
        showModal(document.getElementById('addMusicModal'));
      } else {
        showModal(document.getElementById('adminRequiredModal'));
      }
    });
  }

  const closeAdminNoticeBtn = document.getElementById('closeAdminNoticeBtn');
  const dismissAdminNoticeBtn = document.getElementById('dismissAdminNoticeBtn');

  if (closeAddMusicModal) {
    closeAddMusicModal.addEventListener('click', () => hideModal(document.getElementById('addMusicModal')));
  }
  if (closeAdminNoticeBtn) {
    closeAdminNoticeBtn.addEventListener('click', () => hideModal(document.getElementById('adminRequiredModal')));
  }
  if (dismissAdminNoticeBtn) {
    dismissAdminNoticeBtn.addEventListener('click', () => hideModal(document.getElementById('adminRequiredModal')));
  }

  // Backdrop click for all modals
  window.addEventListener('click', (e) => {
    if (e.target.classList && e.target.classList.contains('neu-modal')) {
      hideModal(e.target);
    }
  });

  // ESC key
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.neu-modal.active').forEach(m => hideModal(m));
    }
  });

  // Live Cover Image Preview when typing URL
  if (musicCoverUrl && coverPreviewBox && coverPreviewImg) {
    let previewTimer;
    musicCoverUrl.addEventListener('input', () => {
      clearTimeout(previewTimer);
      previewTimer = setTimeout(() => {
        const val = musicCoverUrl.value.trim();
        if (val && (val.startsWith('http://') || val.startsWith('https://'))) {
          coverPreviewImg.src = val;
          coverPreviewBox.style.display = 'block';
        } else {
          coverPreviewBox.style.display = 'none';
        }
      }, 300);
    });
  }

  // Submit Add Music Form via AJAX
  if (addMusicForm) {
    addMusicForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(addMusicForm);

      submitAddMusicBtn.disabled = true;
      const originalHtml = submitAddMusicBtn.innerHTML;
      submitAddMusicBtn.innerHTML = `<ion-icon name="sync-outline" class="spin-icon"></ion-icon> Adding Track...`;

      try {
        const res = await fetch(getApiUrl('add'), {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
          },
          body: formData,
        });
        const data = await res.json();

        if (res.status === 403 || data.requires_admin) {
          hideModal(document.getElementById('addMusicModal'));
          showModal(document.getElementById('adminRequiredModal'));
          return;
        }

        if (data.success && data.track) {
          tracks.unshift(data.track);
          if (data.track.is_favorite) {
            const curFavs = getLocalFavs() || [];
            if (!curFavs.includes(data.track.id)) {
              curFavs.push(data.track.id);
              saveLocalFavs(curFavs);
            }
          }
          updateCounts();
          renderPlaylist();
          hideModal(document.getElementById('addMusicModal'));
          addMusicForm.reset();
          if (coverPreviewBox) coverPreviewBox.style.display = 'none';
          // Auto load and play new track
          currentIndex = 0;
          loadTrack(0, true);
        } else {
          alert(data.error || 'Failed to add music track. Please check the URLs.');
        }
      } catch (err) {
        console.error('Error adding track:', err);
        alert('Network error while adding music track.');
      } finally {
        submitAddMusicBtn.disabled = false;
        submitAddMusicBtn.innerHTML = originalHtml;
      }
    });
  }

  // Initialize with tracks passed from template or fetch via API
  async function init() {
    const rawJson = document.getElementById('initialMusicJson');
    if (rawJson && rawJson.textContent.trim()) {
      try {
        tracks = JSON.parse(rawJson.textContent);
      } catch (_) {
        tracks = [];
      }
    }

    if (!tracks.length) {
      try {
        const res = await fetch(getApiUrl('list'));
        const data = await res.json();
        if (data.success && data.tracks) {
          tracks = data.tracks;
        }
      } catch (err) {
        console.warn('Could not fetch music tracks:', err);
      }
    }

    // Load local favorites if saved
    const savedFavs = getLocalFavs();
    if (savedFavs && Array.isArray(savedFavs)) {
      tracks.forEach(t => {
        t.is_favorite = savedFavs.includes(t.id);
      });
    } else {
      const initialFavIds = tracks.filter(t => t.is_favorite).map(t => t.id);
      saveLocalFavs(initialFavIds);
    }

    ensureModalsInBody();
    updateCounts();
    renderPlaylist();
    if (tracks.length > 0) {
      loadTrack(0, false);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
