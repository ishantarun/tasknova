from datetime import datetime, date
from database import get_db

class TaskRepository:
    @staticmethod
    def get_all(filters=None, sort_by=None, search=None):
        db = get_db()
        query = """
            SELECT t.*, p.name as project_name, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE 1=1
        """
        params = []
        filters = filters or {}

        if 'status' in filters and filters['status']:
            query += " AND t.status = ?"
            params.append(filters['status'])
        
        if 'priority' in filters and filters['priority']:
            query += " AND t.priority = ?"
            params.append(filters['priority'])

        if 'category' in filters and filters['category']:
            query += " AND t.category = ?"
            params.append(filters['category'])

        if 'project_id' in filters and filters['project_id']:
            query += " AND t.project_id = ?"
            params.append(filters['project_id'])

        if 'is_important' in filters and filters['is_important'] is not None:
            query += " AND t.is_important = ?"
            params.append(1 if filters['is_important'] else 0)

        if 'due_date_date' in filters and filters['due_date_date']:
            # Tasks due on a specific calendar day (prefix match on YYYY-MM-DD)
            query += " AND SUBSTR(t.due_date, 1, 10) = ?"
            params.append(filters['due_date_date'])

        if 'due_upcoming' in filters and filters['due_upcoming']:
            today_str = date.today().isoformat()
            query += " AND SUBSTR(t.due_date, 1, 10) > ? AND t.status != 'Completed'"
            params.append(today_str)

        if search:
            search_param = f"%{search.strip()}%"
            query += " AND (t.title LIKE ? OR t.description LIKE ? OR t.tags LIKE ?)"
            params.extend([search_param, search_param, search_param])

        # Sorting logic
        sort_map = {
            'due_date_asc': "t.due_date IS NULL, t.due_date ASC",
            'due_date_desc': "t.due_date DESC",
            'priority': """
                CASE t.priority 
                    WHEN 'Urgent' THEN 1 
                    WHEN 'High' THEN 2 
                    WHEN 'Medium' THEN 3 
                    WHEN 'Low' THEN 4 
                    ELSE 5 
                END ASC
            """,
            'title_asc': "t.title COLLATE NOCASE ASC",
            'title_desc': "t.title COLLATE NOCASE DESC",
            'created_at_desc': "t.created_at DESC",
            'created_at_asc': "t.created_at ASC"
        }
        order_clause = sort_map.get(sort_by, "t.is_important DESC, t.due_date IS NULL, t.due_date ASC, t.id DESC")
        query += f" ORDER BY {order_clause}"

        cursor = db.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(task_id):
        db = get_db()
        cursor = db.execute("""
            SELECT t.*, p.name as project_name, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.id = ?
        """, (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(data):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO tasks (
                title, description, category, project_id, priority, status,
                start_date, due_date, tags, estimated_duration, is_important, is_focus
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('title', '').strip(),
            data.get('description', '').strip(),
            data.get('category', 'Work'),
            data.get('project_id') or None,
            data.get('priority', 'Medium'),
            data.get('status', 'Pending'),
            data.get('start_date') or None,
            data.get('due_date') or None,
            data.get('tags', '').strip(),
            int(data.get('estimated_duration') or 30),
            1 if data.get('is_important') else 0,
            1 if data.get('is_focus') else 0
        ))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update(task_id, data):
        db = get_db()
        existing = TaskRepository.get_by_id(task_id)
        if not existing:
            return False

        # Status transition handling for completed_at
        status = data.get('status', existing['status'])
        completed_at = existing['completed_at']
        if status == 'Completed' and existing['status'] != 'Completed':
            completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif status != 'Completed' and existing['status'] == 'Completed':
            completed_at = None

        db.execute("""
            UPDATE tasks SET
                title = ?,
                description = ?,
                category = ?,
                project_id = ?,
                priority = ?,
                status = ?,
                start_date = ?,
                due_date = ?,
                tags = ?,
                estimated_duration = ?,
                is_important = ?,
                is_focus = ?,
                completed_at = ?
            WHERE id = ?
        """, (
            data.get('title', existing['title']).strip(),
            data.get('description', existing['description']).strip(),
            data.get('category', existing['category']),
            data.get('project_id', existing['project_id']) or None,
            data.get('priority', existing['priority']),
            status,
            data.get('start_date', existing['start_date']) or None,
            data.get('due_date', existing['due_date']) or None,
            data.get('tags', existing['tags']).strip(),
            int(data.get('estimated_duration', existing['estimated_duration']) or 30),
            1 if data.get('is_important', existing['is_important']) else 0,
            1 if data.get('is_focus', existing['is_focus']) else 0,
            completed_at,
            task_id
        ))
        db.commit()
        return True

    @staticmethod
    def delete(task_id):
        db = get_db()
        cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def toggle_complete(task_id):
        db = get_db()
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return None
        new_status = 'Pending' if task['status'] == 'Completed' else 'Completed'
        completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if new_status == 'Completed' else None
        # If completing, remove is_focus
        is_focus = 0 if new_status == 'Completed' else task['is_focus']

        db.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, is_focus = ?
            WHERE id = ?
        """, (new_status, completed_at, is_focus, task_id))
        db.commit()
        return TaskRepository.get_by_id(task_id)

    @staticmethod
    def toggle_important(task_id):
        db = get_db()
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return None
        new_important = 0 if task['is_important'] else 1
        db.execute("UPDATE tasks SET is_important = ? WHERE id = ?", (new_important, task_id))
        db.commit()
        return TaskRepository.get_by_id(task_id)

    @staticmethod
    def set_focus(task_id):
        db = get_db()
        # Reset previous focus
        db.execute("UPDATE tasks SET is_focus = 0")
        if task_id:
            db.execute("UPDATE tasks SET is_focus = 1 WHERE id = ?", (task_id,))
        db.commit()
        return TaskRepository.get_by_id(task_id) if task_id else None

    @staticmethod
    def get_today_tasks():
        today_str = date.today().isoformat()
        db = get_db()
        cursor = db.execute("""
            SELECT t.*, p.name as project_name, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE SUBSTR(t.due_date, 1, 10) = ?
            ORDER BY t.status = 'Completed', 
                     CASE t.priority WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END ASC,
                     t.due_date ASC
        """, (today_str,))
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_upcoming_tasks():
        today_str = date.today().isoformat()
        db = get_db()
        cursor = db.execute("""
            SELECT t.*, p.name as project_name, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE SUBSTR(t.due_date, 1, 10) > ? AND t.status != 'Completed'
            ORDER BY t.due_date ASC, t.is_important DESC
        """, (today_str,))
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_important_tasks():
        db = get_db()
        cursor = db.execute("""
            SELECT t.*, p.name as project_name, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.is_important = 1
            ORDER BY t.status = 'Completed', t.due_date IS NULL, t.due_date ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_completed_tasks():
        db = get_db()
        cursor = db.execute("""
            SELECT t.*, p.name as project_name, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status = 'Completed'
            ORDER BY t.completed_at DESC, t.id DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_overdue_tasks():
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        today_str = date.today().isoformat()
        db = get_db()
        cursor = db.execute("""
            SELECT t.*, p.name as project_name, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status != 'Completed' 
              AND t.due_date IS NOT NULL 
              AND (
                  (LENGTH(t.due_date) = 10 AND t.due_date < ?) OR
                  (LENGTH(t.due_date) > 10 AND t.due_date < ?)
              )
            ORDER BY t.due_date ASC
        """, (today_str, now_str))
        return [dict(row) for row in cursor.fetchall()]


class ProjectRepository:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.execute("SELECT * FROM projects ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(project_id):
        db = get_db()
        cursor = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(data):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO projects (name, description, color, icon)
            VALUES (?, ?, ?, ?)
        """, (
            data.get('name', '').strip(),
            data.get('description', '').strip(),
            data.get('color', '#6366f1'),
            data.get('icon', 'folder')
        ))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update(project_id, data):
        db = get_db()
        cursor = db.execute("""
            UPDATE projects SET
                name = ?,
                description = ?,
                color = ?,
                icon = ?
            WHERE id = ?
        """, (
            data.get('name', '').strip(),
            data.get('description', '').strip(),
            data.get('color', '#6366f1'),
            data.get('icon', 'folder'),
            project_id
        ))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def delete(project_id):
        db = get_db()
        # Tasks linked to this project will safely have project_id set to NULL due to ON DELETE SET NULL,
        # but let's also explicitly do it for robustness
        db.execute("UPDATE tasks SET project_id = NULL WHERE project_id = ?", (project_id,))
        cursor = db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def get_with_stats():
        db = get_db()
        cursor = db.execute("""
            SELECT 
                p.*,
                COUNT(t.id) as total_tasks,
                SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN t.status != 'Completed' THEN 1 ELSE 0 END) as pending_tasks
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            GROUP BY p.id
            ORDER BY p.name ASC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            tot = r['total_tasks'] or 0
            comp = r['completed_tasks'] or 0
            r['progress_pct'] = round((comp / tot * 100)) if tot > 0 else 0
        return rows


class FocusSessionRepository:
    @staticmethod
    def record(task_id, task_title, duration_minutes=25, notes=''):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO focus_sessions (task_id, task_title, duration_minutes, notes)
            VALUES (?, ?, ?, ?)
        """, (task_id or None, task_title, duration_minutes, notes))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_recent(limit=10):
        db = get_db()
        cursor = db.execute("""
            SELECT fs.*, t.category, t.priority
            FROM focus_sessions fs
            LEFT JOIN tasks t ON fs.task_id = t.id
            ORDER BY fs.completed_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def get_stats():
        today_str = date.today().isoformat()
        db = get_db()
        cursor = db.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                COALESCE(SUM(duration_minutes), 0) as total_minutes,
                SUM(CASE WHEN SUBSTR(completed_at, 1, 10) = ? THEN 1 ELSE 0 END) as today_sessions,
                COALESCE(SUM(CASE WHEN SUBSTR(completed_at, 1, 10) = ? THEN duration_minutes ELSE 0 END), 0) as today_minutes
            FROM focus_sessions
        """, (today_str, today_str))
        row = cursor.fetchone()
        return dict(row) if row else {
            'total_sessions': 0, 'total_minutes': 0, 'today_sessions': 0, 'today_minutes': 0
        }


class SettingsRepository:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.execute("SELECT key, value FROM user_settings")
        return {r['key']: r['value'] for r in cursor.fetchall()}

    @staticmethod
    def get(key, default=None):
        db = get_db()
        cursor = db.execute("SELECT value FROM user_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else default

    @staticmethod
    def set(key, value):
        db = get_db()
        db.execute("INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)", (key, str(value)))
        db.commit()
