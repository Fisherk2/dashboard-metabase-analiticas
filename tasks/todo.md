# TODO — F0: Preparación

**Fecha:** 2026-07-03 | **Estado:** Pendiente
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Foundation (Estructura + Seguridad)

- [ ] **F0-01a** — Crear directorios: `docker/`, `sql/views/`, `sql/indexes/`, `sql/partitions/`, `metabase/collections/`
- [ ] **F0-01b** — Mover `docker-compose.yml` de raíz a `docker/`, eliminar `Dockerfile` stub
- [ ] **F0-01c** — Eliminar `scripts/build.sh`, `lint.sh`, `setup.sh`, `test.sh` (reemplazados por make targets)
- [ ] **F0-02a** — Extender `.gitignore` con: `data/`, `*.sql.gz`, `.pytest_cache/`, `.coverage`, `metabase-data/`, `*.egg-info/`
- [ ] **F0-02b** — Crear `.env.example` con template: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`, `METABASE_PORT`, `METABASE_SECRET_KEY`

## Checkpoint 1: Foundation ✅

- [ ] `tree -L 2 -I 'agents|skills|references|commands|.git' .` muestra estructura del SPEC.md
- [ ] `git check-ignore -v .env` confirma que `.env` está ignorado
- [ ] `git check-ignore -v .env.example` confirma que `.env.example` NO está ignorado
- [ ] `docker/docker-compose.yml` existe, raíz no tiene `docker-compose.yml`
- [ ] `scripts/` no contiene archivos `.sh`
- [ ] `.env.example` tiene al menos 6 variables documentadas

---

## Slice 2: Documentation (README + Verificación)

- [ ] **F0-03** — Crear `README.md` inicial con: título, descripción, badges, Quick Start (`make setup`), estructura, enlaces
- [ ] **F0-04** — Verificar `AGENTS.md` (49 líneas) y `docs/ARCHITECTURE.md` (115 líneas) — ya completos

## Checkpoint 2: F0 Core ✅ (Ready para F1)

- [ ] `README.md` renderiza correctamente
- [ ] `AGENTS.md` <60 líneas, enlaces funcionan
- [ ] `docs/ARCHITECTURE.md` tiene diagrama Mermaid + ADR index
- [ ] FTR de F0 pasa checklist de `docs/WORKFLOW.md` §5

---

## Slice 3: Automation Interface (Makefile + Requirements)

- [ ] **F0-05** — Implementar `Makefile` completo (25+ targets, 6 secciones, `.PHONY`, `.DEFAULT_GOAL := help`, `include .env`)
- [ ] **F0-05b** — Llenar `requirements.txt` con: `faker>=18.0`, `psycopg2-binary>=2.9`, `python-dotenv>=1.0`

## Checkpoint Final: F0 Complete ✅

- [ ] `make help` lista 25+ targets
- [ ] `make validate` ejecuta sin errores
- [ ] `make deps` instala requirements correctamente
- [ ] `make setup` ejecuta el flujo completo (deps → up → db-init → data-generate) — *requiere F2 para data-generate*
- [ ] Todos los commits atómicos hechos (5-7 commits)
- [ ] Working tree limpio

---

## Slice 4: Quality Tooling [OPCIONAL — Diferible a F2]

- [ ] **F0-06a** — Configurar `sqlfluff` (`.sqlfluff` con `dialect = postgres`)
- [ ] **F0-06b** — Configurar `black` + `flake8` (`pyproject.toml`, `.flake8`)
- [ ] **F0-06c** — Configurar `pre-commit` hooks (`.pre-commit-config.yaml`)

---

## Progreso

- **Total tareas:** 7 (sin F0-06) o 10 (con F0-06)
- **Tareas completadas:** 0
- **Checkpoints pasados:** 0/2
- **Tiempo invertido:** 0h
- **Estimación restante:** 6h (sin F0-06) o 7.5h (con F0-06)
