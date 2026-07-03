# SPEC: Dashboard Metabase + Colección Analítica para E-commerce v1.0

## Objective

Build a reproducible **analytical dashboard** connected to PostgreSQL that visualizes KPIs of inventory, rotation, and minimum stock alerts for a simulated e-commerce environment. The project demonstrates:

- Star schema design for OLAP workloads in PostgreSQL
- SQL query optimization (target: <2s per view)
- Metabase configuration as a BI visualization tool
- Synthetic data generation with Python + Faker
- Professional, reproducible documentation for portfolio purposes

**Target user:** Fisherk2 (portfolio demonstration for employers/clients)

## Tech Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| PostgreSQL | 15+ | Analytical database (star schema, materialized views, partitioning) |
| Metabase | Latest (OSS) | BI visualization (dashboards, queries, export) |
| Docker Compose | 20+ | Service orchestration (reproducibility) |
| Python | 3.8+ | Synthetic data generation |
| Faker | Latest | Realistic fake data |
| psycopg2 | Latest | PostgreSQL adapter for Python |

## Commands

```bash
# Infrastructure
docker-compose up -d                    # Start PostgreSQL + Metabase
docker-compose down                     # Stop all services
docker-compose logs -f postgres         # View PostgreSQL logs

# Database
docker exec -it postgres psql -U admin -d ecommerce  # Connect to DB
psql -h localhost -p 5432 -U admin -d ecommerce -f scripts/init.sql  # Run schema

# Data Generation
pip install -r scripts/requirements.txt  # Install Python dependencies
python scripts/generate_data.py          # Generate synthetic data
python scripts/generate_data.py --debug  # Run with debug logging

# Materialized Views
psql -h localhost -p 5432 -U admin -d ecommerce -f scripts/refresh_materialized_views.sql

# Validation
docker-compose config                    # Validate docker-compose.yml
EXPLAIN ANALYZE <query>;                 # Validate query performance in psql
```

## Project Structure

```
/
├── AGENTS.md                       # Lean project index (links to all docs)
├── SPEC.md                         # This file — central specification
├── README.md                       # User-facing documentation + badges
├── .env                            # Environment variables (NOT committed)
├── .gitignore                      # Git ignore patterns
│
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md             # Architecture patterns + ADR index
│   ├── SCHEMA.md                   # Database schema (star schema detail)
│   ├── APPFLOW.md                  # Navigation flows
│   ├── CODE_STYLE.md               # SQL + Python style conventions
│   ├── TESTING.md                  # Testing strategy
│   ├── SECURITY.md                 # Security guidelines
│   ├── WORKFLOW.md                 # Phase-by-phase workflow
│   ├── PRD.md                      # Product Requirements
│   ├── TRD.md                      # Technical Requirements
│   └── TECH_DEBT.md                # Technical debt register
│
├── specs/                          # Modular feature specifications
│   ├── spec-infrastructure.md      # Docker Compose setup
│   ├── spec-star-schema.md         # Star schema design
│   ├── spec-data-generation.md     # Python data generation
│   ├── spec-sql-optimization.md    # Query optimization
│   ├── spec-metabase-dashboards.md # Dashboard configuration
│   └── adr/                        # Architecture Decision Records
│       ├── adr-001-postgresql.md
│       ├── adr-002-metabase.md
│       ├── adr-003-star-schema.md
│       └── adr-004-docker-compose.md
│
├── scripts/                        # Scripts
│   ├── generate_data.py            # Synthetic data generation
│   ├── requirements.txt            # Python dependencies
│   ├── init.sql                    # Schema initialization
│   └── refresh_materialized_views.sql
│
├── docker/                         # Docker configuration
│   └── docker-compose.yml          # Service orchestration
│
├── sql/                            # SQL artifacts
│   ├── views/                      # Materialized views
│   ├── indexes/                    # Index creation scripts
│   └── partitions/                 # Partitioning scripts
│
└── metabase/                       # Metabase configuration (optional)
    └── collections/                # Exported dashboard collections
```

## Code Style

See **[docs/CODE_STYLE.md](docs/CODE_STYLE.md)** for full conventions.

**Key rules:**
- **SQL:** Keywords in UPPERCASE, 4-space indent, explicit JOINs, descriptive English column names
- **Python:** PEP 8, `snake_case` for variables/functions, Google-style docstrings
- **Naming:** Tables `snake_case`, indexes `idx_<table>_<column>`, materialized views `mv_<description>`
- **Credentials:** NEVER hardcoded — always via `.env` variables

## Testing Strategy

See **[docs/TESTING.md](docs/TESTING.md)** for full strategy.

| Phase | Tool | Success Criteria |
|-------|------|-----------------|
| Unit (SQL) | `EXPLAIN ANALYZE` | All queries <2s |
| Integration | Metabase + PostgreSQL | Dashboards display correct data |
| Integration | pytest | Data generation produces valid records |
| E2E | Metabase | Full dashboard flow works |
| Performance | `pg_stat_statements` | Queries <2s with 200K records/table |

## Boundaries

### Always Do
- Use `.env` for all credentials (POSTGRES_PASSWORD, etc.)
- Validate queries with `EXPLAIN ANALYZE` before implementing
- Use explicit JOINs (INNER JOIN, LEFT JOIN) — never implicit
- Use transactions (BEGIN/COMMIT) in Python insertion scripts
- Create indexes on columns used in WHERE, JOIN, GROUP BY
- Document schema changes with migration naming convention

### Ask First
- Changing the star schema structure (adding/removing tables)
- Adding new Python dependencies
- Modifying Docker network or port configuration
- Changing materialized view definitions

### Never Do
- Hardcode credentials in any file (SQL, Python, YAML)
- Use `SELECT *` — always list columns explicitly
- Expose PostgreSQL to `0.0.0.0` or the internet
- Use `root`/`superuser` for application connections
- Run queries without indexes on critical columns
- Implement business logic outside PostgreSQL (no app-level calculations)
- Use implicit JOINs (`FROM a, b WHERE a.id = b.id`)

## Success Criteria

- [ ] `docker-compose up -d` starts PostgreSQL + Metabase without errors
- [ ] Metabase connects to PostgreSQL via JDBC successfully
- [ ] `generate_data.py` populates: 50K–200K fact records, 1K–10K dimension records
- [ ] Star schema has 8+ tables (3+ fact, 5+ dimension)
- [ ] Materialized views created and refreshable (`mv_rotacion_mensual`, etc.)
- [ ] 3+ Metabase dashboards display correct data (rotation, stock, sales)
- [ ] All dashboard queries load in <2s (validated with `EXPLAIN ANALYZE`)
- [ ] Export to PNG/CSV works for all panels
- [ ] Project is reproducible: works on a fresh `docker-compose up`

## Open Questions

| # | Question | Decision |
|---|----------|----------|
| 1 | Include optional alert configuration in Metabase? | Defer to F3 |
| 2 | Record video tutorial for portfolio? | Optional (F5) |
| 3 | Partition `ventas` table by date range? | Recommended for performance demo |
| 4 | Include `logistica` and `devoluciones` in dashboards? | If time permits (nice-to-have) |
