from datetime import datetime, date
from flask import Blueprint, render_template, request
from models import TaskRepository, ProjectRepository, FocusSessionRepository, SettingsRepository
from analytics_service import AnalyticsService
from recommendations import SmartPriorityAssistant

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_global_data():
    """Inject common stats and settings across all Jinja templates."""
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "Good morning!"
    elif hour < 17:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"

    metrics = AnalyticsService.get_dashboard_metrics()
    streaks = AnalyticsService.get_streaks()
    user_settings = SettingsRepository.get_all()
    projects = ProjectRepository.get_all()

    return {
        'greeting': greeting,
        'current_date_formatted': now.strftime('%A, %B %d, %Y'),
        'today_str': date.today().isoformat(),
        'metrics': metrics,
        'streaks': streaks,
        'user_settings': user_settings,
        'projects_list': projects
    }

@main_bp.route('/')
@main_bp.route('/dashboard')
def dashboard():
    all_tasks = TaskRepository.get_all()
    today_tasks = TaskRepository.get_today_tasks()
    today_focus = [t for t in today_tasks if t['status'] != 'Completed'][:3]
    if len(today_focus) < 3:
        # Fill with top pending tasks
        pending_other = [t for t in all_tasks if t['status'] != 'Completed' and t not in today_focus]
        today_focus.extend(pending_other[:3 - len(today_focus)])

    recommendation = SmartPriorityAssistant.get_recommendation(all_tasks)
    recent_tasks = all_tasks[:6]
    charts_data = AnalyticsService.get_charts_data()
    focus_stats = FocusSessionRepository.get_stats()

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        today_focus=today_focus,
        recommendation=recommendation,
        recent_tasks=recent_tasks,
        charts_data=charts_data,
        focus_stats=focus_stats
    )

@main_bp.route('/tasks')
def tasks():
    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')
    project_id = request.args.get('project_id')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'priority')

    filters = {}
    if status: filters['status'] = status
    if priority: filters['priority'] = priority
    if category: filters['category'] = category
    if project_id: filters['project_id'] = project_id

    tasks_list = TaskRepository.get_all(filters=filters, sort_by=sort_by, search=search)
    return render_template(
        'tasks.html',
        active_page='tasks',
        tasks=tasks_list,
        current_status=status,
        current_priority=priority,
        current_category=category,
        current_project_id=project_id,
        current_sort=sort_by,
        search_query=search or ''
    )

@main_bp.route('/today')
def today():
    today_tasks = TaskRepository.get_today_tasks()
    return render_template(
        'today.html',
        active_page='today',
        tasks=today_tasks
    )

@main_bp.route('/upcoming')
def upcoming():
    upcoming_tasks = TaskRepository.get_upcoming_tasks()
    return render_template(
        'upcoming.html',
        active_page='upcoming',
        tasks=upcoming_tasks
    )

@main_bp.route('/important')
def important():
    important_tasks = TaskRepository.get_important_tasks()
    return render_template(
        'important.html',
        active_page='important',
        tasks=important_tasks
    )

@main_bp.route('/completed')
def completed():
    completed_tasks = TaskRepository.get_completed_tasks()
    return render_template(
        'completed.html',
        active_page='completed',
        tasks=completed_tasks
    )

@main_bp.route('/projects')
def projects():
    projects_with_stats = ProjectRepository.get_with_stats()
    return render_template(
        'projects.html',
        active_page='projects',
        projects=projects_with_stats
    )

@main_bp.route('/calendar')
def calendar():
    all_tasks = TaskRepository.get_all()
    return render_template(
        'calendar.html',
        active_page='calendar',
        tasks=all_tasks
    )

@main_bp.route('/analytics')
def analytics():
    insights = AnalyticsService.get_productivity_insights()
    streaks = AnalyticsService.get_streaks()
    charts_data = AnalyticsService.get_charts_data()
    focus_stats = FocusSessionRepository.get_stats()
    recent_sessions = FocusSessionRepository.get_recent(limit=6)

    return render_template(
        'analytics.html',
        active_page='analytics',
        insights=insights,
        streaks=streaks,
        charts_data=charts_data,
        focus_stats=focus_stats,
        recent_sessions=recent_sessions
    )

@main_bp.route('/settings')
def settings():
    user_settings = SettingsRepository.get_all()
    return render_template(
        'settings.html',
        active_page='settings',
        settings=user_settings
    )
