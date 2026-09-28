# CodePilot AI — Operational Troubleshooting & Incident Recovery Manual

## 1. Quick Diagnostic Checklist

Before diving into component-specific troubleshooting, run the unified health probe:
```bash
# Test health endpoint directly
curl -s http://localhost:8000/health | jq .

# Or test via Nginx proxy
curl -s http://localhost/health | jq .
```
Look for subsystem status indicators:
* `"database": {"status": "healthy"}`
* `"redis": {"status": "healthy"}`
* `"gemini": {"status": "healthy"}`

---

## 2. Database Connection Issues

### Symptom: `asyncpg.exceptions.ConnectionDoesNotExistError` or `Is the server running on host "localhost" (127.0.0.1) and accepting TCP/IP connections?`

#### Causes & Fixes:
1. **PostgreSQL container is not started**:
   ```bash
   docker compose ps codepilot_postgres
   docker compose start codepilot_postgres
   ```
2. **PostgreSQL port collision (5432 vs 5433)**:
   * By default in `docker-compose.yml`, PostgreSQL is mapped to host port **5433** to avoid conflicts with existing local PostgreSQL installations on 5432.
   * If connecting locally outside Docker, set `DATABASE_PORT=5433` in your `.env`.
3. **Database credentials mismatch**:
   * Inspect `.env`:
     ```env
     DATABASE_USER=postgres
     DATABASE_PASSWORD=postgres_password
     DATABASE_NAME=codepilot_db
     DATABASE_PORT=5432   # Inside Docker network
     ```

#### Verification Command:
```bash
docker exec -it codepilot_postgres pg_isready -U postgres -d codepilot_db
```

---

## 3. Redis Unavailable or Degraded Cache

### Symptom: Health endpoint reports `"redis": {"status": "degraded"}` or logs report `ConnectionRefusedError: [Errno 111] Connect call failed ('127.0.0.1', 6379)`

#### Causes & Fixes:
1. **Redis container is stopped**:
   ```bash
   docker compose start codepilot_redis
   ```
2. **Host port mapping**:
   * Redis is mapped to host port **6380** in `docker-compose.yml` to prevent clashing with existing Redis servers on 6379.
   * Local scripts outside Docker should use:
     ```env
     REDIS_URL=redis://localhost:6380/0
     ```
3. **Application continues in degraded mode**:
   * CodePilot AI is designed to gracefully degrade if Redis is down. Queries will bypass cache and execute directly on PostgreSQL, but rate limiting will fall back to in-memory mode.

#### Verification Command:
```bash
docker exec -it codepilot_redis redis-cli ping
# Expected output: PONG
```

---

## 4. Google Gemini API Errors & Quota Limits

### Symptom: Logs report `google.genai.errors.APIError: 429 Resource has been exhausted (e.g. check quota)` or `401 Unauthorized`

#### Causes & Fixes:
1. **Invalid or Missing API Key**:
   * Ensure `GEMINI_API_KEY` is set in `.env`:
     ```env
     GEMINI_API_KEY=AIzaSy...
     ```
2. **Quota Exceeded (HTTP 429)**:
   * CodePilot AI automatically falls back to deterministic AST rule evaluation and returns quality grades without crashing.
   * To switch model version, adjust `GEMINI_MODEL=gemini-2.5-flash` in `.env`.
3. **Mock Mode for Development / Testing**:
   * Set `MOCK_GEMINI=true` in `.env` to simulate responses without consuming API credits.

---

## 5. Alembic Database Migration Errors

### Symptom: `alembic.util.exc.CommandError: Can't locate revision identified by 'xxxx'` or Table already exists error

#### Causes & Fixes:
1. **Database out of sync with migration history**:
   ```bash
   # Check current migration version
   alembic current

   # Stamp the database to current head if tables were created manually
   alembic stamp head

   # Re-apply migrations
   alembic upgrade head
   ```
2. **Lock contention during migration**:
   * If a migration hangs waiting on a table lock, restart the Postgres container:
     ```bash
     docker compose restart codepilot_postgres
     ```

---

## 6. Docker Startup & Health Check Failures

### Symptom: `dependency failed to start: container codepilot_backend is unhealthy`

#### Causes & Fixes:
1. **Slow cold boot on Windows / WSL2**:
   * The backend container executes Alembic migrations and boots Gunicorn workers on startup. If Docker is slow, the healthcheck start period may expire.
   * We configured `start_period: 60s` and `interval: 10s` in `docker-compose.yml`.
2. **Inspect backend container logs**:
   ```bash
   docker logs codepilot_backend --tail 50
   ```
3. **IPv6 resolution failure on localhost**:
   * Health probes should target `http://127.0.0.1:8000/health` rather than `http://localhost:8000/health` to avoid Docker IPv6 resolving issues.

---

## 7. Upload & Archive Processing Failures

### Symptom: `HTTP 400 Bad Request: "Archive exceeds maximum allowed size"` or extraction error

#### Causes & Fixes:
1. **File size exceeds limit**:
   * Default single file size limit is **1 MB**.
   * Default archive size limit is **50 MB**.
   * Adjust `MAX_UPLOAD_SIZE_MB=100` in `.env` if larger archives are needed.
2. **Nginx HTTP 413 Payload Too Large**:
   * Ensure `client_max_body_size 50M;` is present in `nginx/default.conf`.
3. **Corrupted or Unsupported Archive**:
   * Only standard `.zip` and `.tar.gz` archives are accepted. Password-protected ZIP files are rejected for security analysis.

---

## 8. Port Conflicts

### Symptom: `Bind for 0.0.0.0:80 failed: port is already allocated`

#### Diagnostic Commands:
```powershell
# On Windows PowerShell, find process using port 80:
Get-NetTCPConnection -LocalPort 80 | Select-Object OwningProcess

# Kill conflicting process or change port in docker-compose.yml:
# ports:
#   - "8080:80"
```

Common conflicts:
* Port **80**: Windows IIS (`w3svc`), Skype, or Apache.
* Port **5432**: Local PostgreSQL service. Remapped to `5433` in Docker Compose.
* Port **6379**: Local Redis service. Remapped to `6380` in Docker Compose.

---

## 9. Environment Configuration Failures

### Symptom: `pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings`

#### Causes & Fixes:
1. Pydantic validates all settings at application startup in `app/core/config.py`.
2. Check for missing required variables:
   * Verify that `.env` contains valid types (e.g. `DATABASE_PORT` must be an integer, not a string with quotes).
   * Ensure `SECRET_KEY` is at least 32 characters long.

---

*Document Version: 1.0.0 — Troubleshooting & Incident Recovery Manual.*
