# TODO — F1: Infraestructura

**Fecha:** 2026-07-03 | **Estado:** ✅ COMPLETADO
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Compose Config Foundation (1.9 h)

- [x] **F1-01** — Completar `docker/docker-compose.yml` con environment, ports (solo Metabase), volumes named, healthcheck (pg_isready), network `ecommerce_net`, mem_limit, restart policy, depends_on service_healthy
- [x] **F1-02** — Extender `.env.example` con 7 vars faltantes: `MB_DB_TYPE`, `MB_DB_DBNAME`, `MB_DB_PORT`, `MB_DB_USER`, `MB_DB_PASS`, `MB_DB_HOST`, `METABASE_SECRET_KEY`
- [x] **F1-03** — Crear `.dockerignore` con patrones: `venv/`, `tests/`, `__pycache__/`, `*.pyc`, `.env`, `.env.*`, `.git/`, `metabase-data/`, `data/`, `*.log`, `.pytest_cache/`
- [x] **F1-04** — Crear `docker/docker-compose.override.yml` template con `services: {}` y comentario explicativo

## Checkpoint 1: Config Foundation ✅

- [x] `make validate` exit 0 sin warnings
- [x] `.env.example` tiene ≥ 14 variables
- [x] `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml config` exit 0
- [x] `.dockerignore` excluye `venv/`, `.env`, `tests/`, `__pycache__/`
- [x] `git check-ignore .env` retorna el path

---

## Slice 2: Services Up & Healthy (35 min)

- [x] **F1-05** — `make up` levanta ambos servicios; `make status` muestra `metabase-postgres` y `metabase-app` en estado "Up"
- [x] **F1-06** — `make db-check` retorna "accepting connections"; log de PostgreSQL muestra "database system is ready"
- [x] **F1-07** — `make logs-mb` muestra "Metabase Initialization Complete" sin FATAL ni "Connection refused"

## Checkpoint 2: Services Healthy ✅

- [x] `make up` exit 0, ambos contenedores `Up`
- [x] `make db-check` retorna "accepting connections"
- [x] `make logs-mb | tail -50` muestra "Metabase Initialization Complete" sin errores
- [x] Docker healthcheck status = "healthy"
- [x] Metabase status = "running"

---

## Slice 3: Integration & Resilience (55 min)

- [x] **F1-08** — `curl -s http://localhost:3000/api/health` retorna 200 con `{"status":"ok"}`
- [x] **F1-09** — `make logs-mb | grep -iE "database|postgres"` muestra inicialización sin errores
- [x] **F1-10** — Persistencia: crear `_f1_test` table, `make down && make up`, verificar que tabla persiste, luego DROP
- [x] **F1-11** — Port isolation: `docker port metabase-postgres` retorna vacío; `nc -zv localhost 5432 -w 2` falla

## Checkpoint 3: Resilience Verified ✅

- [x] `curl -s http://localhost:3000/api/health` retorna 200
- [x] `make logs-mb` NO contiene "Connection refused" ni "FATAL"
- [x] Tabla `_f1_test` persiste tras `make down && make up` (3 rows verificadas)
- [x] 2 volumes named persisten (`metabase-dashboard-fish_pg_data`, `metabase-dashboard-fish_mb_data`)
- [x] `docker port metabase-postgres` retorna vacío (BD aislada de host)
- [x] `nc -zv localhost 5432` falla (puerto no expuesto a host)

---

## Slice 4: Automated Test Suite (1 h)

- [x] **F1-12** — Crear `tests/test_f1.py` con:
  - 61 tests estáticos: config válido, vars presentes, healthcheck definido, network interno, mem_limit
  - 6 tests runtime con marker `@pytest.mark.runtime`: services up, pg_isready, logs, health API, port isolation
  - Skip automático si Docker no disponible

## Checkpoint 4: F1 Complete ✅ (Ready para F2)

- [x] `make test` muestra F0 (72) + F1 (67) = **139 tests passing**
- [x] FTR de F1 pasa checklist de `docs/WORKFLOW.md` §5 (Servicios levantan / Credenciales seguras / Persistencia configurada)
- [x] `make up && make down && make up` roundtrip funciona sin errores
- [x] `make validate && make up && make status` es la ruta crítica documentada
- [x] 2 commits atómicos para F1 (Slice 1 + Slices 2-3)
- [x] Working tree limpio

---

## Progreso

- **Total tareas:** 12
- **Tareas completadas:** 12/12 ✅
- **Checkpoints pasados:** 4/4 ✅
- **Tiempo invertido:** ~3h (static) + ~30min (runtime) = ~3.5h
- **Estimación plan:** 4.5h → **Real: ~3.5h** (-22%)
- **Tests totales:** 139 (72 F0 + 67 F1) — todos pasando
- **Commits:** 16 en feat/mvp-dashboard (14 anteriores + 2 F1)
