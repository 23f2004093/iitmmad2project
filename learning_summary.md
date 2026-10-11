# Learning & Project Context Summary (Read Me First)

This file serves as a memory link between the previous chat session and the new chat session. It explains the project state, architecture choices, and guidelines so the next assistant can immediately understand the context.

---

## 1. Project Background & Requirements
*   **Project Name**: Placement Portal (V2)
*   **Target Repo URL**: `https://github.com/23f2004093/iitmmad2project.git`
*   **Current Workspace**: `C:\Users\bachc\Downloads\projectiitm` 
*   **Technology Stack**:
    *   **Backend**: Flask (Python) with Flask-SQLAlchemy (SQLite)
    *   **Frontend**: Vue.js 3 via CDN (using native browser ES Modules with `import`/`export` syntax, no build step, index.html is entry point)
    *   **Broker & Worker (Celery & Redis)**: Kept files but bypassed in active code logic for now (user wants standard Flask session cookies and synchronous tasks for simplicity).
    *   **CSS**: Bootstrap 5 only (no Tailwind or other CSS).

---

## 2. Project Folder Structure
```text
/ (Project Root)
├── frontend/                   # Vue 3 CDN project (using native ES Modules)
│   ├── index.html              # Jinja2 / HTML main entrypoint served by send_file
│   ├── css/
│   │   └── style.css           # Custom styling
│   ├── assets/                 # App assets (images)
│   └── js/
│       ├── app.js              # Main Vue router configuration (Vue Router 4)
│       └── components/         # Modular ES Component JS files (empty fetch methods)
│           ├── Navbar.js
│           ├── AllLogin.js
│           ├── StudentRegistration.js
│           ├── StudentDashboard.js
│           ├── CompanyDashboard.js
│           └── AdminDashboard.js
│
└── backend/                    # Python Flask backend (initialized empty skeletons)
    ├── app.py                  # Flask entrypoint & DB create_all()
    ├── config.py               # Database and task configurations
    ├── database.py             # SQLite database engine connection
    ├── requirements.txt        # Python package dependencies
    ├── models/                 # SQLAlchemy database models
    │   ├── __init__.py
    │   ├── user.py
    │   ├── job.py
    │   └── application.py
    ├── routes/                 # Flask API Blueprints
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── students.py
    │   ├── companies.py
    │   ├── admin.py
    │   └── jobs.py
    └── tasks/                  # Celery batch & background jobs
        ├── __init__.py
        ├── daily_reminders.py
        ├── monthly_report.py
        └── csv_export.py
```

---

## 3. Key Design Choices
1.  **Vue CDN + Router**: Native ES Modules are used to import components inside `app.js` using `import`/`export` statements (similar to Vue CLI but runs without Node/Vite build steps).
2.  **No complex middleware**: We serve `index.html` from `app.py` using `send_file("../frontend/index.html")` which avoids the `{{ }}` curly brace conflict between Jinja2 and Vue.
3.  **Obsidian Vault**: The user's learning logs and questions are actively updated in `C:\Users\bachc\OneDrive\Documents\Obsidian Vault\Placement Portal Learning.md`.

---

## 4. Current State
*   All backend routing and task files have been created as **empty skeleton files** (0 bytes) so the user can write the logic personally.
*   The frontend components are populated with **Bootstrap HTML templates** and data models, with the `fetch()` calls replaced by `// TODO` comments.
*   Next assistant should read this file, inspect the folder structure, and ask the user how they would like to start writing the code!
