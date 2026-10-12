import sqlite3
import os
from datetime import datetime, timedelta
from flask import g, current_app

def get_db():
    """Get or create SQLite connection for the current application context."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        # Ensure instance directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app=None):
    """Create database tables and seed initial data if needed."""
    def _execute_init(db):
        cursor = db.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#6366f1',
                icon TEXT DEFAULT 'folder',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'Work',
                project_id INTEGER,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Pending',
                start_date TEXT,
                due_date TEXT,
                tags TEXT,
                estimated_duration INTEGER DEFAULT 30,
                is_important INTEGER DEFAULT 0,
                is_focus INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            );
        """)

        # Focus Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                task_title TEXT NOT NULL,
                duration_minutes INTEGER DEFAULT 25,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
            );
        """)

        # User Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)

        # Check if seeding is required
        cursor.execute("SELECT COUNT(*) as count FROM projects")
        if cursor.fetchone()['count'] == 0:
            _seed_initial_data(cursor)

        db.commit()

    if app:
        with app.app_context():
            db = get_db()
            _execute_init(db)
    else:
        db = get_db()
        _execute_init(db)

def _seed_initial_data(cursor):
    """Seed initial projects and realistic tasks so the application feels alive on launch."""
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    today_evening = f"{today_str}T18:00"
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    two_days_ago = (now - timedelta(days=2)).strftime('%Y-%m-%d')
    three_days_ago = (now - timedelta(days=3)).strftime('%Y-%m-%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    next_week = (now + timedelta(days=5)).strftime('%Y-%m-%d')
    past_due = (now - timedelta(days=1)).strftime('%Y-%m-%d') + "T10:00"

    # Seed projects
    projects = [
        ("TaskNova Redesign", "Full overhaul of the design system, micro-interactions, and analytics.", "#6366f1", "palette"),
        ("Cloud Infrastructure", "Zero-downtime scaling, database optimizations, and telemetry.", "#0284c7", "server"),
        ("Personal Growth", "Health, learning routines, reading goals, and habit building.", "#10b981", "heart")
    ]
    cursor.executemany(
        "INSERT INTO projects (name, description, color, icon) VALUES (?, ?, ?, ?)",
        projects
    )

    # Seed initial tasks
    sample_tasks = [
        # (title, description, category, project_id, priority, status, start_date, due_date, tags, est_dur, is_imp, is_focus, completed_at)
        ("Finalize Q4 Architecture Review", "Review microservice boundaries, caching strategy, and latency targets with the team.", "Work", 2, "Urgent", "Pending", today_str, past_due, "architecture,team", 45, 1, 1, None),
        ("Implement Dark Mode Accent Controls", "Add theme palette picker and verify CSS custom property inheritance across cards.", "Work", 1, "High", "In Progress", today_str, today_evening, "ui,css", 30, 1, 0, None),
        ("Daily 30-Minute Cardio Session", "Morning interval run or cycling session to maintain focus and energy.", "Health", 3, "Medium", "Completed", today_str, f"{today_str}T08:00", "fitness,routine", 30, 0, 0, now.strftime('%Y-%m-%d %H:%M:%S')),
        ("Audit SQLite Indexes & Query Plans", "Analyze EXPLAIN QUERY PLAN on task filtering by status and date proximity.", "Work", 2, "High", "Pending", today_str, f"{tomorrow}T17:00", "database,perf", 40, 1, 0, None),
        ("Read 2 Chapters of 'Designing Data-Intensive Apps'", "Focus on consensus algorithms, replication logs, and linearizability.", "Study", 3, "Medium", "Pending", today_str, f"{tomorrow}T21:00", "reading,study", 60, 0, 0, None),
        ("Refactor Sidebar Navigation Drawer", "Ensure seamless transition from desktop collapsible to mobile overlay with smooth backdrop.", "Work", 1, "Medium", "Completed", yesterday, f"{yesterday}T16:00", "frontend,mobile", 35, 0, 0, f"{yesterday} 16:30:00"),
        ("Grocery Restock & Meal Prep", "Organic produce, protein snacks, and cold brew coffee prep for the week.", "Personal", 3, "Low", "Completed", two_days_ago, f"{two_days_ago}T19:00", "errands,home", 45, 0, 0, f"{two_days_ago} 18:45:00"),
        ("Draft Sprint Retrospective Deck", "Collect team wins, bottlenecks, and action items for next sprint kickoff.", "Work", 1, "Medium", "Completed", three_days_ago, f"{three_days_ago}T15:00", "agile,docs", 25, 0, 0, f"{three_days_ago} 14:50:00"),
        ("Prepare Product Demo for Stakeholders", "Create end-to-end walkthrough video featuring Nova Focus mode and productivity insights.", "Work", 1, "Urgent", "Pending", tomorrow, f"{next_week}T11:00", "demo,exec", 60, 1, 0, None),
        ("Review Weekly Budget & Investments", "Reconcile account statements and check recurring subscription expenses.", "Personal", 3, "Low", "Pending", today_str, f"{next_week}T20:00", "finance", 20, 0, 0, None)
    ]

    for t in sample_tasks:
        cursor.execute("""
            INSERT INTO tasks (
                title, description, category, project_id, priority, status,
                start_date, due_date, tags, estimated_duration, is_important, is_focus,
                created_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        """, (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11], t[12]))

    # Seed focus sessions for streak & history
    focus_sessions = [
        (3, "Daily 30-Minute Cardio Session", 25, f"{today_str} 08:35:00", "Felt great, completed warm-up and sprints."),
        (6, "Refactor Sidebar Navigation Drawer", 25, f"{yesterday} 16:15:00", "Completed responsive breakpoints."),
        (7, "Grocery Restock & Meal Prep", 25, f"{two_days_ago} 18:30:00", "Finished all meal containers."),
        (8, "Draft Sprint Retrospective Deck", 25, f"{three_days_ago} 14:40:00", "Added charts and retro notes.")
    ]
    for fs in focus_sessions:
        cursor.execute("""
            INSERT INTO focus_sessions (task_id, task_title, duration_minutes, completed_at, notes)
            VALUES (?, ?, ?, ?, ?)
        """, fs)

    # Seed user settings
    default_settings = [
        ("user_name", "Alex Hunter"),
        ("user_role", "Senior Product Architect"),
        ("theme", "light"),
        ("pomodoro_duration", "25"),
        ("short_break", "5"),
        ("notifications_enabled", "true")
    ]
    for s in default_settings:
        cursor.execute("INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)", s)
