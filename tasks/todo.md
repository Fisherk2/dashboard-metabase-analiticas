# TODO — F2: Núcleo

**Fecha:** 2026-07-03 | **Estado:** ✅ COMPLETADO
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Schema Foundation (3.5 h)

- [x] **F2-01** — Crear `scripts/init.sql` con 6 dimensiones (categorias, proveedores, productos, clientes, tiempo, promociones). Aplicar SERIAL PK, UNIQUE en campos clave, CHECK constraints, NOT NULL, COMMENT ON TABLE
- [x] **F2-02** — Añadir 4 hechos (ventas, inventario, devoluciones, logistica) a `scripts/init.sql` con FKs explícitas, CHECK constraints, índices B-tree en cada FK
- [x] **F2-03** — Validar schema: `make db-init` exit 0, `make db-reset` roundtrip funciona, `\dt` muestra 10 tablas

## Checkpoint 1: Schema Foundation ✅

- [x] `make db-init` exit 0 (schema completo)
- [x] `make db-reset` roundtrip funciona (DROP CASCADE + init.sql)
- [x] 10 tablas en `information_schema.tables` (6 dim + 4 hechos)
- [x] Todas las FKs declaradas con `REFERENCES`
- [x] CHECK constraints en precios/stocks/cantidades
- [x] Índices B-tree en cada FK

---

## Slice 2: Data Generation (5 h)

- [x] **F2-04** — Crear `scripts/requirements.txt` con faker>=18.0, psycopg2-binary>=2.9, python-dotenv>=1.0
- [x] **F2-05** — Implementar `scripts/generate_data.py`: clase `DataGenerator`, `connect_db()`, `main()` con transacciones, argparse `--debug`/`--scale`/`--reset`. Métodos `_seed_categorias()`, `_seed_proveedores()`
- [x] **F2-06** — Implementar `_seed_productos()` (5K Pareto 70/30), `_seed_clientes()` (2K), `_seed_tiempo()` (365 días 2026), `_seed_promociones()` (30)
- [x] **F2-07** — Implementar `_seed_ventas()` (100K Pareto 70/30), `_seed_inventario()` (50K), `_seed_devoluciones()` (5K = 5% ventas), `_seed_logistica()` (20K = 20% ventas)
- [x] **F2-08** — Validar: `make data-count` exit 0, `make test-integrity` exit 0, `total = cantidad * precio_unitario` en 100% ventas

## Checkpoint 2: Data Valid ✅

- [x] `make deps` exit 0
- [x] `python scripts/generate_data.py --reset` exit 0
- [x] Volúmenes: 20+50+5000+2000+365+30+100000+50000+5000+20000 = **155,535 registros**
- [x] `make test-integrity` exit 0 (sin huérfanos)
- [x] `make data-count` exit 0 con todos los conteos
- [x] Ventas: `total = cantidad * precio_unitario` en 100% de filas
- [x] Tiempo: 365 días consecutivos (2026-01-01 a 2026-12-31)

---

## Slice 3: Indexes (1.5 h)

- [x] **F2-09** — Crear `sql/indexes/create_indexes.sql` con 9+ índices B-tree (`IF NOT EXISTS`). Mínimo: idx_ventas_{producto,cliente,fecha}_id, idx_inventario_{producto,fecha}_id, idx_devoluciones_venta_id, idx_productos_{categoria,proveedor}_id, idx_ventas_fecha_venta
- [x] **F2-10** — Validar con EXPLAIN ANALYZE las 4 queries críticas de `docs/SCHEMA.md` §4; documentar en `sql/queries_baseline.sql`. Tiempos <500ms con Index Scan

## Checkpoint 3: Indexes Applied ✅

- [x] `make indexes-check` muestra 9+ índices
- [x] Todas las queries críticas usan Index Scan (no Seq Scan)
- [x] Tiempos baseline <500ms (medidos con `\timing`)
- [x] `sql/queries_baseline.sql` documenta el plan de ejecución

---

## Slice 4: Materialized Views (2 h)

- [x] **F2-11** — Crear `sql/views/mv_rotacion_mensual.sql` con CREATE MATERIALIZED VIEW (categoría/mes/año, ventas_totales, ingresos_totales, productos_vendidos). Índices en categoria y (mes, anio)
- [x] **F2-12** — Crear `sql/views/mv_stock_actual.sql` con CASE para estado (ALERTA/PRECAUCION/OK). Índices en estado y producto_id
- [x] **F2-13** — Crear `sql/views/mv_top_productos.sql` (ORDER BY ingresos DESC, top 100). Índice en ingresos_totales DESC
- [x] **F2-14** — Crear `scripts/refresh_materialized_views.sql` con REFRESH MATERIALIZED VIEW para las 3 MVs
- [x] **F2-15** — Validar queries contra MVs <2s con EXPLAIN ANALYZE

## Checkpoint 4: Materialized Views Active ✅

- [x] 3 MVs creadas: `mv_rotacion_mensual`, `mv_stock_actual`, `mv_top_productos`
- [x] `make mv-refresh` exit 0 (refresca las 3)
- [x] Índices en cada MV creados
- [x] Queries contra MVs <2s (validado con EXPLAIN ANALYZE)
- [x] MVs pobladas con datos (`WITH DATA`)

---

## Slice 5: Partitioning (2 h)

- [x] **F2-16** — Crear `sql/partitions/partition_ventas.sql`: DROP ventas CASCADE + CREATE ventas PARTITION BY RANGE (fecha_venta) + 12 particiones mensuales (2026_01 a 2026_12)
- [x] **F2-17** — Recrear índices (IF NOT EXISTS) en tabla particionada. Validar partition pruning con EXPLAIN ANALYZE filtrando por rango de fecha
- [x] **F2-18** — Re-validar queries <2s post-particion. Refrescar MVs. Documentar comparación en `docs/PERFORMANCE.md`

## Checkpoint 5: Partitioning Active ✅

- [x] `ventas` es tabla particionada con 12 particiones mensuales
- [x] `pg_partition_tree('ventas')` retorna 12 hijos + 1 padre
- [x] EXPLAIN muestra **partition pruning** en queries con filtro fecha
- [x] Índices recreados en tabla particionada
- [x] MVs refrescadas tras recreación de `ventas`
- [x] Queries siguen <2s (performance mantenida o mejorada)

---

## Slice 6: Test Suite (2.5 h)

- [x] **F2-19** — Crear `tests/test_f2.py` con **tests estáticos** (≥15): existencia de archivos SQL/Python, regex CREATE TABLE para 10 tablas, AST parse de generate_data.py, MVs definidas
- [x] **F2-20** — Añadir **tests runtime** (≥25) con `@pytest.mark.runtime` (skip si no Docker): `make db-init`, conteos ≥ esperados, `make test-integrity`, EXPLAIN ANALYZE <2s para MVs, `pg_partition_tree` 12 particiones, REFRESH MATERIALIZED VIEW

## Checkpoint 6: F2 Complete ✅ (Ready para F3)

- [x] `make test` muestra F0 (72) + F1 (67) + F2 (≥40) = **≥179 tests passing**
- [x] FTR de F2 pasa checklist de `docs/WORKFLOW.md` §5 (Schema + datos + queries optimizadas)
- [x] Roundtrip `make db-reset && make data-generate && make mv-refresh` funciona
- [x] `make validate && make up && make db-init && make data-generate && make mv-refresh` es la ruta crítica
- [x] `git log --oneline` muestra 6-8 commits atómicos para F2
- [x] Working tree limpio

---

## Progreso

- **Total tareas:** 20
- **Tareas completadas:** 20/20
- **Checkpoints pasados:** 6/6
- **Tiempo estimado:** ~12h (1.5 días)
- **Tests objetivo:** 72 (F0) + 67 (F1) + ≥40 (F2) = **≥179 tests**
- **Commits objetivo:** 6-8 atómicos
- **Alcance confirmado:** Particionamiento ✅, Logistica completa ✅, test_f2.py completo ✅
