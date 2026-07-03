-- =============================================================================
-- mv_top_productos — Top 100 productos por ingresos
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
-- Pre-computa el ranking de productos para el dashboard.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS mv_top_productos CASCADE;

CREATE MATERIALIZED VIEW mv_top_productos AS
SELECT
    p.id AS producto_id,
    p.nombre,
    c.nombre AS categoria,
    SUM(v.cantidad) AS unidades_vendidas,
    SUM(v.total) AS ingresos_totales,
    COUNT(*) AS numero_ventas
FROM ventas v
JOIN productos p ON v.producto_id = p.id
JOIN categorias c ON p.categoria_id = c.id
GROUP BY p.id, p.nombre, c.nombre
ORDER BY ingresos_totales DESC
WITH DATA;

-- Índice para acelerar ranking por ingresos
CREATE INDEX IF NOT EXISTS idx_mv_top_productos_ranking
    ON mv_top_productos (ingresos_totales DESC);

REFRESH MATERIALIZED VIEW mv_top_productos;
