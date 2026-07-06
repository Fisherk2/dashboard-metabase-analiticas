-- =============================================================================
-- queries_performance.sql — EXPLAIN ANALYZE validation for F4
-- =============================================================================
-- Fecha: 2026-07-06 | Fase: F4 (Pruebas)
-- Propósito: Validar plan de ejecución y rendimiento de las 4 queries del
--            dashboard con EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT).
--
-- Tiempo objetivo: p95 <2s en las 4 queries.
-- Uso:
--   1. Conectar a PostgreSQL: make db-shell
--   2. Copiar cada bloque y ejecutar en psql
--   3. Verificar plan, buffers y tiempos
--   4. Documentar resultados reales en la sección "Resultados"
-- =============================================================================


-- =============================================================================
-- Query 1: Rotación por Categoría
-- Panel:  Rotación por Categoría (bar chart)
-- MV:     mv_rotacion_mensual
-- =============================================================================

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    categoria,
    mes,
    anio,
    ventas_totales,
    ingresos_totales,
    productos_vendidos
FROM mv_rotacion_mensual
WHERE anio = '2026'
  AND mes = '03'
ORDER BY ventas_totales DESC;

-- Resultados esperados:
--   Plan: Index Scan on mv_rotacion_mensual using idx_mv_rotacion_mes_anio
--   Tiempo: <50ms
--
-- Resultados reales:
--   (completar tras ejecución con psql)
--   Tiempo planificación: ___ms
--   Tiempo ejecución: ___ms
--   Buffers: shared hit=__ read=__
--   Filas: __


-- =============================================================================
-- Query 2: Stock Actual vs Mínimo
-- Panel:  Stock Actual vs Mínimo (table with conditional formatting)
-- MV:     mv_stock_actual
-- =============================================================================

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    producto_id,
    nombre,
    categoria,
    proveedor,
    stock_actual,
    stock_minimo,
    estado
FROM mv_stock_actual
WHERE estado IN ('ALERTA', 'PRECAUCION')
ORDER BY stock_actual ASC;

-- Resultados esperados:
--   Plan: Index Scan on mv_stock_actual using idx_mv_stock_estado
--   Tiempo: <50ms
--
-- Resultados reales:
--   (completar tras ejecución con psql)
--   Tiempo planificación: ___ms
--   Tiempo ejecución: ___ms
--   Buffers: shared hit=__ read=__
--   Filas: __


-- =============================================================================
-- Query 3: Top 10 Productos por Ventas
-- Panel:  Top 10 Productos por Ventas (row chart)
-- MV:     mv_top_productos
-- =============================================================================

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    producto_id,
    nombre,
    categoria,
    unidades_vendidas,
    ingresos_totales,
    numero_ventas
FROM mv_top_productos
ORDER BY ingresos_totales DESC
LIMIT 10;

-- Resultados esperados:
--   Plan: Index Scan Backward on mv_top_productos using idx_mv_top_productos_ranking
--   Tiempo: <20ms
--
-- Resultados reales:
--   (completar tras ejecución con psql)
--   Tiempo planificación: ___ms
--   Tiempo ejecución: ___ms
--   Buffers: shared hit=__ read=__
--   Filas: __


-- =============================================================================
-- Query 4: Alertas de Stock Mínimo
-- Panel:  Alertas de Stock Mínimo (table)
-- Tablas base: productos + proveedores
-- Nota: Usa tablas base porque la lógica de stock mínimo no está en las MVs.
-- =============================================================================

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    p.id,
    p.nombre,
    p.stock_actual,
    p.stock_minimo,
    pr.nombre AS proveedor,
    pr.email AS contacto_proveedor
FROM productos p
JOIN proveedores pr ON p.proveedor_id = pr.id
WHERE p.stock_actual <= p.stock_minimo
ORDER BY p.stock_actual ASC;

-- Resultados esperados:
--   Plan: Index Scan on productos + Index Scan on proveedores
--   Tiempo: <200ms
--
-- Resultados reales:
--   (completar tras ejecución con psql)
--   Tiempo planificación: ___ms
--   Tiempo ejecución: ___ms
--   Buffers: shared hit=__ read=__
--   Filas: __
--   Nested Loop: ___


-- =============================================================================
-- Resumen de Resultados
-- =============================================================================
-- Después de ejecutar todas las queries, documentar aquí los tiempos reales:
--
-- | Query | Plan | Tiempo | Buffers | <2s? |
-- |-------|------|--------|---------|------|
-- | 1 Rotación | Index Scan | ___ms | hit=__, read=__ | ✅ |
-- | 2 Stock | Index Scan | ___ms | hit=__, read=__ | ✅ |
-- | 3 Top 10 | Index Scan Backward | ___ms | hit=__, read=__ | ✅ |
-- | 4 Alertas | Nested Loop + Index Scans | ___ms | hit=__, read=__ | ✅ |
--
-- Todos cumplen <2s: ✅ / ❌
