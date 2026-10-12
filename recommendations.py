from datetime import datetime, date

class SmartPriorityAssistant:
    """
    Transparent, rule-based recommendation engine in Python.
    Evaluates pending tasks by priority, deadline proximity, overdue status,
    and estimated duration to determine the highest-impact task to tackle next.
    """

    @staticmethod
    def get_recommendation(tasks):
        """
        Receives a list of task dicts and returns the best task with an analytical explanation.
        """
        pending_tasks = [t for t in tasks if t.get('status') != 'Completed']
        if not pending_tasks:
            return None

        today = date.today()
        now = datetime.now()
        scored_tasks = []

        for task in pending_tasks:
            score = 0
            reasons = []

            # 1. Priority scoring
            priority = task.get('priority', 'Medium')
            if priority == 'Urgent':
                score += 50
                reasons.append("it is flagged with Urgent priority")
            elif priority == 'High':
                score += 35
                reasons.append("it is a High-priority item")
            elif priority == 'Medium':
                score += 20
            else: # Low
                score += 10

            # 2. Due date proximity & overdue status
            due_date_str = task.get('due_date')
            is_overdue = False
            due_today = False
            due_soon = False

            if due_date_str:
                try:
                    # Can be YYYY-MM-DD or YYYY-MM-DDTHH:MM
                    if 'T' in due_date_str:
                        due_dt = datetime.fromisoformat(due_date_str)
                        due_d = due_dt.date()
                        if due_dt < now:
                            is_overdue = True
                    else:
                        due_d = date.fromisoformat(due_date_str)
                        if due_d < today:
                            is_overdue = True

                    if is_overdue:
                        score += 60
                        reasons.append("it is past its deadline and overdue")
                    elif due_d == today:
                        score += 40
                        due_today = True
                        reasons.append("it is scheduled for completion today")
                    elif 0 < (due_d - today).days <= 2:
                        score += 25
                        due_soon = True
                        reasons.append(f"it is due within {(due_d - today).days} day(s)")
                except Exception:
                    pass

            # 3. Important / Starred status
            if task.get('is_important'):
                score += 20
                reasons.append("you marked it as an important priority")

            # 4. Focus flag (already selected)
            if task.get('is_focus'):
                score += 15

            # 5. Estimated duration: quick win bonus (25 mins or less)
            est_dur = task.get('estimated_duration') or 30
            if est_dur <= 25:
                score += 10
                reasons.append(f"it can be achieved in a single focus session ({est_dur} mins)")

            # Assemble plain English explanation
            if not reasons:
                explanation = "Recommended as the next standard priority task in your queue."
            else:
                if len(reasons) == 1:
                    explanation = f"Recommended because {reasons[0]}."
                elif len(reasons) == 2:
                    explanation = f"Recommended because {reasons[0]} and {reasons[1]}."
                else:
                    primary = reasons[0]
                    secondary = reasons[1]
                    explanation = f"Top recommendation because {primary}, {secondary}, and {reasons[-1]}."

            scored_tasks.append({
                'task': task,
                'score': score,
                'explanation': explanation,
                'is_overdue': is_overdue,
                'due_today': due_today
            })

        # Sort descending by score
        scored_tasks.sort(key=lambda x: x['score'], reverse=True)
        top = scored_tasks[0]

        return {
            'task': top['task'],
            'score': top['score'],
            'explanation': top['explanation'],
            'alternatives': [item['task'] for item in scored_tasks[1:4]]
        }
