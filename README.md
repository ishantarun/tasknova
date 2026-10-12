# TaskNova — Your Day, Under Control
> **Plan Smarter. Focus Better. Achieve More.**

TaskNova is a commercial-grade, modern productivity SaaS web application built with a **pure Python (Flask)** backend and an elegant, responsive frontend interface. Designed with a dark navy sidebar, electric violet and soft blue accents, subtle gradients, and micro-animations, TaskNova elevates task management beyond traditional To-Do lists into a comprehensive daily productivity cockpit.

---

## 🚀 Key Features

### 1. Executive Productivity Dashboard
- **4 Real-Time Statistics Cards:**
  - **Total Tasks** — all tasks tracked persistently in SQLite.
  - **Completed Today** — tasks finished on the current calendar day with daily completion percentage.
  - **Pending Tasks** — active items in the pipeline.
  - **Overdue Tasks** — unfinished tasks past their deadlines with dynamic alert states.
- **Productivity Analytics:**
  - Weekly task completion trend (Chart.js line chart with smooth curves).
  - Task distribution doughnut chart (Completed vs In Progress vs Pending).
  - Priority distribution telemetry.
- **Today's Focus Section:**
  - Highlights top scheduled targets.
  - Interactive daily completion progress bar.
  - Direct 1-click Pomodoro focus launcher.
- **Quick Capture Input:**
  - Rapidly log ideas and tasks without leaving the dashboard.

### 2. Nova Focus Mode (Distraction-Free Pomodoro)
- Dedicated 25-minute Pomodoro timer with start, pause, resume, and reset controls.
- Smooth SVG circular countdown animation.
- Web Audio API synthesized completion bell chime (zero external audio file dependencies).
- Direct task assignment and automatic session logging to SQLite (`focus_sessions` table).
- 1-click completion of the active focus task.

### 3. Smart Priority Assistant
- Transparent, rule-based recommendation engine written in pure Python.
- Evaluates urgency, deadline proximity, overdue status, star priority, and estimated duration.
- Explains recommendations in clear plain English (e.g., *"Top recommendation because it is past its deadline and overdue, it is flagged with Urgent priority, and you marked it as an important priority."*).

### 4. Advanced Task Management
- **Full Metadata Fields:** Title, Description, Category (Work, Personal, Study, Health, Other), Project, Priority (Low, Medium, High, Urgent), Status (Pending, In Progress, Completed), Start Date, Due Date & Time, Tags, Estimated Duration, Important Star.
- **Dual View Modes:** Seamless toggle between **List View** and **Card View**.
- **Real-Time Multi-Attribute Filtering:** Filter simultaneously by status, priority, category, and project.
- **Dynamic Sorting:** Sort by priority, due date, creation date, or alphabetical title.
- **Quick Actions:** Instant inline complete/reopen, star/unstar, edit, and safe delete with confirmation modal.

### 5. Task Streaks & Telemetry
- Tracks consecutive days with at least one completed task.
- Calculates current streak and all-time best streak from actual SQLite completion history.
- Handles gap days and empty states cleanly.

### 6. Projects & Organization
- Create, edit, and delete high-level projects with custom brand colors and icons.
- Real-time progress bars showing completion percentage per project.
- **Safe Deletion Handling:** Deleting a project never deletes its tasks (preserves tasks safely via `ON DELETE SET NULL`).

### 7. Interactive Monthly Calendar
- Monthly calendar grid rendering with previous/next month navigation.
- Visual task chips on due dates.
- Interactive date inspector panel: click any day to view and launch tasks scheduled for that date, or click **Add** to prefill the task's due date.

### 8. Analytics & Deep Insights
- Peak velocity weekday detection (e.g. Wednesday).
- Top output category calculation.
- Average tasks resolved per active day.
- Historical log of completed Pomodoro sessions.

### 9. Customization & Settings
- Persistent theme toggle between **Light (Default SaaS Clean)** and **Dark (Midnight Slate)**.
- User profile customizations (Name, Role).
- Configurable Pomodoro focus duration and break settings saved in SQLite.

---

## 🛠️ Technology Stack

- **Backend:** Python 3 (Flask) — **Python is the ONLY backend language used**.
- **Database:** SQLite (`instance/tasknova.db`) via Python's built-in `sqlite3` module.
- **Templating:** Jinja2 with semantic HTML5 and reusable layouts.
- **Styling:** Custom CSS3 Design System + Bootstrap 5.3 + Google Font Inter.
- **Icons:** Font Awesome 6.5.
- **Data Visualization:** Chart.js 4.4.

---

## 📂 Project Structure

```
tasknova/
├── app.py                     # Flask application factory and server entry point
├── config.py                  # App configuration and database paths
├── database.py                # SQLite connection lifecycle, schema, and initial seeding
├── models.py                  # TaskRepository, ProjectRepository, FocusSessionRepository, SettingsRepository
├── recommendations.py         # Smart Priority Assistant (transparent rule-based scoring engine)
├── analytics_service.py       # Metrics, streaks, Chart.js dataset formats, and insights
├── test_tasknova.py           # Comprehensive unittest suite (CRUD, API, routes, edge cases)
├── requirements.txt           # Python package dependencies
├── README.md                  # Complete documentation and setup guide
├── instance/
│   └── tasknova.db            # SQLite persistent database file
├── routes/
│   ├── __init__.py
│   ├── main.py                # Jinja2 template page routes
│   └── api.py                 # RESTful JSON endpoints for dynamic UI interactions
├── static/
│   ├── css/
│   │   └── style.css          # Design system, dark navy sidebar, cards, and animations
│   └── js/
│       ├── app.js             # Global modals, toast notifications, search, and CRUD
│       ├── dashboard.js       # Dashboard line and doughnut charts
│       ├── tasks.js           # List/Card switching and instant filtering
│       ├── focus.js           # Nova Focus Pomodoro timer and Web Audio chime
│       ├── calendar.js        # Interactive monthly calendar and day inspector
│       └── analytics.js       # Analytics line and bar charts
└── templates/
    ├── base.html              # Shell layout: dark navy sidebar, header, and shared modals
    ├── dashboard.html         # Overview dashboard, stats cards, today's focus, assistant
    ├── tasks.html             # Full task management, filters, and list/card views
    ├── today.html             # Today's tasks view and daily completion progress bar
    ├── upcoming.html          # Future scheduled tasks
    ├── important.html         # Starred priority items
    ├── completed.html         # Completion archive with reopen options
    ├── projects.html          # Projects overview, color pickers, and progress bars
    ├── calendar.html          # Monthly calendar view with scheduled tasks
    ├── analytics.html         # Productivity telemetry, streaks, and focus history
    └── settings.html          # Appearance, profile, and Pomodoro timer preferences
```

---

## 💻 Windows & VS Code Setup Instructions

### Prerequisites
- Python 3.10+ installed on Windows.

### 1. Open in VS Code
Open the `tasknova` directory in VS Code:
```powershell
code "C:\Users\ishan\.gemini\antigravity\scratch\tasknova"
```

### 2. Create Virtual Environment
Open the VS Code Terminal (`Ctrl + ~`) in PowerShell:
```powershell
py -m venv venv
```

### 3. Install Dependencies
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Run the Application
```powershell
.\venv\Scripts\python.exe app.py
```

### 5. Access the Web App
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running the Automated Test Suite

To verify all database models, CRUD operations, recommendation engine, analytics calculations, and HTTP endpoints:

```powershell
.\venv\Scripts\python.exe -m unittest test_tasknova.py -v
```

All 9 test suites will run and report `OK`.

---

## 🔒 Security & Reliability Highlights
- Parameterized SQL queries prevent SQL injection across all queries.
- Database tables and initial starter data are auto-generated on first run.
- Foreign keys enabled (`PRAGMA foreign_keys = ON;`) with safe cascade handlers (`ON DELETE SET NULL`) preventing accidental task data loss.
- Timestamps and dates formatted consistently for reliable timezone presentation.
