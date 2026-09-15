// ============================================================
//  TASK TRACKER SCRIPT (ENHANCED)
//  - Pomodoro timer with sound toggle & persistent session counts
//  - Kanban board: drag-and-drop, AJAX CRUD (with Task Editing)
//  - Non-blocking toast notifications & keyboard shortcuts
// ============================================================

function initTracker() {
  const container = document.querySelector('.tracker-main');
  if (!container) return;

  // ── TOAST NOTIFICATIONS HELPER ─────────────────────────────
  function showTrackerToast(message, isSuccess = true) {
    let toast = document.getElementById('trackerToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'trackerToast';
      toast.className = 'contact-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = 'contact-toast ' + (isSuccess ? 'toast-success' : 'toast-error');
    toast.style.display = 'block';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
      toast.style.display = 'none';
    }, 4000);
  }

  // ── CSRF helper (Django standard) ────────────────────────
  function getCsrf() {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i].trim();
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    const inputToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    return inputToken || '';
  }

  // ── HTML Escape helper for XSS prevention ─────────────────
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ── API HELPERS ──────────────────────────────────────────
  async function apiPost(url, body) {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body: JSON.stringify(body),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) {
      throw new Error(data.error || `Request failed with status ${r.status}`);
    }
    return data;
  }

  async function apiPatch(url, body) {
    const r = await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body: JSON.stringify(body),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) {
      throw new Error(data.error || `Request failed with status ${r.status}`);
    }
    return data;
  }

  async function apiDelete(url) {
    const r = await fetch(url, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCsrf() },
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) {
      throw new Error(data.error || `Request failed with status ${r.status}`);
    }
    return data;
  }

  // ── COLUMN COUNT UPDATER ─────────────────────────────────
  function updateCounts() {
    ['todo', 'in_progress', 'done'].forEach(status => {
      const col = document.getElementById(`cards-${status}`);
      const countEl = document.getElementById(`count-${status}`);
      if (col && countEl) countEl.textContent = col.querySelectorAll('.kanban-card').length;
    });
  }

  // ── CREATE CARD ELEMENT ──────────────────────────────────
  function createCardEl(task) {
    const priorityLabels = { low: 'Low', medium: 'Medium', high: 'High' };
    const priorityClass = `priority-${task.priority || 'medium'}`;

    const card = document.createElement('div');
    card.className = 'kanban-card' + (task.status === 'done' ? ' card-done' : '');
    card.dataset.taskId = task.id;
    card.dataset.status = task.status;
    card.dataset.priority = task.priority || 'medium';
    card.dataset.description = task.description || '';
    card.dataset.dueDate = task.due_date || '';
    card.draggable = true;

    let moveButtons = '';
    if (task.status === 'todo') {
      moveButtons = `
        <button class="card-edit-btn" data-task-id="${task.id}" title="Edit Task"><ion-icon name="create-outline"></ion-icon></button>
        <button class="card-move-btn" data-task-id="${task.id}" data-move="in_progress" title="Move to In Progress"><ion-icon name="arrow-forward-outline"></ion-icon></button>`;
    } else if (task.status === 'in_progress') {
      moveButtons = `
        <button class="card-edit-btn" data-task-id="${task.id}" title="Edit Task"><ion-icon name="create-outline"></ion-icon></button>
        <button class="card-move-btn" data-task-id="${task.id}" data-move="todo" title="Move Back"><ion-icon name="arrow-back-outline"></ion-icon></button>
        <button class="card-move-btn" data-task-id="${task.id}" data-move="done" title="Mark Done"><ion-icon name="checkmark-outline"></ion-icon></button>`;
    } else {
      moveButtons = `
        <button class="card-edit-btn" data-task-id="${task.id}" title="Edit Task"><ion-icon name="create-outline"></ion-icon></button>
        <button class="card-move-btn" data-task-id="${task.id}" data-move="in_progress" title="Reopen"><ion-icon name="refresh-outline"></ion-icon></button>`;
    }

    const escapedTitle = escapeHtml(task.title);
    let descHtml = '';
    if (task.description) {
      const words = task.description.split(' ');
      const truncated = words.slice(0, 15).join(' ') + (words.length > 15 ? '…' : '');
      descHtml = `<p class="card-desc">${escapeHtml(truncated)}</p>`;
    }

    card.innerHTML = `
      <div class="card-priority ${priorityClass}">${priorityLabels[task.priority] || task.priority}</div>
      <h4 class="card-title">${escapedTitle}</h4>
      ${descHtml}
      ${task.due_date ? `<span class="card-due"><ion-icon name="calendar-outline"></ion-icon> ${escapeHtml(task.due_date)}</span>` : ''}
      <div class="card-actions">
        ${moveButtons}
        <button class="card-delete-btn" data-task-id="${task.id}" title="Delete"><ion-icon name="trash-outline"></ion-icon></button>
      </div>`;

    attachCardEvents(card);
    return card;
  }

  // ── ATTACH EVENTS TO CARD ─────────────────────────────────
  function attachCardEvents(card) {
    if (card.dataset.hasEvents) return;
    card.dataset.hasEvents = 'true';

    // Edit button
    card.querySelector('.card-edit-btn')?.addEventListener('click', (e) => {
      e.stopPropagation();
      const data = getCardData(card);
      openEditModal(data);
    });

    // Move buttons
    card.querySelectorAll('.card-move-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = btn.dataset.taskId;
        const newStatus = btn.dataset.move;
        try {
          const result = await apiPatch(`/tasks/api/tasks/${id}/update/`, { status: newStatus });
          if (result.id) {
            card.remove();
            const newCard = createCardEl(result);
            const col = document.getElementById(`cards-${newStatus}`);
            if (col) col.prepend(newCard);
            updateCounts();
            showTrackerToast(`Task moved to ${newStatus.replace('_', ' ')}!`, true);
          }
        } catch (err) {
          showTrackerToast(err.message, false);
        }
      });
    });

    // Delete button
    card.querySelector('.card-delete-btn')?.addEventListener('click', async (e) => {
      e.stopPropagation();
      const id = card.dataset.taskId;
      if (!confirm('Delete this task?')) return;
      try {
        const result = await apiDelete(`/tasks/api/tasks/${id}/delete/`);
        if (result.success) {
          card.remove();
          updateCounts();
          showTrackerToast("Task deleted successfully.", true);
        }
      } catch (err) {
        showTrackerToast(err.message, false);
      }
    });

    // Drag events
    card.addEventListener('dragstart', e => {
      e.dataTransfer.setData('taskId', card.dataset.taskId);
      e.dataTransfer.setData('currentStatus', card.dataset.status);
      setTimeout(() => card.classList.add('dragging'), 0);
    });
    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      document.querySelectorAll('.kanban-column').forEach(col => col.classList.remove('drag-over'));
    });
  }

  function getCardData(card) {
    return {
      id: card.dataset.taskId,
      title: card.querySelector('.card-title')?.textContent || '',
      description: card.dataset.description || '',
      priority: card.dataset.priority || 'medium',
      status: card.dataset.status,
      due_date: card.dataset.dueDate || '',
    };
  }

  // ── DRAG-AND-DROP COLUMNS ─────────────────────────────────
  document.querySelectorAll('.kanban-column').forEach(col => {
    if (col.dataset.hasDropListener) return;
    col.dataset.hasDropListener = 'true';

    let dragCounter = 0;

    col.addEventListener('dragenter', e => {
      e.preventDefault();
      dragCounter++;
      col.classList.add('drag-over');
    });

    col.addEventListener('dragover', e => {
      e.preventDefault();
    });

    col.addEventListener('dragleave', () => {
      dragCounter--;
      if (dragCounter <= 0) {
        dragCounter = 0;
        col.classList.remove('drag-over');
      }
    });

    col.addEventListener('drop', async e => {
      e.preventDefault();
      dragCounter = 0;
      col.classList.remove('drag-over');

      const taskId = e.dataTransfer.getData('taskId');
      const newStatus = col.dataset.status;
      const card = document.querySelector(`.kanban-card[data-task-id="${taskId}"]`);
      if (!card || card.dataset.status === newStatus) return;

      try {
        const result = await apiPatch(`/tasks/api/tasks/${taskId}/update/`, { status: newStatus });
        if (result.id) {
          card.remove();
          const newCard = createCardEl(result);
          const cardsDiv = col.querySelector('.kanban-cards');
          if (cardsDiv) cardsDiv.prepend(newCard);
          updateCounts();
          showTrackerToast(`Task moved to ${newStatus.replace('_', ' ')}!`, true);
        }
      } catch (err) {
        showTrackerToast(err.message, false);
      }
    });
  });

  // Attach events to pre-rendered server-side cards
  document.querySelectorAll('.kanban-card').forEach(card => attachCardEvents(card));

  // ── ADD/EDIT TASK MODAL ───────────────────────────────────
  const modal     = document.getElementById('taskModal');
  const addBtn    = document.getElementById('addTaskBtn');
  const closeBtn  = document.getElementById('modalClose');
  const form      = document.getElementById('addTaskForm');

  if (addBtn && !addBtn.dataset.hasListener) {
    addBtn.addEventListener('click', () => {
      const modalTitle = document.getElementById('modalTitle');
      const modalSubmitIcon = document.getElementById('modalSubmitIcon');
      const modalSubmitText = document.getElementById('modalSubmitText');

      if (modalTitle) modalTitle.textContent = "Add New Task";
      if (modalSubmitText) modalSubmitText.textContent = "Add Task";
      if (modalSubmitIcon) modalSubmitIcon.setAttribute('name', 'add-outline');

      form.reset();
      form.dataset.mode = 'add';
      form.dataset.taskId = '';

      modal.classList.add('active');
      setTimeout(() => form.taskTitle?.focus(), 100);
    });
    addBtn.dataset.hasListener = 'true';
  }

  if (closeBtn && !closeBtn.dataset.hasListener) {
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    closeBtn.dataset.hasListener = 'true';
  }

  if (modal && !modal.dataset.hasClickListener) {
    modal.addEventListener('click', e => { if (e.target === modal) modal.classList.remove('active'); });
    modal.dataset.hasClickListener = 'true';
  }

  // Keyboard shortcut to close modal
  if (!window._hasModalKeyHandler) {
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        const activeModal = document.getElementById('taskModal');
        if (activeModal && activeModal.classList.contains('active')) {
          activeModal.classList.remove('active');
        }
      }
    });
    window._hasModalKeyHandler = true;
  }

  function openEditModal(task) {
    modal.classList.add('active');

    const modalTitle = document.getElementById('modalTitle');
    const modalSubmitIcon = document.getElementById('modalSubmitIcon');
    const modalSubmitText = document.getElementById('modalSubmitText');

    if (modalTitle) modalTitle.textContent = "Edit Task";
    if (modalSubmitText) modalSubmitText.textContent = "Save Changes";
    if (modalSubmitIcon) modalSubmitIcon.setAttribute('name', 'save-outline');

    form.taskTitle.value = task.title;
    form.taskDesc.value = task.description;
    form.taskPriority.value = task.priority;
    form.taskStatus.value = task.status;
    form.taskDueDate.value = task.due_date || '';

    form.dataset.mode = 'edit';
    form.dataset.taskId = task.id;
    setTimeout(() => form.taskTitle?.focus(), 100);
  }

  if (form && !form.dataset.hasSubmitListener) {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const mode = form.dataset.mode;
      const taskId = form.dataset.taskId;

      const data = {
        title: form.taskTitle.value.trim(),
        description: form.taskDesc.value.trim(),
        priority: form.taskPriority.value,
        status: form.taskStatus.value,
        due_date: form.taskDueDate.value || null,
      };
      if (!data.title) return;

      const submitBtn = document.getElementById('modalSubmitBtn');
      if (submitBtn) submitBtn.disabled = true;

      try {
        if (mode === 'add') {
          const result = await apiPost('/tasks/api/tasks/create/', data);
          if (result.id) {
            const newCard = createCardEl(result);
            const col = document.getElementById(`cards-${result.status}`);
            if (col) col.prepend(newCard);
            updateCounts();
            form.reset();
            modal.classList.remove('active');
            showTrackerToast("Task created successfully!", true);
          }
        } else if (mode === 'edit') {
          const result = await apiPatch(`/tasks/api/tasks/${taskId}/update/`, data);
          if (result.id) {
            const oldCard = document.querySelector(`.kanban-card[data-task-id="${taskId}"]`);
            if (oldCard) oldCard.remove();

            const newCard = createCardEl(result);
            const col = document.getElementById(`cards-${result.status}`);
            if (col) col.prepend(newCard);

            updateCounts();
            form.reset();
            modal.classList.remove('active');
            showTrackerToast("Task updated successfully!", true);
          }
        }
      } catch (err) {
        showTrackerToast(err.message, false);
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
    form.dataset.hasSubmitListener = 'true';
  }

  // ═══════════════════════════════════════════════════════════
  //  POMODORO TIMER
  // ═══════════════════════════════════════════════════════════
  const CIRCUMFERENCE = 2 * Math.PI * 90; // r=90

  let totalSeconds = 25 * 60;
  let remainingSeconds = totalSeconds;
  let timerInterval = null;
  let sessionCount = parseInt(localStorage.getItem('pomo-session-count') || '0', 10);
  let isRunning = false;
  let audioCtx = null;
  let soundEnabled = localStorage.getItem('pomo-sound') !== 'false';

  function initAudio() {
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
    } catch (e) { /* Web Audio not supported */ }
  }

  const ring           = document.getElementById('timerRing');
  const minDisplay     = document.getElementById('timerMinutes');
  const secDisplay     = document.getElementById('timerSeconds');
  const btnStart       = document.getElementById('pomoBtnStart');
  const btnPause       = document.getElementById('pomoBtnPause');
  const btnReset       = document.getElementById('pomoBtnReset');
  const sessionCountEl = document.getElementById('pomoSessionCount');
  const modeButtons    = document.querySelectorAll('[data-pomo-mode]');

  if (sessionCountEl) sessionCountEl.textContent = sessionCount;
  if (ring) ring.style.strokeDasharray = CIRCUMFERENCE;

  function updateTimerDisplay() {
    const m = Math.floor(remainingSeconds / 60);
    const s = remainingSeconds % 60;
    if (minDisplay) minDisplay.textContent = String(m).padStart(2, '0');
    if (secDisplay) secDisplay.textContent = String(s).padStart(2, '0');

    const progress = totalSeconds > 0 ? remainingSeconds / totalSeconds : 1;
    if (ring) ring.style.strokeDashoffset = CIRCUMFERENCE * (1 - progress);
  }

  function startTimer() {
    if (isRunning) return;
    isRunning = true;
    if (btnStart) btnStart.disabled = true;
    if (btnPause) btnPause.disabled = false;

    timerInterval = setInterval(() => {
      if (remainingSeconds <= 0) {
        clearInterval(timerInterval);
        isRunning = false;
        sessionCount++;
        localStorage.setItem('pomo-session-count', String(sessionCount));
        if (sessionCountEl) sessionCountEl.textContent = sessionCount;
        if (btnStart) btnStart.disabled = false;
        if (btnPause) btnPause.disabled = true;
        
        playBeep();
        showTrackerToast("🎉 Pomodoro session complete! Great work!", true);

        remainingSeconds = totalSeconds;
        updateTimerDisplay();
        return;
      }
      remainingSeconds--;
      updateTimerDisplay();
    }, 1000);
  }

  function pauseTimer() {
    clearInterval(timerInterval);
    isRunning = false;
    if (btnStart) btnStart.disabled = false;
    if (btnPause) btnPause.disabled = true;
  }

  function resetTimer() {
    clearInterval(timerInterval);
    isRunning = false;
    remainingSeconds = totalSeconds;
    updateTimerDisplay();
    if (btnStart) btnStart.disabled = false;
    if (btnPause) btnPause.disabled = true;
  }

  function setMode(minutes) {
    totalSeconds = minutes * 60;
    remainingSeconds = totalSeconds;
    resetTimer();
  }

  if (btnStart && !btnStart.dataset.hasListener) {
    btnStart.addEventListener('click', () => {
      initAudio();
      startTimer();
    });
    btnStart.dataset.hasListener = 'true';
  }

  if (btnPause && !btnPause.dataset.hasListener) {
    btnPause.addEventListener('click', pauseTimer);
    btnPause.dataset.hasListener = 'true';
  }

  if (btnReset && !btnReset.dataset.hasListener) {
    btnReset.addEventListener('click', resetTimer);
    btnReset.dataset.hasListener = 'true';
  }

  modeButtons.forEach(btn => {
    if (btn.dataset.hasListener) return;
    btn.addEventListener('click', () => {
      modeButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      setMode(parseInt(btn.dataset.minutes, 10));
    });
    btn.dataset.hasListener = 'true';
  });

  updateTimerDisplay();

  function playBeep() {
    if (!soundEnabled) return;
    try {
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.type = 'sine';
      osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 1.2);
      osc.start(audioCtx.currentTime);
      osc.stop(audioCtx.currentTime + 1.2);
    } catch (e) { /* Audio not supported */ }
  }
}

// Expose globally for PJAX router reinitialization
window.initTracker = initTracker;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTracker);
} else {
  initTracker();
}
