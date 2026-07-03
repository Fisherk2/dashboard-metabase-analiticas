-- =============================================================================
-- Baseline Queries — Consultas críticas del dashboard
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
--
-- 4 queries críticas que los dashboards de Metabase usarán.
-- Validar con EXPLAIN ANALYZE antes de implementar en F3.
-- Tiempo objetivo: <500ms con índices, <2s con MVs.
-- =============================================================================

-- 1. Rotación por Categoría (Mensual)
EXPLAIN ANALYZE
SELECT
    c.nombre AS categoria,
    t.mes,
    t.anio,
    SUM(v.cantidad) AS ventas_totales,
    SUM(v.total) AS ingresos_totales,
    COUNT(DISTINCT v.producto_id) AS productos_vendidos
FROM ventas v
JOIN productos p ON v.producto_id = p.id
JOIN categorias c ON p.categoria_id = c.id
JOIN tiempo t ON v.fecha_id = t.id
GROUP BY c.nombre, t.mes, t.anio
ORDER BY t.anio DESC, t.mes DESC, ventas_totales DESC;

-- 2. Stock Actual vs Mínimo (Alertas)
EXPLAIN ANALYZE
SELECT
    p.id,
    p.nombre,
    p.stock_actual,
    p.stock_minimo,
    pr.nombre AS proveedor,
    CASE
        WHEN p.stock_actual <= p.stock_minimo THEN 'ALERTA'
        WHEN p.stock_actual <= p.stock_minimo * 1.2 THEN 'PRECAUCION'
        ELSE 'OK'
    END AS estado
FROM productos p
JOIN proveedores pr ON p.proveedor_id = pr.id
WHERE p.stock_actual <= p.stock_minimo * 1.2
ORDER BY p.stock_actual ASC;

-- 3. Top 10 Productos más vendidos
EXPLAIN ANALYZE
SELECT
    p.id,
    p.nombre,
    c.nombre AS categoria,
    SUM(v.cantidad) AS unidades_vendidas,
    SUM(v.total) AS ingresos,
    COUNT(*) AS numero_ventas
FROM ventas v
JOIN productos p ON v.producto_id = p.id
JOIN categorias c ON p.categoria_id = c.id
GROUP BY p.id, p.nombre, c.nombre
ORDER BY ingresos DESC
LIMIT 10;

-- 4. Alertas de Stock Mínimo (por Proveedor)
EXPLAIN ANALYZE
SELECT
    p.id,
    p.nombre,
    p.stock_actual,
    p.stock_minimo,
    pr.nombre AS proveedor,
    pr.email AS contacto
FROM productos p
JOIN proveedores pr ON p.proveedor_id = pr.id
WHERE p.stock_actual <= p.stock_minimo
ORDER BY pr.nombre, p.stock_actual ASC;
