/**
 * TaskNova — Nova Focus Mode (Pomodoro Timer & Session Logging)
 */

let focusTimer = {
  totalSeconds: 25 * 60,
  remainingSeconds: 25 * 60,
  intervalId: null,
  isRunning: false,
  targetTaskId: null,
  targetTaskTitle: 'General Focus Session'
};

const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * 95; // r=95 => ~596.9

// Open Nova Focus Modal
async function openFocusModal() {
  const modalEl = document.getElementById('focusModal');
  if (!modalEl) return;

  // Populate task selector with pending tasks
  const selector = document.getElementById('focusTaskSelector');
  if (selector) {
    try {
      const res = await fetch('/api/tasks?status=Pending');
      const data = await res.json();
      if (data.success) {
        selector.innerHTML = '<option value="">-- General Productivity Session --</option>';
        data.tasks.forEach(t => {
          const opt = document.createElement('option');
          opt.value = t.id;
          opt.textContent = `${t.title} (${t.priority})`;
          if (t.is_focus) opt.selected = true;
          selector.appendChild(opt);
        });
        updateFocusTargetTask();
      }
    } catch (e) {
      console.error('Failed to populate focus tasks', e);
    }
  }

  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

function startFocusWithTask(taskId, taskTitle) {
  focusTimer.targetTaskId = taskId;
  focusTimer.targetTaskTitle = taskTitle;
  
  const displayTitle = document.getElementById('focusTaskTitleDisplay');
  if (displayTitle) displayTitle.textContent = taskTitle;

  const selector = document.getElementById('focusTaskSelector');
  if (selector) selector.value = taskId;

  openFocusModal();
  setTimeout(() => {
    if (!focusTimer.isRunning) toggleFocusTimer();
  }, 400);
}

function updateFocusTargetTask() {
  const selector = document.getElementById('focusTaskSelector');
  const displayTitle = document.getElementById('focusTaskTitleDisplay');
  if (!selector || !displayTitle) return;

  const selectedOption = selector.options[selector.selectedIndex];
  if (selector.value) {
    focusTimer.targetTaskId = parseInt(selector.value);
    focusTimer.targetTaskTitle = selectedOption.textContent;
    displayTitle.textContent = selectedOption.textContent;
  } else {
    focusTimer.targetTaskId = null;
    focusTimer.targetTaskTitle = 'General Focus Session';
    displayTitle.textContent = 'General Focus Session';
  }
}

function updateTimerDisplay() {
  const digitsEl = document.getElementById('timerDigits');
  const circleEl = document.getElementById('timerProgressCircle');

  const mins = Math.floor(focusTimer.remainingSeconds / 60);
  const secs = focusTimer.remainingSeconds % 60;
  const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

  if (digitsEl) digitsEl.textContent = formatted;

  if (circleEl) {
    const fraction = (focusTimer.totalSeconds - focusTimer.remainingSeconds) / focusTimer.totalSeconds;
    const offset = CIRCLE_CIRCUMFERENCE * (1 - fraction);
    circleEl.style.strokeDashoffset = offset;
  }
}

function toggleFocusTimer() {
  const toggleBtn = document.getElementById('timerToggleBtn');

  if (focusTimer.isRunning) {
    // Pause
    clearInterval(focusTimer.intervalId);
    focusTimer.isRunning = false;
    if (toggleBtn) toggleBtn.innerHTML = '<i class="fa-solid fa-play me-2"></i> Resume';
  } else {
    // Start / Resume
    focusTimer.isRunning = true;
    if (toggleBtn) toggleBtn.innerHTML = '<i class="fa-solid fa-pause me-2"></i> Pause';

    focusTimer.intervalId = setInterval(() => {
      if (focusTimer.remainingSeconds > 0) {
        focusTimer.remainingSeconds--;
        updateTimerDisplay();
      } else {
        // Timer completed!
        clearInterval(focusTimer.intervalId);
        focusTimer.isRunning = false;
        playChimeSound();
        completeFocusSession(false);
      }
    }, 1000);
  }
}

function resetFocusTimer() {
  clearInterval(focusTimer.intervalId);
  focusTimer.isRunning = false;
  focusTimer.remainingSeconds = focusTimer.totalSeconds;
  updateTimerDisplay();

  const toggleBtn = document.getElementById('timerToggleBtn');
  if (toggleBtn) toggleBtn.innerHTML = '<i class="fa-solid fa-play me-2"></i> Start Focus';
}

async function completeFocusSession(markTaskComplete = false) {
  const durationMinutes = Math.round((focusTimer.totalSeconds - focusTimer.remainingSeconds) / 60) || 25;

  try {
    const res = await fetch('/api/focus/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        task_id: focusTimer.targetTaskId,
        task_title: focusTimer.targetTaskTitle,
        duration_minutes: durationMinutes,
        mark_task_completed: markTaskComplete
      })
    });
    const result = await res.json();
    if (result.success) {
      showToast(`🎉 Focus session logged: ${durationMinutes} minutes saved!`, 'success');
      resetFocusTimer();
      const modalInstance = bootstrap.Modal.getInstance(document.getElementById('focusModal'));
      if (modalInstance) modalInstance.hide();
      setTimeout(() => window.location.reload(), 450);
    }
  } catch (e) {
    showToast('Failed to save focus session', 'error');
  }
}

// Web Audio API Chime Synthesizer
function playChimeSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.3); // A5

    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 1.2);
  } catch (err) {
    console.log('Audio chime not supported or muted');
  }
}

// Initial circle stroke setup
document.addEventListener('DOMContentLoaded', () => {
  const circleEl = document.getElementById('timerProgressCircle');
  if (circleEl) {
    circleEl.style.strokeDasharray = CIRCLE_CIRCUMFERENCE;
    circleEl.style.strokeDashoffset = CIRCLE_CIRCUMFERENCE;
  }
});
