# Jyotish API — Refactored Structure

## New Directory Layout

```
project/
├── api.py                         ← REPLACE old api.py with this (15 lines)
│
├── core/                          ← NEW folder
│   ├── __init__.py
│   ├── config.py                  ← all env vars / settings in one place
│   ├── database.py                ← MySQL connection POOL (replaces database.py)
│   ├── api_logger.py              ← fixed logger (replaces api_logger.py)
│   ├── exceptions.py              ← custom exception classes
│   └── logging_setup.py           ← call once at startup
│
├── services/                      ← NEW folder — all business logic
│   ├── __init__.py
│   ├── chart_service.py           ← single thread-safe jm wrapper
│   ├── ashtakavarga_service.py    ← BAV computation (all bugs fixed)
│   ├── dasha_service.py           ← all dasha logic
│   ├── panchang_service.py        ← panchang + muhurta logic
│   ├── dosha_service.py           ← mangal / pitra / kaalsarp / papasamaya
│   └── prediction_service.py      ← horoscope + nakshatra + sun predictions
│
├── routers/                       ← NEW folder — HTTP only, no logic
│   ├── __init__.py
│   ├── panchang.py
│   ├── dasha.py
│   ├── horoscope.py
│   ├── dosha.py
│   ├── predictions.py
│   ├── ashtakavarga.py
│   ├── chart.py
│   └── pdf.py
│
└── models/                        ← NEW folder
    ├── __init__.py
    └── requests.py                ← all Pydantic input models
```

---

## Migration Steps (in order)

### Step 1 — Install new dependency
```bash
pip install pydantic-settings
```

### Step 2 — Replace database.py
Delete old `database.py`. Copy `core/database.py` in its place at the **root**,
OR update all imports from `database` → `core.database`.

The new version creates a **connection pool** at startup instead of one
connection per request. No other changes needed — `get_db_connection()` shim
is still present for backward compatibility.

### Step 3 — Replace api_logger.py
Delete old `api_logger.py`. Copy `core/api_logger.py`.
Update import in any file that does `from api_logger import ...`
→ `from core.api_logger import ...`

**Bugs fixed in new version:**
- Uses connection pool (no new socket per decorated call)
- `sql` variable referenced before assignment in `get_api_usage_stats` — fixed
- `get_remaining_calls()` is now a standalone importable function

### Step 4 — Copy new folders
Copy `core/`, `services/`, `routers/`, `models/` into your project root.

### Step 5 — Replace api.py
Replace your old `api.py` (820+ lines) with the new one (15 lines).
All endpoints are identical — same URLs, same request params, same responses.

### Step 6 — Update .env (no changes needed)
`core/config.py` reads the same env var names your old `database.py` used:
`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_TIMEOUT`

Optional new vars you can add:
```
DB_POOL_SIZE=10          # default 10
API_DAILY_LIMIT=500000   # default 500000
LOG_LEVEL=INFO           # default INFO
```

---

## What Changed and Why

| Before | After | Reason |
|---|---|---|
| `mysql.connector.connect()` per request | Connection pool created once | Prevents connection exhaustion at scale |
| `api_logger.py` opens 3 connections per call | 2 pool borrows max | 3x fewer connection operations |
| `jm.generate_astrologicalData()` called from 6+ places with no lock | `chart_service.compute_chart()` with one global lock | Prevents concurrent requests corrupting shared jm state |
| Business logic inside endpoint functions | Logic in `services/` | Reusable, testable, no HTTP dependency |
| `api.py` 820+ lines | `api.py` 15 lines | Single responsibility |
| `api_id` enforced inconsistently | `@log_api_call` raises 401 if missing, always | Consistent auth across all endpoints |
| BAV state accumulated across calls | Fresh dict every call in `ashtakavarga_service` | Correct results for multiple users |
| Hard-coded `500_000` in 15+ places | `settings.API_DAILY_LIMIT` | Change limit in one place |

---

## Adding a New Endpoint (for the future)

1. Add business logic to the relevant `services/` file (or create a new one)
2. Add the route to the relevant `routers/` file (or create a new one)
3. If it's a new router, add one line to `api.py`: `app.include_router(myrouter.router)`

No other files need to change.
