# TODO — F3: Interfaces

**Fecha:** 2026-07-06 | **Estado:** 📋 LISTO PARA EJECUTAR
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Setup Reproductible vía Metabase API (3 h)

- [x] **F3-01** — Crear `scripts/setup_metabase.py`: clase `MetabaseSetup`, `authenticate()` (POST /api/session), `create_database_connection()` con .env. Target: PostgreSQL host=postgres port=5432
- [x] **F3-02** — Añadir `create_question(name, sql, db_id, display_type)`: crea 4 saved queries con display types (bar/table/row). SQL con `{{variable}}` syntax
- [x] **F3-03** — Añadir `create_dashboard(name)` + `add_card_to_dashboard()`: layout 2x2 grid. Export JSON completo a `metabase/collections/dashboard_ecommerce.json`
- [x] **F3-04** — Añadir target `metabase-setup` al Makefile. Validar idempotencia: check-then-create (no duplicar DB/questions/dashboard)

## Checkpoint 1: Setup Funcional ⏳

- [ ] `make metabase-setup` exit 0 (setup completo desde cero) — Pendiente runtime
- [ ] `make metabase-setup` segunda vez no duplica (idempotente) — Pendiente runtime
- [ ] `GET /api/database` retorna 1 DB connection — Pendiente runtime
- [ ] `GET /api/card` retorna 4 questions — Pendiente runtime
- [ ] `GET /api/dashboard` retorna 1 dashboard con 4 cards — Pendiente runtime
- [ ] `metabase/collections/dashboard_ecommerce.json` existe con JSON válido ✅

---

## Slice 2: 3 Paneles Core (Rotación, Stock, Top 10) (2 h)

- [ ] **F3-05** — Panel "Rotación por Categoría": SQL contra `mv_rotacion_mensual`, display=bar, filtros año/mes dropdown
- [ ] **F3-06** — Panel "Stock Actual vs Mínimo": SQL contra `mv_stock_actual`, display=table con formateo condicional por estado, filtros categoría/proveedor/estado
- [ ] **F3-07** — Panel "Top 10 Productos por Ventas": SQL contra `mv_top_productos`, display=row, filtro categoría dropdown
- [ ] **F3-08** — Validar queries con EXPLAIN ANALYZE: 4 queries <2s. Documentar en `sql/queries_dashboard.sql`

## Checkpoint 2: 3 Paneles Core Visibles ✅

- [ ] Dashboard accesible en `http://localhost:3000/dashboard/...`
- [ ] 3 cards visibles: Rotación, Stock, Top 10
- [ ] Cada card carga en <2s (medido con `curl -w "%{time_total}\n"`)
- [ ] Filtros dropdown funcionan (año, mes, categoría, proveedor, estado)
- [ ] Export PNG y CSV funciona en cada panel (manual + verificado)
- [ ] Queries usan `mv_*` (no tablas base) — verificado con EXPLAIN ANALYZE

---

## Slice 3: Panel Alertas + Metabase Pulses (2 h)

- [ ] **F3-09** — Panel "Alertas de Stock Mínimo": SQL contra productos+proveedores, display=table, variable `{{umbral_multiplier}}` editable
- [ ] **F3-10** — Configurar 2 Metabase Pulses vía API: Pulse 1 "Alerta Stock Crítico" (diario 09:00, email), Pulse 2 "Resumen Ventas Diarias" (diario 18:00, email)
- [ ] **F3-11** — Re-export JSON colección: incluye cards + dashboard + pulses. Verificar JSON parseable
- [ ] **F3-12** — Crear `docs/METABASE_SETUP.md`: Setup Rápido, Re-configuración, Troubleshooting, FAQ

## Checkpoint 3: 4 Paneles + Alertas Activas ✅

- [ ] 4to panel "Alertas de Stock Mínimo" visible en dashboard
- [ ] Variable `{{umbral_multiplier}}` funciona (cambia resultados en vivo)
- [ ] 2 Pulses listados en Metabase → Notifications
- [ ] Pulse 1 schedule: diario 09:00
- [ ] Pulse 2 schedule: diario 18:00
- [ ] JSON colección incluye pulses
- [ ] `docs/METABASE_SETUP.md` completo y revisado

---

## Slice 4: Test Suite F3 (2 h)

- [ ] **F3-13** — Crear `tests/test_f3.py` con **tests estáticos** (≥15): existencia de archivos, AST parse de setup_metabase.py (clase MetabaseSetup + métodos), JSON colección válido
- [ ] **F3-14** — Añadir **tests runtime** (≥15) con `@pytest.mark.runtime`: /api/health, setup_metabase.py --db-only, GET /api/database, /api/card, /api/dashboard, /api/pulse, EXPLAIN ANALYZE <2s

## Checkpoint 4: F3 Complete ✅ (Ready para F4)

- [ ] `make test` muestra F0 (72) + F1 (67) + F2 (40) + F3 (≥30) = **≥209 tests passing**
- [ ] FTR de F3 pasa checklist de `docs/WORKFLOW.md` §5 (Paneles + queries <2s + export)
- [ ] `make metabase-setup` es idempotente (re-ejecutable sin duplicar)
- [ ] Roundtrip `make metabase-setup && make metabase-export && make test` funciona
- [ ] `git log --oneline` muestra 4-5 commits atómicos para F3
- [ ] Working tree limpio

---

## Progreso

- **Total tareas:** 14
- **Tareas completadas:** 0/14
- **Checkpoints pasados:** 0/4
- **Tiempo estimado:** ~6.5h (1 día)
- **Tests objetivo:** 72 (F0) + 67 (F1) + 40 (F2) + ≥30 (F3) = **≥209 tests**
- **Commits objetivo:** 4-5 atómicos
- **Alcance confirmado:** Metabase API programático ✅, 4 paneles ✅, 2 Pulses ✅, JSON export ✅, docs troubleshooting ✅
