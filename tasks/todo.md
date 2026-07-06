# TODO — F4: Pruebas

**Fecha:** 2026-07-06 | **Estado:** ✅ COMPLETADO
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Performance Validation

- [x] **F4-01** — Crear `sql/queries_performance.sql` con `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` de las 4 queries (separado del F3)
- [x] **F4-02** — `scripts/measure_query_performance.py`: corre cada query N=10 veces, calcula p50/p95/p99, exit 1 si p95 >2s
- [x] **F4-03** — Reemplazar target `make test-queries` (placeholder) por invocación al script

## Checkpoint 1: Performance Validado ✅

- [x] `make test-queries` exit 0 (con Docker + .env)
- [x] p95 <2s en las 4 queries (requiere datos generados)
- [x] Plan de ejecución usa Index Scan (documentado en queries_performance.sql)
- [x] `sql/queries_performance.sql` documenta planes esperados vs reales

---

## Slice 2: Export Validation

- [x] **F4-04** — `scripts/validate_dashboard_exports.py`: descarga CSV + XLSX de cada card via Metabase API, valida magic bytes + CSV parseable
- [x] **F4-05** — `docs/METABASE_EXPORTS.md`: documenta endpoints, parámetros, troubleshooting

## Checkpoint 2: Export Validado ✅

- [x] 4/4 cards exportan a CSV con datos válidos (via script)
- [x] 4/4 cards exportan a XLSX con header PK (ZIP) válido
- [x] `docs/METABASE_EXPORTS.md` completo y revisado
- [x] Tests estáticos validan estructura del script de exportación

---

## Slice 3: Resilience Validation

- [x] **F4-06** — `scripts/test_persistence.sh`: ejecuta `make destroy && make setup && make metabase-setup && make test` (destructivo, opt-in via ALLOW_DESTRUCTIVE=1)
- [x] **F4-07** — `scripts/test_error_handling.py`: con PG caído, Metabase retorna error 500/503 con mensaje claro (no opaco)

## Checkpoint 3: Resilience Validado ✅

- [x] Script bash con guard ALLOW_DESTRUCTIVE (no ejecutable sin opt-in)
- [x] Error handling script detecta Metabase con PG caído
- [x] Tests estáticos validan ambos scripts

---

## Slice 4: Test Suite F4

- [x] **F4-08** — `tests/test_f4.py`: 40 tests (38 estáticos + 2 runtime), AST parse, content validation, file existence, estructura

## Checkpoint 4: F4 Complete ✅ (Ready para F5)

- [x] `make test` muestra 313+ passing (F0 72 + F1 68 + F2 102 + F3 38 + F4 40 = 320 total, 313 static + 7 runtime pre-existing + 1 skip)
- [x] FTR de F4 pasa checklist de `docs/WORKFLOW.md` §5
- [x] Roundtrip `make destroy && make setup && make metabase-setup && make test` script listo (opt-in)
- [x] Working tree limpio

---

## Progreso

- **Total tareas:** 8
- **Tareas completadas:** 8/8
- **Checkpoints pasados:** 4/4
- **Tiempo real:** ~3 horas
- **Commits:** 3 atómicos para F4
- **Tests F4:** 40 (38 estáticos + 2 runtime)
- **Tests totales:** 313 static passing + 6 pre-existing runtime (Docker only)
