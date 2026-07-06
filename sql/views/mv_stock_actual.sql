-- =============================================================================
-- mv_stock_actual — Estado actual de stock vs mínimo por producto
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
-- Pre-computa alertas de stock para el dashboard.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS mv_stock_actual CASCADE;

CREATE MATERIALIZED VIEW mv_stock_actual AS
SELECT
    p.id AS producto_id,
    p.nombre,
    p.stock_actual,
    p.stock_minimo,
    c.nombre AS categoria,
    pr.nombre AS proveedor,
    CASE
        WHEN p.stock_actual <= p.stock_minimo THEN 'ALERTA'
        WHEN p.stock_actual <= p.stock_minimo * 1.2 THEN 'PRECAUCION'
        ELSE 'OK'
    END AS estado
FROM productos p
JOIN categorias c ON p.categoria_id = c.id
JOIN proveedores pr ON p.proveedor_id = pr.id
WITH DATA;

-- Índices para acelerar consultas por estado y producto
CREATE INDEX IF NOT EXISTS idx_mv_stock_estado
    ON mv_stock_actual (estado);
CREATE INDEX IF NOT EXISTS idx_mv_stock_producto
    ON mv_stock_actual (producto_id);

-- Nota: WITH DATA ya pobló la MV. Refrescar con: make mv-refresh
