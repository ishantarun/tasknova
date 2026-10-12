import os
import unittest
from datetime import datetime, date, timedelta
from app import create_app
from database import get_db
from models import TaskRepository, ProjectRepository, FocusSessionRepository, SettingsRepository
from recommendations import SmartPriorityAssistant
from analytics_service import AnalyticsService

class TestTaskNova(unittest.TestCase):
    def setUp(self):
        # Configure app to use a dedicated test database
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_database_initialization(self):
        """Verify SQLite tables exist and initial seeds are present."""
        db = get_db()
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t['name'] for t in tables]
        self.assertIn('tasks', table_names)
        self.assertIn('projects', table_names)
        self.assertIn('focus_sessions', table_names)
        self.assertIn('user_settings', table_names)

    def test_task_lifecycle_crud(self):
        """Test task creation, reading, editing, and deletion."""
        # 1. Create task
        task_data = {
            'title': 'Automated Test Task 101',
            'description': 'Validating SQLite persistence and retrieval',
            'category': 'Work',
            'priority': 'Urgent',
            'status': 'Pending',
            'start_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=2)).isoformat(),
            'estimated_duration': 45,
            'is_important': 1,
            'tags': 'unit-test, automation'
        }
        task_id = TaskRepository.create(task_data)
        self.assertIsNotNone(task_id)

        # 2. Verify stored in SQLite
        task = TaskRepository.get_by_id(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task['title'], 'Automated Test Task 101')
        self.assertEqual(task['priority'], 'Urgent')
        self.assertEqual(task['is_important'], 1)

        # 3. Update task
        update_data = {
            'title': 'Automated Test Task 101 - Updated',
            'priority': 'High',
            'status': 'In Progress'
        }
        success = TaskRepository.update(task_id, update_data)
        self.assertTrue(success)
        updated_task = TaskRepository.get_by_id(task_id)
        self.assertEqual(updated_task['title'], 'Automated Test Task 101 - Updated')
        self.assertEqual(updated_task['priority'], 'High')
        self.assertEqual(updated_task['status'], 'In Progress')

        # 4. Toggle complete
        completed_task = TaskRepository.toggle_complete(task_id)
        self.assertEqual(completed_task['status'], 'Completed')
        self.assertIsNotNone(completed_task['completed_at'])

        # 5. Reopen task
        reopened_task = TaskRepository.toggle_complete(task_id)
        self.assertEqual(reopened_task['status'], 'Pending')
        self.assertIsNone(reopened_task['completed_at'])

        # 6. Delete task
        deleted = TaskRepository.delete(task_id)
        self.assertTrue(deleted)
        self.assertIsNone(TaskRepository.get_by_id(task_id))

    def test_project_safe_deletion(self):
        """Verify project deletion safely preserves tasks (foreign key nullify)."""
        # Create test project
        proj_id = ProjectRepository.create({
            'name': 'Temporary Deletion Test Project',
            'description': 'Testing cascade behavior',
            'color': '#ff0000',
            'icon': 'folder'
        })
        self.assertIsNotNone(proj_id)

        # Create task linked to this project
        task_id = TaskRepository.create({
            'title': 'Orphan Safe Task',
            'project_id': proj_id
        })
        linked_task = TaskRepository.get_by_id(task_id)
        self.assertEqual(linked_task['project_id'], proj_id)

        # Delete project
        deleted = ProjectRepository.delete(proj_id)
        self.assertTrue(deleted)

        # Check project is deleted
        self.assertIsNone(ProjectRepository.get_by_id(proj_id))

        # Check task still exists and project_id is None
        preserved_task = TaskRepository.get_by_id(task_id)
        self.assertIsNotNone(preserved_task)
        self.assertIsNone(preserved_task['project_id'])

        # Clean up
        TaskRepository.delete(task_id)

    def test_smart_priority_assistant(self):
        """Test rule-based Smart Priority Assistant evaluation."""
        sample_tasks = [
            {'id': 1, 'title': 'Routine low task', 'priority': 'Low', 'status': 'Pending', 'due_date': None},
            {'id': 2, 'title': 'Critical urgent item due today', 'priority': 'Urgent', 'status': 'Pending', 'due_date': date.today().isoformat(), 'is_important': 1}
        ]
        rec = SmartPriorityAssistant.get_recommendation(sample_tasks)
        self.assertIsNotNone(rec)
        self.assertEqual(rec['task']['id'], 2)
        self.assertIn('Urgent', rec['explanation'])

    def test_pomodoro_focus_session_logging(self):
        """Test logging Pomodoro focus session to database."""
        session_id = FocusSessionRepository.record(
            task_id=None,
            task_title="Architectural Deep Work",
            duration_minutes=25,
            notes="Completed unit test suites"
        )
        self.assertIsNotNone(session_id)
        stats = FocusSessionRepository.get_stats()
        self.assertGreater(stats['total_sessions'], 0)
        self.assertGreater(stats['total_minutes'], 0)

    def test_streaks_calculation(self):
        """Test consecutive streak calculation."""
        streaks = AnalyticsService.get_streaks()
        self.assertIn('current_streak', streaks)
        self.assertIn('best_streak', streaks)
        self.assertGreaterEqual(streaks['current_streak'], 0)

    def test_all_web_routes(self):
        """Test that all 10 requested pages return HTTP 200 OK."""
        pages = [
            '/',
            '/dashboard',
            '/tasks',
            '/today',
            '/upcoming',
            '/important',
            '/completed',
            '/projects',
            '/calendar',
            '/analytics',
            '/settings'
        ]
        for url in pages:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Page {url} failed with status {res.status_code}")

    def test_api_endpoints(self):
        """Test RESTful JSON API endpoints."""
        # 1. GET /api/tasks
        res = self.client.get('/api/tasks')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])

        # 2. GET /api/dashboard/metrics
        res = self.client.get('/api/dashboard/metrics')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])

        # 3. GET /api/analytics/charts
        res = self.client.get('/api/analytics/charts')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])

        # 4. GET /api/smart-recommendation
        res = self.client.get('/api/smart-recommendation')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])

    def test_search_filter_and_sorting(self):
        """Test search by tag, sorting by priority, and overdue calculations."""
        # Search by tag
        res = TaskRepository.get_all(search='architecture')
        self.assertGreater(len(res), 0)

        # Sort by priority
        sorted_prio = TaskRepository.get_all(sort_by='priority')
        self.assertGreater(len(sorted_prio), 0)
        # First task should be Urgent or High
        self.assertIn(sorted_prio[0]['priority'], ['Urgent', 'High'])

        # Overdue query
        overdue = TaskRepository.get_overdue_tasks()
        self.assertIsInstance(overdue, list)

        # Empty recommendation
        rec_empty = SmartPriorityAssistant.get_recommendation([])
        self.assertIsNone(rec_empty)

if __name__ == '__main__':
    unittest.main()
