/**
 * TaskNova — Tasks Management View (Filtering, Sorting, and List/Card Toggle)
 */

function switchTaskView(view) {
  const listView = document.getElementById('tasksListView');
  const cardView = document.getElementById('tasksCardView');
  const listBtn = document.getElementById('listViewBtn');
  const cardBtn = document.getElementById('cardViewBtn');

  if (view === 'card') {
    listView?.classList.add('d-none');
    cardView?.classList.remove('d-none');
    listBtn?.classList.replace('text-dark', 'text-muted');
    listBtn?.classList.remove('active');
    cardBtn?.classList.replace('text-muted', 'text-dark');
    cardBtn?.classList.add('active');
  } else {
    cardView?.classList.add('d-none');
    listView?.classList.remove('d-none');
    cardBtn?.classList.replace('text-dark', 'text-muted');
    cardBtn?.classList.remove('active');
    listBtn?.classList.replace('text-muted', 'text-dark');
    listBtn?.classList.add('active');
  }
}

function applyFilters() {
  const search = document.getElementById('taskSearchFilter').value.toLowerCase().trim();
  const status = document.getElementById('statusFilter').value;
  const priority = document.getElementById('priorityFilter').value;
  const category = document.getElementById('categoryFilter').value;
  const project = document.getElementById('projectFilter').value;

  const items = document.querySelectorAll('.task-item, .task-card-item');
  let visibleCount = 0;

  items.forEach(el => {
    const itemTitle = el.getAttribute('data-title') || '';
    const itemDesc = el.getAttribute('data-desc') || '';
    const itemStatus = el.getAttribute('data-status') || '';
    const itemPriority = el.getAttribute('data-priority') || '';
    const itemCategory = el.getAttribute('data-category') || '';
    const itemProject = el.getAttribute('data-project') || '';

    let match = true;

    if (search && !itemTitle.includes(search) && !itemDesc.includes(search)) match = false;
    if (status && itemStatus !== status) match = false;
    if (priority && itemPriority !== priority) match = false;
    if (category && itemCategory !== category) match = false;
    if (project && itemProject !== project) match = false;

    if (match) {
      el.style.display = '';
      visibleCount++;
    } else {
      el.style.display = 'none';
    }
  });

  const countEl = document.getElementById('displayedCount');
  if (countEl) countEl.textContent = Math.ceil(visibleCount / 2); // Divided by 2 since items exist in both list and card views
}

function resetAllFilters() {
  document.getElementById('taskSearchFilter').value = '';
  document.getElementById('statusFilter').value = '';
  document.getElementById('priorityFilter').value = '';
  document.getElementById('categoryFilter').value = '';
  document.getElementById('projectFilter').value = '';
  applyFilters();
}
