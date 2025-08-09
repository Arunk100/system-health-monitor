# System Health Monitor

End‑to‑end monitoring stack consisting of a lightweight cross‑platform agent, a FastAPI backend (SQLite persistence), and a Vue 3 dashboard for viewing machine health & exporting data.

## Features
* Health checks: disk encryption status, OS updates up‑to‑date, antivirus present/enabled, inactivity sleep timeout.
* WSL / unsupported environments gracefully skipped with reasons.
* Change detection: agent only reports when results differ (hash comparison).
* Exponential backoff on transient POST failures.
* API endpoints: ingest, list (filter by OS & issues), CSV export.
* Dashboard: OS filter, issues-only toggle, client-side sorting, auto & manual refresh, tooltips for skipped reasons, CSV download link.
* Optional API key authentication for report ingestion.

## Architecture
```
[ Agent ] --POST /report--> [ FastAPI Backend + SQLite ] --JSON--> [ Vue Frontend ]
										 |\
										 | +--> /machines (JSON list)
										 | +--> /machines.csv (export)
										 | +--> (future) /health
```

### Components
* `client/` – Python agent (`agent.py`, health checks in `checks.py`).
* `backend/` – FastAPI app (`main.py`, routes in `routes.py`, models via SQLAlchemy, SQLite DB file in root directory).
* `frontend/` – Vue 3 SPA (development server or built static assets).

## Health Checks (current semantics)
| Check | Key | Pass Criteria | Issue Criteria | Skipped Conditions |
|-------|-----|---------------|----------------|--------------------|
| Disk Encryption | `disk_encryption.status` | True | False | WSL / not detectable |
| OS Updates | `os_update.up_to_date` | True | False | WSL / not detectable |
| Antivirus | `antivirus.present` & `antivirus.enabled` | Both True | Either False | WSL / not detectable |
| Inactivity Sleep | `inactivity_sleep.sleep_minutes` | <= 10 or null | > 10 | WSL / not detectable |

Each check object may have: `skipped: bool`, `reason: str`, and other fields.

## Data Model (simplified)
Machine: `machine_id (str)`, `os (str)`, `last_checkin (UTC datetime)`, `results (JSON)`.

## API Endpoints
| Method | Path | Description | Query Params |
|--------|------|-------------|--------------|
| POST | `/report` | Ingest/update machine status (requires valid body; optional API key) | N/A |
| GET | `/machines` | List machines | `os`, `issues` (true) |
| GET | `/machines.csv` | CSV export of machines (same filters) | `os`, `issues` |

Optional header: `X-API-Key: <key>` (if `API_KEY` environment variable is set on backend, it is enforced for `/report`).

## Quick Start (Development)
Terminal 1 – Backend:
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Terminal 2 – Frontend:
```
cd frontend
npm install
npm run serve -- --port 5173
```
Terminal 3 – Agent:
```
cd client
pip install -r requirements.txt
python agent.py
```
Open the dashboard (default) http://localhost:5173

## CSV Export
Download via link in UI or directly: `http://localhost:8000/machines.csv` (add `?issues=true&os=Linux` etc.).

## Configuration
Backend environment variables:
* `API_KEY` – If set, required for POST /report (sent as `X-API-Key`).

Agent configuration (`client/config.py`):
* `API_URL` – Base URL for backend (`http://localhost:8000`).
* `CHECK_INTERVAL_MINUTES` – Periodic loop delay.
* `API_KEY` – Matches backend if auth enabled.

## Security Notes
Current minimal API key enforcement on ingest. For production hardening consider: rate limiting, signed payloads (HMAC), TLS, moving auth to all endpoints.

## Frontend Notes
All sorting is client-side. For large fleets add server-side pagination & sorting. Auto-refresh interval: 30s.

## Future Improvements (Ideas)
* Historical timeline / per-check history.
* WebSocket push updates.
* Structured logging & metrics (Prometheus endpoint).
* Docker / container build (multi-stage) & compose refinement.
* Unit/integration test suite (pytest + frontend component tests).

## Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `/machines.csv` 404 | Old backend process w/out route | Restart uvicorn; verify in `/docs` |
| Agent prints repeated "No change" | Results hash unchanged | Modify a check or wait for change |
| CORS errors in browser | Different host/port & missing CORS config | CORS already `*`; ensure hitting correct URL |

## License
Educational / assignment project; add license text here if required.

