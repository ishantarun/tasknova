/**
 * TaskNova — Interactive Task Calendar
 */

let currentCalDate = new Date();
let selectedCalDate = new Date();

document.addEventListener('DOMContentLoaded', () => {
  renderCalendar();
  selectDate(selectedCalDate);
});

function navCalendar(action) {
  if (action === 'prev') {
    currentCalDate.setMonth(currentCalDate.getMonth() - 1);
  } else if (action === 'next') {
    currentCalDate.setMonth(currentCalDate.getMonth() + 1);
  } else if (action === 'today') {
    currentCalDate = new Date();
    selectedCalDate = new Date();
  }
  renderCalendar();
}

function renderCalendar() {
  const year = currentCalDate.getFullYear();
  const month = currentCalDate.getMonth();

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  document.getElementById('calendarMonthTitle').textContent = `${monthNames[month]} ${year}`;

  const grid = document.getElementById('calendarDaysGrid');
  if (!grid) return;
  grid.innerHTML = '';

  const firstDayIndex = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const todayStr = new Date().toISOString().split('T')[0];
  const allTasks = window.allTasksData || [];

  // Group tasks by date string YYYY-MM-DD
  const tasksByDate = {};
  allTasks.forEach(t => {
    if (t.due_date) {
      const dStr = t.due_date.substring(0, 10);
      if (!tasksByDate[dStr]) tasksByDate[dStr] = [];
      tasksByDate[dStr].push(t);
    }
  });

  // Previous month trailing days
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const dayNum = daysInPrevMonth - i;
    const cell = document.createElement('div');
    cell.className = 'calendar-day-cell other-month';
    cell.innerHTML = `<span class="calendar-day-number">${dayNum}</span>`;
    grid.appendChild(cell);
  }

  // Current month days
  for (let day = 1; day <= daysInMonth; day++) {
    const dObj = new Date(year, month, day);
    const dStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const isToday = dStr === todayStr;

    const cell = document.createElement('div');
    cell.className = `calendar-day-cell ${isToday ? 'is-today' : ''}`;
    cell.onclick = () => selectDate(dObj);

    let tasksHtml = '';
    const dayTasks = tasksByDate[dStr] || [];
    if (dayTasks.length > 0) {
      tasksHtml = '<div class="calendar-task-dot-list">';
      dayTasks.slice(0, 2).forEach(t => {
        tasksHtml += `<div class="calendar-task-chip" title="${t.title}">${t.title}</div>`;
      });
      if (dayTasks.length > 2) {
        tasksHtml += `<div class="text-muted" style="font-size: 0.65rem; font-weight:600;">+${dayTasks.length - 2} more</div>`;
      }
      tasksHtml += '</div>';
    }

    cell.innerHTML = `
      <span class="calendar-day-number">${day}</span>
      ${tasksHtml}
    `;
    grid.appendChild(cell);
  }
}

function selectDate(dateObj) {
  selectedCalDate = dateObj;
  const year = dateObj.getFullYear();
  const month = dateObj.getMonth();
  const day = dateObj.getDate();
  const dStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  const options = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
  document.getElementById('selectedDateTitle').textContent = dateObj.toLocaleDateString(undefined, options);

  const allTasks = window.allTasksData || [];
  const dayTasks = allTasks.filter(t => t.due_date && t.due_date.substring(0, 10) === dStr);

  const container = document.getElementById('selectedDateTasksList');
  if (!container) return;
  container.innerHTML = '';

  if (dayTasks.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4 text-muted small">
        <i class="fa-regular fa-calendar-check fs-3 mb-2 d-block"></i>
        No tasks scheduled for this date.
      </div>
    `;
    return;
  }

  dayTasks.forEach(task => {
    const item = document.createElement('div');
    item.className = `task-item p-2 mb-1 ${task.status === 'Completed' ? 'is-completed' : ''}`;
    item.innerHTML = `
      <div class="task-left">
        <button class="custom-checkbox-btn ${task.status === 'Completed' ? 'checked' : ''}" onclick="toggleTaskComplete(${task.id})">
          <i class="fa-solid fa-check fa-xs"></i>
        </button>
        <div class="task-info-block">
          <span class="task-title" style="font-size: 0.88rem;">${task.title}</span>
          <div class="task-meta-row">
            <span class="task-badge ${task.priority.toLowerCase()}">${task.priority}</span>
            <span class="task-project-pill">${task.category}</span>
          </div>
        </div>
      </div>
      <div class="task-right">
        <button class="action-icon-btn" onclick="startFocusWithTask(${task.id}, '${task.title.replace(/'/g, "\\'")}')" title="Focus">
          <i class="fa-solid fa-stopwatch text-primary fa-xs"></i>
        </button>
      </div>
    `;
    container.appendChild(item);
  });
}

function openTaskModalForSelectedDate() {
  openTaskModal();
  const year = selectedCalDate.getFullYear();
  const month = selectedCalDate.getMonth();
  const day = selectedCalDate.getDate();
  const dStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  document.getElementById('taskDueDate').value = `${dStr}T17:00`;
}
