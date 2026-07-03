-- =============================================================================
-- refresh_materialized_views.sql — Refrescar todas las MVs
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
-- Ejecutar con: make mv-refresh
-- =============================================================================

REFRESH MATERIALIZED VIEW mv_rotacion_mensual;
REFRESH MATERIALIZED VIEW mv_stock_actual;
REFRESH MATERIALIZED VIEW mv_top_productos;
