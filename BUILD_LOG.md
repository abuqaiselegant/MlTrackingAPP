# 🛠️ BUILD LOG — ML Experiment Tracker

> Single source of truth for the project's overview, architecture, plan, steps, and
> a running log of issues / improvements. Append new entries with timestamps — never
> rewrite history; add a new dated entry instead.

- **Created:** 2026-07-07 04:55 IST
- **Repo:** `MlTrackingAPP` (branch `main`)
- **Maintainer:** Abu Qais

---

## 1. Overview

A self-hostable, MLflow-style **experiment tracking platform**. ML engineers log
training runs (hyperparameters, time-series metrics, and model/artifact files) from
any Python project with a few lines of code, then browse and compare them in a web
dashboard.

Three cooperating pieces:

| Piece | Tech | Role |
|-------|------|------|
| **Backend API** (`app/`) | FastAPI + PostgreSQL + SQLAlchemy | Persists experiments, metrics, artifacts; exposes REST API |
| **Python client** (`mltracker.py`) | Single file, only `requests` | 4-line integration to log runs from training code |
| **Frontend** (`frontend/`) | Next.js 16, TypeScript, Tailwind, shadcn/ui | Dashboard, detail pages, charts, integration page |

**Deployed:** Frontend → Vercel (`ml-tracking-app.vercel.app`), Backend → Render
(`ml-tracking-api.onrender.com`).

---

## 2. Architecture

### Request flow
```
 training script                  Next.js dashboard
   │ import mltracker                │ axios (lib/api.ts)
   ▼                                 ▼
 ┌─────────────────────────────────────────────┐
 │        FastAPI (app/main.py)                 │
 │   CORS → routers → services → models         │
 └───────────────┬──────────────┬───────────────┘
                 ▼              ▼
         PostgreSQL       artifacts/ (disk)
     experiments/metrics    model files
```

### Backend layering (clean separation)
- **routers/** — HTTP surface + validation (`experiments.py`, `metrics.py`, `artifacts.py`)
- **services/** — business logic + DB access (`*_service.py`)
- **models/** — SQLAlchemy ORM (`experiment`, `metric`, `artifact`)
- **schemas/** — Pydantic request/response contracts
- **config.py** — `pydantic_settings` (`DATABASE_URL`, `ARTIFACTS_PATH`, `CORS_ORIGINS`)
- **database.py** — engine/session + `get_db` dependency
- **alembic/** — DB migrations (`001_initial`, `002_add_tags_column`)

### Data model
- **Experiment** — UUID id, name, status (`running`/`completed`/`failed`),
  `hyperparameters` (JSON), `tags` (JSON array), `created_at`. Cascades to metrics & artifacts.
- **Metric** — `id`, experiment_id, `step` (≥0), `metric_name`, `value` (no NaN/Inf), `timestamp`.
- **Artifact** — UUID id, experiment_id, filename, filepath (on disk), size_bytes, uploaded_at.

### Key endpoints
- `POST /experiments`, `GET /experiments` (paginated: `page`/`size`, `status` filter)
- `GET /experiments/compare?ids=...`, `GET /experiments/{id}`
- `PUT /experiments/{id}/status`, `PUT /experiments/{id}/tags`, `DELETE /experiments/{id}`
- `POST /experiments/{id}/metrics` (single or batch ≤1000), `GET .../metrics`, `GET .../metrics/summary`
- `POST /artifacts/experiments/{id}/upload`, `GET /artifacts/experiments/{id}`,
  `GET /artifacts/{id}/download`, `DELETE /artifacts/{id}`

### Python client (`mltracker.py`)
`SimpleMLTracker` singleton `tracker`: `start()`, `log()`, `log_many()`,
`save_model()`, `add_tags()`, `finish()`, plus `@track_experiment` decorator
(auto start/finish, marks `failed` on exception).

---

## 3. Plan

Prioritized backlog to harden the project. Check items off and log completion below.

- [x] **P0** — Fix client ↔ backend contract mismatches (Issues #1, #2 ✅ done 2026-07-07; #3 still open).
  Client can now upload artifacts and log step-less metrics.
- [x] **P1** — Align frontend pagination params with backend (`page`/`size`) — Issue #4 ✅ done 2026-07-07.
- [ ] **P1** — Turn off SQLAlchemy `echo` in production / drive via env — Issue #5.
- [ ] **P2** — Make `CORS_ORIGINS` include the deployed frontend via env — Issue #6.
- [ ] **P2** — Add integration tests that exercise the real client against the API.
- [ ] **P3** — Client `api_url` hardcoded to localhost; allow env/config for prod use — Issue #7.
- [ ] **P3** — Document `.env` setup and Render/Vercel env vars in README.

---

## 4. Steps (chronological work log)

Append one line per action taken. Format: `- [timestamp] action — result`.

- [2026-07-07 04:55 IST] Full-project analysis completed (backend, client, frontend, infra).
- [2026-07-07 04:55 IST] Created this BUILD_LOG.md with overview, architecture, plan, steps, issues.
- [2026-07-07 04:58 IST] Fixed blocker #1: client `save_model()` now POSTs to `/artifacts/experiments/{id}/upload` (`mltracker.py:129`).
- [2026-07-07 04:58 IST] Fixed blocker #2: `MetricCreate.step` now defaults to 0 (`app/schemas/metric.py:9`); client omits `step` when None (`mltracker.py:82-90`).
- [2026-07-07 04:58 IST] Verified schema: omitted step→0, provided step respected, null step rejected (client never sends null).
- [2026-07-07 12:50 IST] Fixed Issue #4: frontend `getExperiments` now sends `page`/`size` instead of `skip`/`limit` (`frontend/lib/api.ts:24`).
- [2026-07-07 12:50 IST] Verified pagination live: `page=1&size=1` and `page=2&size=1` return different experiments; old `skip`/`limit` returned all rows (confirming they were ignored).

---

## 5. Issues & Improvements (timestamped)

> Verified against source on 2026-07-07. Severity: 🔴 blocker · 🟠 bug · 🟡 improvement.

### 🔴 Issue #1 — Artifact upload URL mismatch (client can't save models)
- **Found:** 2026-07-07 04:55 IST
- **Where:** `mltracker.py:130` vs `app/routers/artifacts.py:18`
- **Detail:** Client POSTs to `/experiments/{id}/artifacts`, but the backend route is
  `/artifacts/experiments/{id}/upload`. `tracker.save_model()` will hit **404**.
- **Fix:** Point client at `/artifacts/experiments/{self.experiment_id}/upload`.
- **Status:** ✅ FIXED 2026-07-07 04:58 IST (`mltracker.py:129`)

### 🔴 Issue #2 — Metric schema mismatch (`step` required, client sends optional)
- **Found:** 2026-07-07 04:55 IST
- **Where:** `mltracker.py:73-90` vs `app/schemas/metric.py:8-11`
- **Detail:** `MetricCreate` requires `step: int = Field(..., ge=0)`. Client's `log()`
  defaults `step=None`, so `tracker.log("loss", 0.3)` (no step) sends `step: null` →
  **422 Unprocessable Entity**. Also, the batch endpoint expects `{"metrics": [...]}`
  while the client posts a single flat object — only works because the router accepts a
  `Union[MetricCreate, MetricBatchCreate]`, and single works *only if* step is provided.
- **Fix:** Either make `step` optional/defaulted server-side, or have the client default `step` to a running counter.
- **Status:** ✅ FIXED 2026-07-07 04:58 IST — server defaults `step` to 0 (`app/schemas/metric.py:9`); client omits
  `step` from the payload when `None` (`mltracker.py:82-90`) so the server default applies. Verified with all three cases.

### 🟠 Issue #3 — Client sends unsupported `artifact_type`
- **Found:** 2026-07-07 04:55 IST
- **Where:** `mltracker.py:128` vs `app/routers/artifacts.py:23-27`
- **Detail:** Client sends `data={'artifact_type': ...}` on upload; the upload endpoint
  accepts only `file`. Harmless extra field, but the parameter is silently ignored — the
  artifact type is never stored. Decide whether to persist it or drop it from the client.
- **Status:** OPEN

### 🟠 Issue #4 — Frontend pagination params don't match backend
- **Found:** 2026-07-07 04:55 IST
- **Where:** `frontend/lib/api.ts:26` vs `app/routers/experiments.py:33-42`
- **Detail:** Frontend `getExperiments` sends `skip`/`limit`; backend `list_experiments`
  reads `page`/`size`. Unknown query params are ignored, so the UI always gets page 1 at
  the default size — pagination is effectively broken from the dashboard.
- **Fix:** Send `page`/`size` from the frontend (or accept `skip`/`limit` on the backend).
- **Status:** ✅ FIXED 2026-07-07 12:50 IST — frontend now sends `page`/`size` (`frontend/lib/api.ts:24`),
  matching the backend `list_experiments` contract. Verified live that page 2 returns a distinct row.

### 🟡 Issue #5 — SQLAlchemy `echo=True` in production
- **Found:** 2026-07-07 04:55 IST
- **Where:** `app/database.py:11`
- **Detail:** `echo=True` logs every SQL statement; noisy and a minor perf/security concern
  in production. Comment even says "Set to False in production".
- **Fix:** Drive from settings, e.g. `echo=settings.SQL_ECHO` defaulting to `False`.
- **Status:** OPEN

### 🟡 Issue #6 — CORS origins default to localhost only
- **Found:** 2026-07-07 04:55 IST
- **Where:** `app/config.py:10`
- **Detail:** Default `CORS_ORIGINS` excludes the deployed Vercel frontend; prod works only
  if the env var is set on Render. Worth documenting/verifying.
- **Status:** OPEN (verify Render env)

### 🟡 Issue #7 — Client API URL hardcoded to localhost
- **Found:** 2026-07-07 04:55 IST
- **Where:** `mltracker.py:33`, and printed URLs (`localhost:3000`) throughout
- **Detail:** `api_url` defaults to `http://localhost:8000` and success messages print
  `localhost:3000`. Fine for local use, but a copy-pasted client can't target the hosted
  backend without editing code. Consider reading `MLTRACKER_API_URL` from env.
- **Status:** OPEN

---

## 6. How to run (reference)

```bash
# Backend + Postgres
docker-compose up -d

# Frontend
cd frontend && npm install && npm run dev   # http://localhost:3000

# Tests
pytest

# API docs
open http://localhost:8000/docs
```

---

_Last updated: 2026-07-07 04:58 IST_
