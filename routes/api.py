from flask import Blueprint, request, jsonify
from models import TaskRepository, ProjectRepository, FocusSessionRepository, SettingsRepository
from analytics_service import AnalyticsService
from recommendations import SmartPriorityAssistant

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- TASKS API ---

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('priority'):
        filters['priority'] = request.args.get('priority')
    if request.args.get('category'):
        filters['category'] = request.args.get('category')
    if request.args.get('project_id'):
        filters['project_id'] = request.args.get('project_id')
    if request.args.get('important'):
        filters['is_important'] = request.args.get('important').lower() in ('true', '1')
    if request.args.get('date'):
        filters['due_date_date'] = request.args.get('date')
    if request.args.get('upcoming'):
        filters['due_upcoming'] = True

    search = request.args.get('search')
    sort_by = request.args.get('sort_by')

    tasks = TaskRepository.get_all(filters=filters, sort_by=sort_by, search=search)
    return jsonify({'success': True, 'tasks': tasks, 'count': len(tasks)})

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = TaskRepository.get_by_id(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    return jsonify({'success': True, 'task': task})

@api_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or request.form.to_dict()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'error': 'Task title is required'}), 400

    new_id = TaskRepository.create(data)
    task = TaskRepository.get_by_id(new_id)
    return jsonify({'success': True, 'message': 'Task created successfully', 'task': task}), 201

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json() or request.form.to_dict()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'error': 'Task title cannot be empty'}), 400

    updated = TaskRepository.update(task_id, data)
    if not updated:
        return jsonify({'success': False, 'error': 'Task not found or update failed'}), 404

    task = TaskRepository.get_by_id(task_id)
    return jsonify({'success': True, 'message': 'Task updated successfully', 'task': task})

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    deleted = TaskRepository.delete(task_id)
    if not deleted:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    return jsonify({'success': True, 'message': 'Task deleted successfully'})

@api_bp.route('/tasks/<int:task_id>/toggle-complete', methods=['POST'])
def toggle_complete(task_id):
    task = TaskRepository.toggle_complete(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    return jsonify({'success': True, 'task': task})

@api_bp.route('/tasks/<int:task_id>/toggle-important', methods=['POST'])
def toggle_important(task_id):
    task = TaskRepository.toggle_important(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    return jsonify({'success': True, 'task': task})

@api_bp.route('/tasks/<int:task_id>/set-focus', methods=['POST'])
def set_focus(task_id):
    task = TaskRepository.set_focus(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    return jsonify({'success': True, 'task': task})

# --- PROJECTS API ---

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    projects = ProjectRepository.get_with_stats()
    return jsonify({'success': True, 'projects': projects})

@api_bp.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json() or request.form.to_dict()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Project name is required'}), 400

    new_id = ProjectRepository.create(data)
    project = ProjectRepository.get_by_id(new_id)
    return jsonify({'success': True, 'message': 'Project created successfully', 'project': project}), 201

@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json() or request.form.to_dict()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Project name cannot be empty'}), 400

    updated = ProjectRepository.update(project_id, data)
    if not updated:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    project = ProjectRepository.get_by_id(project_id)
    return jsonify({'success': True, 'message': 'Project updated successfully', 'project': project})

@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    deleted = ProjectRepository.delete(project_id)
    if not deleted:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    return jsonify({'success': True, 'message': 'Project deleted successfully (associated tasks preserved)'})

# --- FOCUS SESSIONS API ---

@api_bp.route('/focus/session', methods=['POST'])
def record_focus_session():
    data = request.get_json() or request.form.to_dict()
    task_id = data.get('task_id')
    task_title = data.get('task_title', 'General Focus Session')
    duration = int(data.get('duration_minutes', 25))
    notes = data.get('notes', '')

    session_id = FocusSessionRepository.record(task_id, task_title, duration, notes)
    
    # If mark_completed is requested
    if data.get('mark_task_completed') and task_id:
        TaskRepository.toggle_complete(task_id)

    stats = FocusSessionRepository.get_stats()
    return jsonify({'success': True, 'session_id': session_id, 'stats': stats}), 201

@api_bp.route('/focus/stats', methods=['GET'])
def get_focus_stats():
    stats = FocusSessionRepository.get_stats()
    recent = FocusSessionRepository.get_recent(limit=5)
    return jsonify({'success': True, 'stats': stats, 'recent': recent})

# --- DASHBOARD & ANALYTICS API ---

@api_bp.route('/dashboard/metrics', methods=['GET'])
def get_metrics():
    metrics = AnalyticsService.get_dashboard_metrics()
    streaks = AnalyticsService.get_streaks()
    return jsonify({'success': True, 'metrics': metrics, 'streaks': streaks})

@api_bp.route('/analytics/charts', methods=['GET'])
def get_charts():
    charts = AnalyticsService.get_charts_data()
    return jsonify({'success': True, 'charts': charts})

@api_bp.route('/smart-recommendation', methods=['GET'])
def get_smart_recommendation():
    all_tasks = TaskRepository.get_all()
    rec = SmartPriorityAssistant.get_recommendation(all_tasks)
    return jsonify({'success': True, 'recommendation': rec})

# --- SETTINGS API ---

@api_bp.route('/settings', methods=['POST'])
def save_settings():
    data = request.get_json() or request.form.to_dict()
    for k, v in data.items():
        SettingsRepository.set(k, v)
    return jsonify({'success': True, 'message': 'Settings saved successfully'})
