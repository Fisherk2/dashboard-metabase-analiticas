# TODO — F1: Infraestructura

**Fecha:** 2026-07-03 | **Estado:** Pendiente
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Compose Config Foundation (1.9 h)

- [ ] **F1-01** — Completar `docker/docker-compose.yml` con environment, ports (solo Metabase), volumes named, healthcheck (pg_isready), network `ecommerce_net`, mem_limit, restart policy, depends_on service_healthy
- [ ] **F1-02** — Extender `.env.example` con 7 vars faltantes: `MB_DB_TYPE`, `MB_DB_DBNAME`, `MB_DB_PORT`, `MB_DB_USER`, `MB_DB_PASS`, `MB_DB_HOST`, `METABASE_SECRET_KEY`
- [ ] **F1-03** — Crear `.dockerignore` con patrones: `venv/`, `tests/`, `__pycache__/`, `*.pyc`, `.env`, `.env.*`, `.git/`, `metabase-data/`, `data/`, `*.log`, `.pytest_cache/`
- [ ] **F1-04** — Crear `docker/docker-compose.override.yml` template con `services: {}` y comentario explicativo

## Checkpoint 1: Config Foundation ✅

- [ ] `make validate` exit 0 sin warnings
- [ ] `docker compose -f docker/docker-compose.yml config` muestra ambos servicios con healthcheck, volumes, environment, networks
- [ ] `.env.example` tiene ≥ 14 variables (verificar con `grep -c '=' .env.example`)
- [ ] `docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml config` exit 0
- [ ] `.dockerignore` excluye `venv/`, `.env`, `tests/`, `__pycache__/`
- [ ] `git check-ignore .env` retorna el path

---

## Slice 2: Services Up & Healthy (35 min)

- [ ] **F1-05** — `make up` levanta ambos servicios; `make status` muestra `metabase-postgres` y `metabase-app` en estado "Up"
- [ ] **F1-06** — `make db-check` retorna "accepting connections"; log de PostgreSQL muestra "database system is ready"
- [ ] **F1-07** — `make logs-mb` muestra "Metabase Initialization Complete" sin FATAL ni "Connection refused"

## Checkpoint 2: Services Healthy ✅

- [ ] `make up` exit 0, ambos contenedores `Up`
- [ ] `make db-check` retorna "accepting connections"
- [ ] `make logs-mb | tail -50` muestra "Metabase Initialization Complete" sin errores
- [ ] `docker inspect metabase-postgres --format='{{.State.Health.Status}}'` retorna "healthy"
- [ ] `docker inspect metabase-app --format='{{.State.Status}}'` retorna "running"

---

## Slice 3: Integration & Resilience (55 min)

- [ ] **F1-08** — `curl -s http://localhost:3000/api/health` retorna 200 con `{"status":"ok"}`
- [ ] **F1-09** — `make logs-mb | grep -iE "database|postgres"` muestra inicialización sin errores
- [ ] **F1-10** — Persistencia: crear `_f1_test` table, `make down && make up`, verificar que tabla persiste, luego DROP
- [ ] **F1-11** — Port isolation: `docker port metabase-postgres` retorna vacío; `nc -zv localhost 5432 -w 2` falla

## Checkpoint 3: Resilience Verified ✅

- [ ] `curl -s http://localhost:3000/api/health` retorna 200
- [ ] `make logs-mb` NO contiene "Connection refused" ni "FATAL"
- [ ] Tabla `_f1_test` persiste tras `make down && make up`
- [ ] `docker volume ls | grep metabase-dashboard` muestra 2 volumes (pg_data, mb_data)
- [ ] `docker port metabase-postgres` retorna vacío (BD aislada de host)
- [ ] `nc -zv localhost 5432` falla (puerto no expuesto a host)

---

## Slice 4: Automated Test Suite (1 h)

- [ ] **F1-12** — Crear `tests/test_f1.py` con:
  - Tests estáticos: config válido, vars presentes, healthcheck definido, network interno, mem_limit
  - Tests de runtime con marker `@pytest.mark.runtime`: `make up` + `curl /api/health` + `docker port` vacío
  - Skip automático si Docker no disponible

## Checkpoint 4: F1 Complete ✅ (Ready para F2)

- [ ] `make test` muestra F0 (72) + F1 (≥20) tests passing = 92+ total
- [ ] FTR de F1 pasa checklist de `docs/WORKFLOW.md` §5
- [ ] `make up && make down && make up` roundtrip funciona sin errores
- [ ] `make validate && make up && make status` es la ruta crítica documentada
- [ ] `git log --oneline` muestra 6-8 commits atómicos para F1
- [ ] Working tree limpio

---

## Progreso

- **Total tareas:** 12
- **Tareas completadas:** 0
- **Checkpoints pasados:** 0/4
- **Tiempo invertido:** 0h
- **Estimación restante:** 4.5h
- **Tests objetivo:** 72 (F0) + 20 (F1) = 92+ passing
