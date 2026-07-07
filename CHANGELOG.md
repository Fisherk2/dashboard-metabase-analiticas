# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for future changes.

---

## [v1.0.0] - 2026-07-07

### Added

- **Central specification (`SPEC.md`)** — project objective, tech stack, commands, boundaries, and success criteria for the MVP.
- **5 modular feature specifications** — infrastructure, star schema, data generation, SQL optimization, Metabase dashboards, and Makefile automation.
- **4 Architecture Decision Records (ADRs)** — PostgreSQL 15+, Metabase OSS, star schema for OLAP, Docker Compose orchestration.
- **Star schema (10 tables)** — 6 dimension tables (`productos`, `categorias`, `clientes`, `tiempo`, `proveedores`, `almacenes`) and 4 fact tables (`ventas`, `inventario`, `devoluciones`, `logistica`) with explicit foreign keys, `CHECK` constraints, `NOT NULL`, and `COMMENT ON TABLE`.
- **Synthetic data generator (`generate_data.py`)** — Python + Faker script with `--debug`/`--scale`/`--reset` flags, 10 table seeders, Pareto distributions, and transactional inserts.
- **Indexes** — 9+ B-tree indexes on critical columns (`producto_id`, `fecha_id`, `cliente_id`, etc.) via `create_indexes.sql` with `IF NOT EXISTS` idempotency.
- **Materialized views** — 3 pre-aggregated views: `mv_rotacion_mensual`, `mv_stock_actual`, `mv_top_productos` with refresh script.
- **Table partitioning** — `ventas` partitioned by `RANGE (fecha_venta)` into 12 monthly partitions plus a `DEFAULT` partition.
- **Metabase REST API setup script (`setup_metabase.py`)** — programmatic authentication, database connection, dashboard creation, and pulse configuration.
- **4 Metabase dashboards** — Rotación por Categoría (bar chart), Stock Actual vs. Mínimo (table with filters), Ventas por Producto Top 10 (row chart), Alertas de Stock Crítico.
- **2 Metabase Pulses** — "Alerta Stock Crítico" (daily at 09:00) and "Resumen Ventas" (daily at 18:00).
- **Performance validation suite** — `measure_query_performance.py` with p50/p95/p99 percentiles, wired through `make test-queries`.
- **Export validation** — `validate_dashboard_exports.py` for CSV/XLSX/JSON/PNG export endpoints.
- **Persistence roundtrip test** — `test_persistence.sh` verifying data survives `make destroy` → `make setup`.
- **Error handling tests** — `test_error_handling.py` covering PostgreSQL failover, health checks, restart, and recovery.
- **Pytest validation suites** — `tests/test_f0.py` through `tests/test_f6.py` covering static analysis, runtime checks, and Git workflow.
- **Product Requirements Document (`docs/PRD.md`)** — functional and non-functional requirements approved v1.0.0.
- **Technical Requirements Document (`docs/TRD.md`)** — technical constraints and decisions approved v1.0.0.
- **Technical debt register (`docs/TECH_DEBT.md`)** — 4 real items with severity, mitigation, and timeline.
- **Lessons learned document (`docs/LESSONS_LEARNED.md`)** — 19 cross-phase patterns organized by phase with 8 overarching conclusions.
- **User Guide (`docs/USER_GUIDE.md`)** — 297 lines covering dashboard interpretation, troubleshooting, FAQ, and export API.
- **Technical Guide (`docs/TECHNICAL_GUIDE.md`)** — 444 lines covering architecture, star schema, materialized views, optimized queries, and lessons learned.
- **Reproducibility validation** — confirmed `make setup` succeeds on a fresh clone with all 304/318 tests passing.

### Changed

- **AGENTS.md** — compressed from 422 lines to a 55-line lean project index with links to all documentation.
- **README.md** — expanded from a stub to 283 lines with badges, Mermaid architecture diagram, 17 sections, feature table, performance metrics, and security notes.
- **Makefile** — 25+ targets organized in 6 sections (Infrastructure, Database, Data, SQL Optimization, Testing, Utilities), loaded from `.env`.
- **Test suites** — simplified with DRY helpers (`has_docker`), extracted shared fixtures to `conftest.py`, parametrized repetitive tests.
- **`generate_data.py`** — extracted helper functions and constants, fixed N+1 query pattern, improved maintainability.
- **Metabase API client** — extracted `_api_get` helper, removed dead code, flattened `create_pulse`, improved error handling.
- **Docker structure** — moved `docker-compose.yml` to `docker/` directory, added `.dockerignore`.
- **Collection export timestamps** — updated to reflect current export state.
- **Directory structure** — removed root stubs and shell scripts, replaced by Makefile targets.

### Fixed

- **Code review observations** — 3 critical, 8 important, and 7 suggestions from multi-axis code review (Tezcatlipoca) across F0–F6, spanning 17 files with +127/-59 lines.
- **Metabase API response handling** — corrected dashboard card creation and SQL parameter serialization.
- **Docker exec flags** — changed `-it` to `-i` for non-interactive Makefile and runtime test contexts.
- **`.dockerignore` patterns** — corrected markdown file exclusion in `docs/`.
- **`.gitignore` paths** — fixed `docker-compose.override.yml` exclusion at correct path.
- **False positives** — reduced noise in `no_secrets_in_commit_messages` test.
- **Percentile calculation** — fixed off-by-one error in `measure_query_performance.py`.
- **Hardcoded credentials** — removed from export and error-handling scripts.
- **Makefile `create-views`** — added fail-fast guard to prevent silent failures.
- **Makefile `setup`** — added `.venv` creation and fixed `data-count` target.
- **Error swallowing** — in data-generator sidecar Makefile targets.
- **Redundant SQL** — removed duplicate `REFRESH MATERIALIZED VIEW` from MV creation scripts.
- **Documentation inconsistencies** — corrected record counts (155K → 182K), partition claims, and `db-init` descriptions across README, User Guide, Technical Guide, and Workflow.
- **Tezcatlipoca F3 findings** — 24 observations resolved including security hardening, DRY violations, and error handling gaps.
- **Tezcatlipoca F4 findings** — 7 observations resolved including robustness improvements and code simplification.
- **Ship review observations** — 4 findings corrected post-release preparation.

### Removed

- **Unused helper** — `dedent_yaml` from test suite.
- **Dead code** — dead imports, unused variables, redundant logic in Metabase API client and test scripts.
- **Root stubs** — empty shell scripts replaced by Makefile targets.
- **Duplicate indexes** — redundant index definitions from schema initialization.
- **Port exposure** — PostgreSQL port 5432 no longer exposed to host; access restricted to Docker network.

### Security

- **PostgreSQL port exposure removed** — database accessible only within Docker internal network.
- **Data-generator sidecar** — synthetic data generation runs in an isolated container, not from the host.
- **Metabase encryption** — `MB_ENCRYPTION_SECRET_KEY` configured via environment variable.
- **Resource limits** — `deploy.resources` constraints added to both services in `docker-compose.yml`.
- **Credentials** — all secrets via `.env` only, never hardcoded in scripts, SQL, or YAML.

### Documentation

- **Architecture (`docs/ARCHITECTURE.md`)** — patterns, component diagram, data flow, SOLID principles, ADR index.
- **Code Style (`docs/CODE_STYLE.md`)** — SQL/Python/Docker/Makefile conventions with pre-commit checklists.
- **Testing Strategy (`docs/TESTING.md`)** — 3-phase testing strategy, frameworks, metrics, query validation guide.
- **Security Guidelines (`docs/SECURITY.md`)** — input validation, secrets management, Docker security, prohibitions.
- **Workflow (`docs/WORKFLOW.md`)** — phase-by-phase implementation plan with Gantt chart, risk matrix, metrics, FTR gates.
- **Execution plans** — separate plans for each phase (F0–F6) with task breakdown and Definition of Done.
- **ADR templates** — reusable templates for future architecture decisions.
- **Spec templates** — reusable templates for feature specifications.
- **Changelog** — human-readable change tracking in Keep a Changelog format.

---

## [v0.1.0] - 2026-07-02

### Added
- Project scaffolding with directory structure (`/docs`, `/scripts`, `/sql`, `/docker`, `/specs`).
- `.gitignore` with patterns for Python, SQL, Docker, and Metabase artifacts.
- `.env.example` with placeholder values for all required environment variables.
- Initial `README.md` with description, tech stack, badges, and quick start.

---

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Unreleased]: https://github.com/Fisherk2/dashboard-metabase-analiticas/compare/v1.0.0...HEAD
[v1.0.0]: https://github.com/Fisherk2/dashboard-metabase-analiticas/releases/tag/v1.0.0
[v0.1.0]: https://github.com/Fisherk2/dashboard-metabase-analiticas/releases/tag/v0.1.0
