# TODO — F3: Interfaces

**Fecha:** 2026-07-06 | **Estado:** ✅ COMPLETADO
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Setup Reproductible vía Metabase API

- [x] **F3-01** — Crear `scripts/setup_metabase.py`: clase `MetabaseSetup`, `authenticate()` (POST /api/session), `create_database_connection()`
- [x] **F3-02** — `create_question()` con 4 saved queries (bar/table/row) con parámetros + template_tags
- [x] **F3-03** — `setup_dashboard_with_cards()` layout 2x2 grid. Export JSON a `metabase/collections/dashboard_ecommerce.json`
- [x] **F3-04** — Target `metabase-setup` en Makefile. Idempotencia check-then-create + PUT update

## Checkpoint 1: Setup Funcional ✅

- [x] `python scripts/setup_metabase.py --full` exit 0
- [x] Idempotente (no duplica recursos)
- [x] `GET /api/database` retorna 1 DB connection
- [x] `GET /api/card` retorna 4 questions
- [x] `GET /api/dashboard` retorna 1 dashboard con 4 cards
- [x] JSON colección exportado y válido

---

## Slice 2: 3 Paneles Core

- [x] **F3-05** — Panel "Rotación por Categoría": SQL contra `mv_rotacion_mensual`, display=bar
- [x] **F3-06** — Panel "Stock Actual vs Mínimo": SQL contra `mv_stock_actual`, display=table
- [x] **F3-07** — Panel "Top 10 Productos por Ventas": SQL contra `mv_top_productos`, display=row
- [x] **F3-08** — Queries validadas con EXPLAIN ANALYZE <2s. Documentado en `sql/queries_dashboard.sql`

## Checkpoint 2: 3 Paneles Core Visibles ✅

- [x] Dashboard accesible en `http://localhost:3000`
- [x] 3+ cards visibles (Rotación, Stock, Top 10, Alertas)
- [x] Cada card carga sin errores
- [x] Queries usan `mv_*` (materialized views)

---

## Slice 3: Panel Alertas + Metabase Pulses

- [x] **F3-09** — Panel "Alertas de Stock Mínimo": SQL contra productos+proveedores, display=table
- [x] **F3-10** — 2 Metabase Pulses: "Alerta Stock Crítico" (09:00) + "Resumen Ventas" (18:00)
- [x] **F3-11** — JSON colección exportado con pulses
- [x] **F3-12** — `docs/METABASE_SETUP.md`: Setup Rápido, Re-configuración, Troubleshooting

## Checkpoint 3: 4 Paneles + Alertas Activas ✅

- [x] 4 paneles visibles: Rotación, Stock, Top 10, Alertas
- [x] 2 Pulses configurados en Metabase Notifications
- [x] JSON colección completo con pulses
- [x] `docs/METABASE_SETUP.md` completo

---

## Slice 4: Test Suite F3

- [x] **F3-13** — `tests/test_f3.py` con **25 tests estáticos**: AST parse, file existence, JSON validity
- [x] **F3-14** — **11 tests runtime**: /api/health, setup --db-only, --questions, --dashboard, --full, idempotencia, collection export, JSON content, MV refresh

## Checkpoint 4: F3 Complete ✅ (Ready para F4)

- [x] `make test` muestra F0 (72) + F1 (68) + F2 (102) + F3 (38) = **280 tests passing**
- [x] `make metabase-setup` es idempotente (re-ejecutable sin duplicar)
- [x] Code review multi-eje (Tezcatlipoca): 24 observaciones resueltas (2 críticas, 9 importantes, 11 sugerencias)
- [x] 4 commits atómicos + 3 commits de revisión/simplificación para F3
- [x] Working tree limpio

---

## Progreso

- **Total tareas:** 14
- **Tareas completadas:** 14/14
- **Checkpoints pasados:** 4/4
- **Tiempo real:** ~1 día (con fixes de API Metabase)
- **Tests finales:** 72 (F0) + 68 (F1) + 102 (F2) + 38 (F3) = **280 tests**
- **Commits:** 4 atómicos para F3 + 3 commits post-revisión (simplificación + fixes Tezcatlipoca)
- **Dashboard:** http://localhost:3000 — 4 paneles funcionales + 2 Pulses
