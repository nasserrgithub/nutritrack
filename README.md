# NutriTrack — Backend

A full-stack food and nutrition tracker built with FastAPI, PostgreSQL, SQLAlchemy, and the Anthropic API. This repository contains the FastAPI backend, Flask admin panel, and Celery background worker.

---

## Features

**Food logging**
- Log food entries by name — the AI (Claude) automatically looks up macros for any food not already in the database
- Log food entries via natural language (e.g. "I had two eggs and toast for breakfast") — Claude parses the meal and creates multiple entries in one request
- View all food entries for any given date, including scaled calories, protein, carbs, and fat per entry
- Delete incorrect food entries (with user-scoped ownership validation — users can only delete their own entries)

**Macro tracking**
- Set daily macro goals (calories, protein, carbs, fat) with a configurable effective date
- View a daily summary showing total consumed and remaining macros for any date
- AI-powered food suggestions — provide a list of foods you have available, and Claude suggests portions and combinations to help hit your remaining macro targets

**Weight tracking**
- Log daily weight entries with optional notes
- Retrieve weight history over a configurable date range (default: last 30 days)

**Admin panel** (Flask, port 5000)
- Dashboard showing total user, food, and entry counts
- User management table
- Trigger weekly macro report generation per user (Celery background task)
- Send weekly report emails with macro summaries
- Export food log as CSV (streamed) or weekly report as PDF

**Background tasks** (Celery + Redis)
- Generate weekly macro reports using `MacroAggregator`
- Send HTML email reports via Gmail SMTP
- Tasks triggered from the Flask admin panel

**Authentication**
- JWT-based auth (register, login)
- All food/summary/weight/goal endpoints require a valid Bearer token
- Tokens expire after 24 hours; invalid/expired tokens return 401

---

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Admin panel | Flask + Jinja2 |
| Background tasks | Celery + Redis |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| AI | Anthropic API (Claude) |
| Email | smtplib + Gmail SMTP |
| PDF export | reportlab |
| Testing | pytest + pytest-cov |

---

## Project structure

```
nutritrack/
├── api/
│   ├── main.py              ← FastAPI app, middleware, exception handlers
│   ├── settings.py          ← pydantic-settings config
│   ├── dependencies.py      ← get_db_session, get_current_user
│   ├── auth_utils.py        ← JWT creation/validation, bcrypt hashing
│   └── routers/
│       ├── auth.py          ← POST /auth/register, POST /auth/login
│       ├── foods.py         ← GET /foods/, GET /foods/{id}, POST /foods/
│       ├── logs.py          ← POST /log/, POST /log/natural, GET /log/{date}, DELETE /log/{id}
│       ├── goals.py         ← POST /goals/, GET /goals/active
│       ├── summary.py       ← GET /summary/{date}, POST /summary/{date}/suggestions
│       └── weight.py        ← POST /weight/, GET /weight/
├── ai/
│   ├── client.py            ← Anthropic API calls (food lookup, NL parsing, suggestions)
│   └── prompts.py           ← prompt templates
├── admin/
│   ├── app.py               ← Flask app factory
│   ├── routes.py            ← dashboard, users, exports, task triggers
│   └── templates/admin/     ← Jinja2 HTML templates
├── core/
│   ├── models.py            ← Food, FoodEntry, MacroGoal, WeightEntry dataclasses
│   ├── parsers.py           ← MacroAggregator, get_daily_totals generator
│   ├── utils.py             ← calculate_calories, decorators (timed_log, validate_macros, retry, rate_limit)
│   ├── exceptions.py        ← custom exceptions (FoodNotFoundError, GoalNotSetError, etc.)
│   └── logger.py            ← structured logging setup
├── db/
│   ├── base.py              ← SQLAlchemy declarative base
│   ├── database.py          ← engine, SessionLocal, get_session context manager
│   ├── models.py            ← UserModel, FoodModel, FoodEntryModel, MacroGoalModel, WeightEntryModel
│   ├── repositories.py      ← repository classes (one per model)
│   ├── schemas.py           ← Pydantic request/response schemas
│   └── seed.py              ← seed data (7 common foods)
├── worker/
│   ├── celery_app.py        ← Celery config (Redis broker/backend)
│   ├── tasks.py             ← generate_weekly_report, send_weekly_report_email
│   └── utils.py             ← send_email, render_html (Jinja2 outside Flask)
tests/
├── conftest.py              ← shared fixtures (db_engine, db_session, client, sample data)
├── test_core_models.py      ← FoodEntry scaling methods
├── test_daily_totals.py     ← get_daily_totals generator
├── test_parsers.py          ← MacroAggregator totals, remaining macros, top foods
├── test_utils.py            ← calculate_calories, validate_macros decorator
├── test_repositories.py     ← food creation, IDOR-safe delete
├── test_endpoints.py        ← auth endpoints, POST /log/natural with mocked AI
└── test_exception_handlers.py ← FoodNotFoundError→404, GoalNotSetError→404, AIServiceError→503
alembic/                     ← database migration scripts
run_admin.py                 ← Flask admin entry point
```

---

## Local setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 5+ (Windows: [tporadowski/redis](https://github.com/tporadowski/redis/releases))
- An [Anthropic API key](https://console.anthropic.com)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) for email features

### 1 — Clone and create a virtual environment

```bash
git clone https://github.com/your-username/nutritrack.git
cd nutritrack
python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate

# macOS/Linux
source .venv/bin/activate
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### 3 — Create the database

```bash
# connect to PostgreSQL
psql -U postgres

# inside psql:
CREATE DATABASE nutritrack;
CREATE USER nutritrack_user WITH PASSWORD 'nutritrack_pass';
GRANT ALL PRIVILEGES ON DATABASE nutritrack TO nutritrack_user;
\q
```

### 4 — Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://nutritrack_user:nutritrack_pass@localhost:5432/nutritrack
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key
REDIS_URL=redis://localhost:6379/0
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_FROM=your@gmail.com
```

Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5 — Run database migrations and seed data

```bash
alembic upgrade head
python -m nutritrack.db.seed
```

### 6 — Run the services

Three separate terminals are needed:

```bash
# Terminal 1 — FastAPI (port 8000)
uvicorn nutritrack.api.main:app --reload

# Terminal 2 — Flask admin panel (port 5000)
python run_admin.py

# Terminal 3 — Celery worker (background tasks)
# Windows:
celery -A nutritrack.worker.celery_app worker --loglevel=info --pool=solo
# macOS/Linux:
celery -A nutritrack.worker.celery_app worker --loglevel=info
```

Redis must be running before starting the Celery worker:
```bash
# Windows (if installed as a service)
net start redis

# macOS/Linux
redis-server
```

### 7 — Verify it's running

- FastAPI docs: http://localhost:8000/docs
- Flask admin: http://localhost:5000/admin/

---

## Running tests

```bash
# run all tests
pytest -v

# run with coverage report
pytest --cov=nutritrack --cov-report=term-missing

# run a specific test file
pytest tests/test_parsers.py -v
```

The test suite uses a transactional fixture that rolls back all database changes after each test — your development database is never permanently modified by running tests.

---

## API overview

All endpoints except `/auth/register` and `/auth/login` require a Bearer token in the `Authorization` header.

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login, returns JWT token |
| GET | `/foods/` | List all foods |
| GET | `/foods/{id}` | Get a food by ID |
| POST | `/foods/` | Create a food manually |
| POST | `/log/` | Log a food entry by name |
| POST | `/log/natural` | Log a meal via natural language |
| GET | `/log/{date}` | Get food entries for a date |
| DELETE | `/log/{entry_id}` | Delete a food entry (own entries only) |
| POST | `/goals/` | Create/update a macro goal |
| GET | `/goals/active` | Get the current active macro goal |
| GET | `/summary/{date}` | Get daily macro summary |
| POST | `/summary/{date}/suggestions` | Get AI food suggestions |
| POST | `/weight/` | Log a weight entry |
| GET | `/weight/` | Get weight history (default: last 30 days) |

---

## Windows-specific notes

- Use `python` not `python3` (the latter maps to the Windows Store version outside a venv)
- Celery requires `--pool=solo` on Windows due to multiprocessing restrictions
- Redis: use the [tporadowski Windows port](https://github.com/tporadowski/redis/releases) — Redis 5.0.x is required for Celery 5.4.0 compatibility
- Add Redis to your PATH: `C:\Program Files\Redis\`
- Add PostgreSQL to your PATH: `C:\Program Files\PostgreSQL\17\bin\`
