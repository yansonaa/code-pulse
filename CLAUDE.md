# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodePulse is a full-stack R&D activity intelligence analysis platform. It replaces manual GitLab/GitHub data export and processing workflows with automated commit analysis, visual dashboards, and anomaly detection. The codebase is split into a Python backend (`backend/`) and a React/TypeScript frontend (`frontend/`).

## Common Commands

### Backend

```bash
cd backend

# Windows virtual environment activation
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server (auto-reload on port 8000)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API documentation is available at http://localhost:8000/docs (Swagger) and http://localhost:8000/redoc (ReDoc)
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server (port 3000, proxied to backend)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Note:** There are no test, lint, or formatting tools configured in this project. Adding new ones is a separate task if required.

## High-Level Architecture

### Backend (FastAPI + SQLite)

The backend follows a layered service architecture within a single FastAPI app module:

- **Entry point:** `app/main.py` registers all routers and configures CORS.
- **Data layer:** `app/models.py` (SQLAlchemy ORM), `app/schemas.py` (Pydantic v1), `app/crud.py` (query operations), `app/database.py` (SQLite engine setup). The database file lives at `app/data/codepulse.db`.
- **API layer:** `app/api/` contains FastAPI routers grouped by domain (`commits.py`, `stats.py`, `export_data.py`, `mock.py`, `sync.py`).
- **Business logic:** `app/services/` holds stateless service classes: `StatsCalculator` (computes KPIs, trends, heatmaps, radar, anomaly detection), `GitLogParser` (parses raw git log and CSV), `MockDataGenerator` (produces synthetic commit data), `ExportService` (CSV generation), `LocalGitService` (reads local Git repos via GitPython), `RemoteGitService` (fetches from GitHub/GitLab APIs).

A critical architectural pattern is that all statistics endpoints share a single `StatsCalculator` instance injected via FastAPI's `Depends()` mechanism. Each endpoint receives query parameters (date range, search), parses them, and delegates to `StatsCalculator`, which in turn calls `crud.get_commits()` with filters. This means adding a new filter dimension requires changes in three places: the endpoint signature, the calculator method signature, and the CRUD query builder.

**Python 3.7 Compatibility:** The production environment targets Python 3.7. You must use `List[...]` / `Dict[...]` / `Optional[...]` from `typing` instead of built-in generics (`list[...]`). Pydantic v1 syntax applies: use `orm_mode = True` in `Config` classes, not `from_attributes = True`.

### Frontend (React + Vite + TailwindCSS)

The frontend is a single-page dashboard with no routing. All UI components — header, control panel, KPI cards, trend chart, code stats chart, heatmap, radar chart, member table, anomaly table, import modal, repository config modal — are co-located in `src/App.tsx` as local functional components rather than separate files.

- **State management:** All state lives in the root `App` component. Filter state (date range, search) is lifted here. When filters change, `fetchData()` fires six parallel API calls to populate the dashboard. A `useDebounce` hook (500ms) throttles the search input to avoid excessive requests.
- **API layer:** `src/services/api.ts` uses Axios with a base URL of `/api`. The Vite dev server proxies `/api` to `http://localhost:8000` (see `vite.config.ts`).
- **Visualization:** `echarts-for-react` wraps ECharts instances. Each chart component builds its own ECharts `option` object inline and passes it to `ReactECharts`.
- **Styling:** TailwindCSS utility classes are used throughout. Custom component styles (`.card`, `.btn-primary`, `.table-row`, etc.) and print media queries are defined in `src/index.css`. The dark theme is hardcoded (slate-900 background, slate-100 text).

### Data Flow

1. User adjusts filters in `ControlPanel` → updates `FilterState` in `App`.
2. `useEffect` in `App` triggers `fetchData()` with debounced search.
3. `fetchData` calls six parallel `GET` requests to `/api/stats/*` with the same filter parameters.
4. Backend routes parse dates, inject `StatsCalculator`, and return computed results.
5. `App` updates state for each chart/table, causing re-render.

### Git Repository Connection (New)

The system supports connecting to real Git repositories to automatically load commit data, replacing the previous mock-data-only workflow:

- **Local Git repos:** Uses `GitPython` to read commit history directly from the filesystem. The `LocalGitService` extracts author, message, stats (additions/deletions/files), and detects automated commits via keyword matching. Configured via `POST /api/sync/configs` with `repo_type: "local"` and a `local_path`.
- **Remote GitHub/GitLab repos:** Uses `PyGithub` (GitHub) or direct HTTP requests (GitLab) with an access token to fetch commits via API. Configured via `POST /api/sync/configs` with `repo_type: "github"` or `"gitlab"`, plus `remote_url` and `access_token`.
- **Sync API:** `POST /api/sync/sync/{config_id}` triggers a manual sync for a single repo (default last 90 days, max 5000 commits). `POST /api/sync/sync-all` syncs all active configs at once. Syncs are additive by default; passing `clear_existing=true` wipes old data first.
- **Repository config storage:** `RepositoryConfig` model in SQLite stores name, type, path/token, branch, activation status, and last sync timestamp. The frontend exposes a "仓库管理" modal to add, edit, delete, and sync configs.

### Import Data Formats (Legacy Fallback)

In addition to live Git repo sync, the system still accepts manual imports:
- **Git log text:** Standard `git log` output with commit hash, author, date, message, and file stats. Parsed by `GitLogParser` using regex.
- **CSV:** Flattened commit records with columns matching the schema fields. Also parsed by `GitLogParser`.
- **JSON:** A JSON array of commit objects can be pasted directly via the import modal.

### Mock Data (Legacy Fallback)

`MockDataGenerator` seeds 25 Chinese developer names and 20 commit message templates to generate ~2000 commits across 90 days. It simulates realistic patterns: more commits on weekdays, higher probability of automation at night, occasional large file deletions. Generated via `POST /api/mock/generate` (which also clears existing data first).

### Deployment

Production deployment is intended as:
- Backend: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`
- Frontend: `npm run build` produces static files in `dist/`, served by Nginx with `/api` proxied to the backend.
