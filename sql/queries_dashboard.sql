-- =============================================================================
-- queries_dashboard.sql — Queries de paneles Metabase con EXPLAIN ANALYZE
-- =============================================================================
-- Fecha: 2026-07-06 | Fase: F3 (Interfaces)
-- Propósito: Documentar y validar el rendimiento de las 4 queries del dashboard.
-- Tiempo objetivo: <2s usando vistas materializadas + índices.
-- =============================================================================

-- =============================================================================
-- Query 1: Rotación por Categoría
-- Panel: Rotación por Categoría (bar chart)
-- MV: mv_rotacion_mensual
-- =============================================================================

EXPLAIN ANALYZE
SELECT
    categoria,
    mes,
    anio,
    ventas_totales,
    ingresos_totales,
    productos_vendidos
FROM mv_rotacion_mensual
WHERE anio = 2026
  AND mes = 'Marzo'
ORDER BY ventas_totales DESC;

-- Tiempo esperado: <50ms (MV + índice idx_mv_rotacion_mes_anio)
-- Plan: Index Scan on mv_rotacion_mensual using idx_mv_rotacion_mes_anio


-- =============================================================================
-- Query 2: Stock Actual vs Mínimo
-- Panel: Stock Actual vs Mínimo (table with conditional formatting)
-- MV: mv_stock_actual
-- =============================================================================

EXPLAIN ANALYZE
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

-- Tiempo esperado: <50ms (MV + índice idx_mv_stock_estado)
-- Plan: Index Scan on mv_stock_actual using idx_mv_stock_estado


-- =============================================================================
-- Query 3: Top 10 Productos por Ventas
-- Panel: Top 10 Productos por Ventas (row chart)
-- MV: mv_top_productos
-- =============================================================================

EXPLAIN ANALYZE
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

-- Tiempo esperado: <20ms (MV + índice idx_mv_top_productos_ranking)
-- Plan: Index Scan Backward on mv_top_productos using idx_mv_top_productos_ranking


-- =============================================================================
-- Query 4: Alertas de Stock Mínimo
-- Panel: Alertas de Stock Mínimo (table)
-- Tablas base: productos + proveedores
-- Nota: Usa tablas base porque la lógica de stock mínimo no está en las MVs.
-- =============================================================================

EXPLAIN ANALYZE
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

-- Tiempo esperado: <200ms (índices en productos.proveedor_id, proveedores.id)
-- Plan: Index Scan on productos + Index Scan on proveedores


-- =============================================================================
-- Comparación de rendimiento: con MV vs sin MV
-- =============================================================================

-- Sin MV (consulta directa contra tablas base)
-- SELECT
--     c.nombre AS categoria,
--     t.mes,
--     t.anio,
--     SUM(v.cantidad) AS ventas_totales,
--     SUM(v.total) AS ingresos_totales,
--     COUNT(DISTINCT v.producto_id) AS productos_vendidos
-- FROM ventas v
-- JOIN productos p ON v.producto_id = p.id
-- JOIN categorias c ON p.categoria_id = c.id
-- JOIN tiempo t ON v.fecha_id = t.id
-- WHERE t.anio = 2026 AND t.mes = '03'
-- GROUP BY c.nombre, t.mes, t.anio;
-- Tiempo sin MV: ~200ms (con índices) a ~1.5s (sin índices)
-- Tiempo con MV: <50ms

-- Con MV (query optimizada):
-- SELECT * FROM mv_rotacion_mensual WHERE anio = 2026 AND mes = '03';
-- Tiempo: <50ms — mejora de 4x-30x vs tablas base
