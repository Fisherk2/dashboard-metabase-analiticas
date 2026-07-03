-- =============================================================================
-- mv_rotacion_mensual — Rotación de ventas por categoría y mes
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
-- Pre-computa KPIs de rotación para queries frecuentes del dashboard.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS mv_rotacion_mensual CASCADE;

CREATE MATERIALIZED VIEW mv_rotacion_mensual AS
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
WITH DATA;

-- Índices para acelerar consultas
CREATE INDEX IF NOT EXISTS idx_mv_rotacion_categoria
    ON mv_rotacion_mensual (categoria);
CREATE INDEX IF NOT EXISTS idx_mv_rotacion_mes_anio
    ON mv_rotacion_mensual (mes, anio);

REFRESH MATERIALIZED VIEW mv_rotacion_mensual;
