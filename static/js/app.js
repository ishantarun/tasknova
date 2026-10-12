/**
 * TaskNova — Core Client Application JavaScript
 * Global modal management, API actions, and UI transitions
 */

// Global delete target tracker
let deleteTarget = { type: null, id: null };

// Sidebar Toggle
function toggleSidebar() {
  const sidebar = document.getElementById('appSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (sidebar && overlay) {
    sidebar.classList.toggle('show');
    overlay.classList.toggle('show');
  }
}

// Global Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `nova-toast ${type}`;
  
  let icon = 'circle-info';
  if (type === 'success') icon = 'circle-check';
  if (type === 'error') icon = 'triangle-exclamation';

  toast.innerHTML = `
    <i class="fa-solid fa-${icon} fs-5"></i>
    <div class="flex-grow-1">${message}</div>
    <button class="btn-close btn-close-white btn-sm" onclick="this.parentElement.remove()"></button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(60px)';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// Global Search (Ctrl + K or header enter)
function handleGlobalSearch(event) {
  if (event.key === 'Enter') {
    const query = event.target.value.trim();
    window.location.href = `/tasks?search=${encodeURIComponent(query)}`;
  }
}

document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    const searchInput = document.getElementById('globalSearchInput');
    if (searchInput) searchInput.focus();
  }
});

// Quick Capture Handler
async function handleQuickCapture(e) {
  e.preventDefault();
  const input = document.getElementById('quickCaptureInput');
  const prioritySelect = document.getElementById('quickCapturePriority');
  const title = input.value.trim();
  if (!title) return;

  const priority = prioritySelect ? prioritySelect.value : 'Medium';

  try {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        priority: priority,
        status: 'Pending',
        category: 'Work'
      })
    });
    const result = await res.json();
    if (result.success) {
      showToast(`Task "${title}" created!`, 'success');
      input.value = '';
      setTimeout(() => window.location.reload(), 400);
    } else {
      showToast(result.error || 'Failed to add task', 'error');
    }
  } catch (err) {
    showToast('Network error adding task', 'error');
  }
}

// Task Modal Opening & Population
function openTaskModal(data = null) {
  const form = document.getElementById('taskForm');
  form.reset();

  const titleEl = document.getElementById('taskModalTitleText');
  const idEl = document.getElementById('taskId');

  if (data) {
    titleEl.textContent = 'Edit Task';
    idEl.value = data.id;
    document.getElementById('taskTitle').value = data.title || '';
    document.getElementById('taskDescription').value = data.description || '';
    document.getElementById('taskCategory').value = data.category || 'Work';
    document.getElementById('taskProjectId').value = data.project_id || '';
    document.getElementById('taskPriority').value = data.priority || 'Medium';
    document.getElementById('taskStatus').value = data.status || 'Pending';
    document.getElementById('taskStartDate').value = data.start_date || '';
    document.getElementById('taskDueDate').value = data.due_date || '';
    document.getElementById('taskEstDuration').value = data.estimated_duration || 30;
    document.getElementById('taskTags').value = data.tags || '';
    document.getElementById('taskIsImportant').checked = !!data.is_important;
  } else {
    titleEl.textContent = 'Create New Task';
    idEl.value = '';
  }

  const modal = new bootstrap.Modal(document.getElementById('taskModal'));
  modal.show();
}

function openTaskModalWithTodayDate() {
  openTaskModal();
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('taskStartDate').value = today;
  document.getElementById('taskDueDate').value = `${today}T18:00`;
}

function openTaskModalWithStar() {
  openTaskModal();
  document.getElementById('taskIsImportant').checked = true;
}

async function openEditTaskModal(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}`);
    const data = await res.json();
    if (data.success) {
      openTaskModal(data.task);
    } else {
      showToast('Could not fetch task details', 'error');
    }
  } catch (err) {
    showToast('Failed to load task', 'error');
  }
}

// Task Form Submit (Create or Update)
async function handleTaskFormSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const taskId = document.getElementById('taskId').value;
  const isEdit = !!taskId;

  const data = {
    title: document.getElementById('taskTitle').value.trim(),
    description: document.getElementById('taskDescription').value.trim(),
    category: document.getElementById('taskCategory').value,
    project_id: document.getElementById('taskProjectId').value || null,
    priority: document.getElementById('taskPriority').value,
    status: document.getElementById('taskStatus').value,
    start_date: document.getElementById('taskStartDate').value || null,
    due_date: document.getElementById('taskDueDate').value || null,
    estimated_duration: parseInt(document.getElementById('taskEstDuration').value) || 30,
    tags: document.getElementById('taskTags').value.trim(),
    is_important: document.getElementById('taskIsImportant').checked ? 1 : 0
  };

  const url = isEdit ? `/api/tasks/${taskId}` : '/api/tasks';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();

    if (result.success) {
      const modalInstance = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
      if (modalInstance) modalInstance.hide();
      showToast(result.message || 'Saved successfully!', 'success');
      setTimeout(() => window.location.reload(), 400);
    } else {
      showToast(result.error || 'Submission failed', 'error');
    }
  } catch (err) {
    showToast('Error saving task', 'error');
  }
}

// Toggle Complete
async function toggleTaskComplete(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/toggle-complete`, { method: 'POST' });
    const result = await res.json();
    if (result.success) {
      const task = result.task;
      showToast(task.status === 'Completed' ? 'Task marked complete! Streak updated.' : 'Task reopened', 'success');
      setTimeout(() => window.location.reload(), 450);
    }
  } catch (err) {
    showToast('Failed to update task status', 'error');
  }
}

// Toggle Important
async function toggleTaskImportant(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/toggle-important`, { method: 'POST' });
    const result = await res.json();
    if (result.success) {
      showToast(result.task.is_important ? 'Task marked as Important!' : 'Removed from Important', 'info');
      setTimeout(() => window.location.reload(), 300);
    }
  } catch (err) {
    showToast('Failed to toggle star', 'error');
  }
}

// Delete Confirmation
function confirmDeleteTask(taskId, taskTitle) {
  deleteTarget = { type: 'task', id: taskId };
  document.getElementById('deleteModalTitle').textContent = 'Delete Task?';
  document.getElementById('deleteModalMessage').textContent = `Are you sure you want to delete "${taskTitle}"?`;
  const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
  modal.show();
}

function confirmDeleteProject(projectId, projectName) {
  deleteTarget = { type: 'project', id: projectId };
  document.getElementById('deleteModalTitle').textContent = 'Delete Project?';
  document.getElementById('deleteModalMessage').textContent = `Delete project "${projectName}"? Associated tasks will be preserved safely.`;
  const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
  modal.show();
}

document.getElementById('confirmDeleteBtn')?.addEventListener('click', async () => {
  if (!deleteTarget.type || !deleteTarget.id) return;

  const modalInstance = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal'));
  if (modalInstance) modalInstance.hide();

  const url = deleteTarget.type === 'task' ? `/api/tasks/${deleteTarget.id}` : `/api/projects/${deleteTarget.id}`;

  try {
    const res = await fetch(url, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) {
      showToast(result.message || 'Deleted successfully', 'success');
      setTimeout(() => window.location.reload(), 350);
    } else {
      showToast(result.error || 'Failed to delete', 'error');
    }
  } catch (err) {
    showToast('Error during deletion', 'error');
  }
});

// Projects Management
function openProjectModal(data = null) {
  const form = document.getElementById('projectForm');
  form.reset();

  const titleEl = document.getElementById('projectModalTitleText');
  const idEl = document.getElementById('projectId');

  if (data) {
    titleEl.textContent = 'Edit Project';
    idEl.value = data.id;
    document.getElementById('projectName').value = data.name || '';
    document.getElementById('projectDescription').value = data.description || '';
    document.getElementById('projectColor').value = data.color || '#6366f1';
    document.getElementById('projectIcon').value = data.icon || 'folder';
  } else {
    titleEl.textContent = 'Create Project';
    idEl.value = '';
  }

  const modal = new bootstrap.Modal(document.getElementById('projectModal'));
  modal.show();
}

function openEditProjectModal(id, name, desc, color, icon) {
  openProjectModal({ id, name, description: desc, color, icon });
}

async function handleProjectFormSubmit(e) {
  e.preventDefault();
  const projectId = document.getElementById('projectId').value;
  const isEdit = !!projectId;

  const data = {
    name: document.getElementById('projectName').value.trim(),
    description: document.getElementById('projectDescription').value.trim(),
    color: document.getElementById('projectColor').value,
    icon: document.getElementById('projectIcon').value
  };

  const url = isEdit ? `/api/projects/${projectId}` : '/api/projects';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.success) {
      const modalInstance = bootstrap.Modal.getInstance(document.getElementById('projectModal'));
      if (modalInstance) modalInstance.hide();
      showToast(result.message || 'Project saved!', 'success');
      setTimeout(() => window.location.reload(), 400);
    } else {
      showToast(result.error || 'Failed to save project', 'error');
    }
  } catch (err) {
    showToast('Error saving project', 'error');
  }
}
