from datetime import datetime, date, timedelta
from database import get_db

class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics():
        db = get_db()
        today_str = date.today().isoformat()
        now_dt_str = datetime.now().strftime('%Y-%m-%d %H:%M')

        # 1. Total tasks
        cursor = db.execute("SELECT COUNT(*) as count FROM tasks")
        total_tasks = cursor.fetchone()['count']

        # 2. Completed today
        cursor = db.execute("""
            SELECT COUNT(*) as count FROM tasks 
            WHERE status = 'Completed' AND SUBSTR(completed_at, 1, 10) = ?
        """, (today_str,))
        completed_today = cursor.fetchone()['count']

        # 3. Pending tasks
        cursor = db.execute("SELECT COUNT(*) as count FROM tasks WHERE status != 'Completed'")
        pending_tasks = cursor.fetchone()['count']

        # 4. Overdue tasks
        cursor = db.execute("""
            SELECT COUNT(*) as count FROM tasks 
            WHERE status != 'Completed' 
              AND due_date IS NOT NULL 
              AND (
                  (LENGTH(due_date) = 10 AND due_date < ?) OR
                  (LENGTH(due_date) > 10 AND due_date < ?)
              )
        """, (today_str, now_dt_str))
        overdue_tasks = cursor.fetchone()['count']

        # Today's focus progress
        cursor = db.execute("""
            SELECT 
                COUNT(*) as total_today,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_today
            FROM tasks
            WHERE SUBSTR(due_date, 1, 10) = ?
        """, (today_str,))
        today_row = cursor.fetchone()
        tot_today = today_row['total_today'] or 0
        comp_today = today_row['completed_today'] or 0
        today_pct = round((comp_today / tot_today * 100)) if tot_today > 0 else 0

        return {
            'total_tasks': total_tasks,
            'completed_today': completed_today,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'today_total': tot_today,
            'today_completed': comp_today,
            'today_progress_pct': today_pct
        }

    @staticmethod
    def get_charts_data():
        """Returns structured data ready for Chart.js renders."""
        db = get_db()
        today = date.today()

        # 1. Weekly completion trend (Last 7 days, ending today)
        days = []
        labels = []
        counts = []
        
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_str = d.isoformat()
            label = d.strftime('%a, %b %d') if i in (0, 6) else d.strftime('%a')
            days.append(day_str)
            labels.append(label)

            cursor = db.execute("""
                SELECT COUNT(*) as cnt FROM tasks 
                WHERE status = 'Completed' AND SUBSTR(completed_at, 1, 10) = ?
            """, (day_str,))
            counts.append(cursor.fetchone()['cnt'])

        weekly_chart = {
            'labels': labels,
            'datasets': [{
                'label': 'Tasks Completed',
                'data': counts,
                'borderColor': '#6366f1',
                'backgroundColor': 'rgba(99, 102, 241, 0.12)',
                'borderWidth': 3,
                'fill': True,
                'tension': 0.35,
                'pointRadius': 4,
                'pointHoverRadius': 6,
                'pointBackgroundColor': '#6366f1'
            }]
        }

        # 2. Status distribution (Completed vs Pending vs In Progress)
        cursor = db.execute("""
            SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status
        """)
        status_rows = cursor.fetchall()
        status_map = {r['status']: r['cnt'] for r in status_rows}
        
        status_chart = {
            'labels': ['Completed', 'In Progress', 'Pending'],
            'data': [
                status_map.get('Completed', 0),
                status_map.get('In Progress', 0),
                status_map.get('Pending', 0)
            ],
            'backgroundColor': ['#10b981', '#38bdf8', '#64748b']
        }

        # 3. Tasks grouped by priority
        cursor = db.execute("""
            SELECT priority, COUNT(*) as cnt FROM tasks GROUP BY priority
        """)
        priority_rows = cursor.fetchall()
        priority_map = {r['priority']: r['cnt'] for r in priority_rows}

        priority_chart = {
            'labels': ['Urgent', 'High', 'Medium', 'Low'],
            'data': [
                priority_map.get('Urgent', 0),
                priority_map.get('High', 0),
                priority_map.get('Medium', 0),
                priority_map.get('Low', 0)
            ],
            'backgroundColor': ['#ef4444', '#f59e0b', '#6366f1', '#10b981']
        }

        # 7-day productivity summary stats
        seven_day_total = sum(counts)
        seven_day_avg = round(seven_day_total / 7.0, 1)

        return {
            'weekly_trend': weekly_chart,
            'status_distribution': status_chart,
            'priority_distribution': priority_chart,
            'seven_day_total': seven_day_total,
            'seven_day_avg': seven_day_avg
        }

    @staticmethod
    def get_streaks():
        """Calculates current streak and best streak from completed tasks history."""
        db = get_db()
        cursor = db.execute("""
            SELECT DISTINCT SUBSTR(completed_at, 1, 10) as completion_date
            FROM tasks
            WHERE status = 'Completed' AND completed_at IS NOT NULL
            ORDER BY completion_date DESC
        """)
        dates_raw = [r['completion_date'] for r in cursor.fetchall() if r['completion_date']]
        
        if not dates_raw:
            return {'current_streak': 0, 'best_streak': 0, 'active_today': False}

        completed_dates = set(dates_raw)
        today = date.today()
        today_str = today.isoformat()
        yesterday_str = (today - timedelta(days=1)).isoformat()

        active_today = today_str in completed_dates

        # Calculate current streak
        # If completed today, start from today; else if completed yesterday, start from yesterday
        current_streak = 0
        if active_today:
            curr = today
            while curr.isoformat() in completed_dates:
                current_streak += 1
                curr -= timedelta(days=1)
        elif yesterday_str in completed_dates:
            curr = today - timedelta(days=1)
            while curr.isoformat() in completed_dates:
                current_streak += 1
                curr -= timedelta(days=1)
        else:
            current_streak = 0

        # Calculate best streak historically
        sorted_dates = sorted([date.fromisoformat(d) for d in completed_dates])
        best_streak = 0
        if sorted_dates:
            temp_streak = 1
            best_streak = 1
            for i in range(1, len(sorted_dates)):
                if sorted_dates[i] == sorted_dates[i-1] + timedelta(days=1):
                    temp_streak += 1
                else:
                    temp_streak = 1
                if temp_streak > best_streak:
                    best_streak = temp_streak

        return {
            'current_streak': current_streak,
            'best_streak': max(best_streak, current_streak),
            'active_today': active_today
        }

    @staticmethod
    def get_productivity_insights():
        """Computes rich insights: best weekday, top category, high priority completed, average/day."""
        db = get_db()

        # 1. Completed tasks by day of week
        cursor = db.execute("""
            SELECT completed_at FROM tasks
            WHERE status = 'Completed' AND completed_at IS NOT NULL
        """)
        rows = cursor.fetchall()
        
        if not rows:
            return {
                'has_data': False,
                'best_day': None,
                'top_category': None,
                'high_priority_completed': 0,
                'avg_per_active_day': 0,
                'total_completed_all_time': 0
            }

        days_count = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0} # Monday=0
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        unique_active_days = set()

        for r in rows:
            try:
                dt = datetime.fromisoformat(r['completed_at'][:19])
                days_count[dt.weekday()] += 1
                unique_active_days.add(dt.date().isoformat())
            except Exception:
                pass

        best_day_idx = max(days_count, key=days_count.get)
        best_day = day_names[best_day_idx] if days_count[best_day_idx] > 0 else 'N/A'

        # 2. Most completed category
        cursor = db.execute("""
            SELECT category, COUNT(*) as cnt 
            FROM tasks
            WHERE status = 'Completed'
            GROUP BY category
            ORDER BY cnt DESC
            LIMIT 1
        """)
        top_cat_row = cursor.fetchone()
        top_category = f"{top_cat_row['category']} ({top_cat_row['cnt']} tasks)" if top_cat_row else 'None'

        # 3. High & Urgent priority completed
        cursor = db.execute("""
            SELECT COUNT(*) as cnt 
            FROM tasks
            WHERE status = 'Completed' AND priority IN ('High', 'Urgent')
        """)
        high_priority_completed = cursor.fetchone()['cnt']

        total_completed = len(rows)
        active_day_count = len(unique_active_days)
        avg_per_day = round(total_completed / float(active_day_count), 1) if active_day_count > 0 else 0

        return {
            'has_data': total_completed > 0,
            'best_day': best_day,
            'top_category': top_category,
            'high_priority_completed': high_priority_completed,
            'avg_per_active_day': avg_per_day,
            'total_completed_all_time': total_completed
        }
