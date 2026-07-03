# AGENTS.MD – Dashboard Metabase + Colección Analítica para E-commerce

**Fecha:** 2026-07-03 | **Autor:** Fisherk2 | **Versión:** 2.1 (F0+F1 done, F2 ready)

Panel visual conectado a PostgreSQL que muestra KPIs de inventario, rotación y alertas de stock mínimo para e-commerce simulado. Proyecto de portafolio con datos sintéticos.

## Quick Reference

| Resource | Path | Description |
|----------|------|-------------|
| **Specification** | [SPEC.md](SPEC.md) | Central spec — objective, commands, boundaries, success criteria |
| **Workflow** | [docs/WORKFLOW.md](docs/WORKFLOW.md) | Phase-by-phase implementation plan (F0–F6) |
| **Database Schema** | [docs/SCHEMA.md](docs/SCHEMA.md) | Star schema design (ER diagram, tables, queries) |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Patterns, diagrams, ADR index |
| **Navigation Flows** | [docs/APPFLOW.md](docs/APPFLOW.md) | User flows, navigation matrix, error handling |
| **Code Style** | [docs/CODE_STYLE.md](docs/CODE_STYLE.md) | SQL + Python conventions |
| **Testing** | [docs/TESTING.md](docs/TESTING.md) | Testing strategy (unit, integration, E2E, performance) |
| **Security** | [docs/SECURITY.md](docs/SECURITY.md) | Input validation, secrets management, prohibitions |
| **Product Requirements** | [docs/PRD.md](docs/PRD.md) | Functional and non-functional requirements |
| **Technical Requirements** | [docs/TRD.md](docs/TRD.md) | Technical constraints and decisions |
| **Technical Debt** | [docs/TECH_DEBT.md](docs/TECH_DEBT.md) | Debt register |

## Feature Specifications (`specs/`)

| Spec | Description |
|------|-------------|
| [spec-infrastructure.md](specs/spec-infrastructure.md) | Docker Compose, PostgreSQL + Metabase services |
| [spec-star-schema.md](specs/spec-star-schema.md) | Star schema tables, constraints, indexes |
| [spec-data-generation.md](specs/spec-data-generation.md) | Python + Faker synthetic data |
| [spec-sql-optimization.md](specs/spec-sql-optimization.md) | Materialized views, partitioning, indexes |
| [spec-metabase-dashboards.md](specs/spec-metabase-dashboards.md) | Dashboard panels, filters, export |
| [spec-makefile.md](specs/spec-makefile.md) | Makefile task automation |

## Architecture Decision Records (`specs/adr/`)

| ADR | Decision |
|-----|----------|
| [adr-001](specs/adr/adr-001-postgresql.md) | PostgreSQL 15+ as analytical database |
| [adr-002](specs/adr/adr-002-metabase.md) | Metabase OSS as BI tool |
| [adr-003](specs/adr/adr-003-star-schema.md) | Star schema for OLAP |
| [adr-004](specs/adr/adr-004-docker-compose.md) | Docker Compose for orchestration |

## Key Rules (Summary)

- All business logic lives in PostgreSQL (SQL) — no app-level calculations
- Credentials via `.env` only — never hardcoded
- Validate all queries with `EXPLAIN ANALYZE` (target: <2s)
- Explicit JOINs only — never implicit
- Transactions (BEGIN/COMMIT) in all Python DB scripts
- Synthetic data only — no production use
