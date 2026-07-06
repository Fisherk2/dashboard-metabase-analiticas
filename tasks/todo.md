# TODO — F4: Pruebas

**Fecha:** 2026-07-06 | **Estado:** 📋 LISTO PARA EJECUTAR
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Performance Validation

- [ ] **F4-01** — Crear `sql/queries_performance.sql` con `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` de las 4 queries (separado del F3)
- [ ] **F4-02** — `scripts/measure_query_performance.py`: corre cada query N=10 veces, calcula p50/p95/p99, exit 1 si p95 >2s
- [ ] **F4-03** — Reemplazar target `make test-queries` (placeholder) por invocación al script

## Checkpoint 1: Performance Validado ✅

- [ ] `make test-queries` exit 0
- [ ] p95 <2s en las 4 queries
- [ ] Plan de ejecución usa Index Scan (no Seq Scan) en tablas >1000 filas
- [ ] `sql/queries_performance.sql` documenta planes esperados vs reales

---

## Slice 2: Export Validation

- [ ] **F4-04** — `scripts/validate_dashboard_exports.py`: descarga CSV + PNG de cada card via Metabase API, valida magic bytes + CSV parseable
- [ ] **F4-05** — `docs/METABASE_EXPORTS.md`: documenta endpoints, parámetros, troubleshooting

## Checkpoint 2: Export Validado ✅

- [ ] 4/4 cards exportan a CSV con datos válidos
- [ ] 4/4 cards exportan a PNG con magic bytes correctos
- [ ] `docs/METABASE_EXPORTS.md` completo y revisado
- [ ] Roundtrip `make metabase-export && make test` exit 0

---

## Slice 3: Resilience Validation

- [ ] **F4-06** — `scripts/test_persistence.sh`: ejecuta `make destroy && make setup && make metabase-setup && make test` (destructivo, opt-in)
- [ ] **F4-07** — `scripts/test_error_handling.py`: con PG caído, Metabase retorna error 500/503 con mensaje claro (no opaco)

## Checkpoint 3: Resilience Validado ✅

- [ ] Roundtrip `make destroy && make setup && make metabase-setup && make test` exit 0
- [ ] Con PostgreSQL caído, Metabase retorna error 500/503 con mensaje útil
- [ ] Tras `docker start metabase-postgres`, Metabase se reconecta sin intervención manual
- [ ] Roundtrip completo tarda <10 min

---

## Slice 4: Test Suite F4

- [ ] **F4-08** — `tests/test_f4.py`: tests estáticos (file existence, AST) + runtime (`@pytest.mark.runtime`: export integrity, roundtrip opt-in)

## Checkpoint 4: F4 Complete ✅ (Ready para F5)

- [ ] `make test` muestra F0 (72) + F1 (68) + F2 (102) + F3 (38) + F4 (≥15) = **≥295 tests passing**
- [ ] FTR de F4 pasa checklist de `docs/WORKFLOW.md` §5
- [ ] Roundtrip `make destroy && make setup && make metabase-setup && make test` exit 0
- [ ] `git log --oneline` muestra 4-5 commits atómicos para F4
- [ ] Working tree limpio

---

## Progreso

- **Total tareas:** 8
- **Tareas completadas:** 0/8
- **Checkpoints pasados:** 0/4
- **Tiempo estimado:** ~3.5 horas
- **Commits esperados:** 4-5 atómicos
- **Tests objetivo:** 280 (F0-F3) + ≥15 (F4) = ≥295
