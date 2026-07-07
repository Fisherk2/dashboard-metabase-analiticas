-- =============================================================================
-- Indexes — Dashboard Metabase + Colección Analítica para E-commerce
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
--
-- Índices B-tree en columnas usadas en WHERE, JOIN, GROUP BY.
-- Todos usan CREATE INDEX IF NOT EXISTS para idempotencia.
-- =============================================================================

-- ─── Ventas ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_ventas_producto_id
    ON ventas (producto_id);
CREATE INDEX IF NOT EXISTS idx_ventas_cliente_id
    ON ventas (cliente_id);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha_id
    ON ventas (fecha_id);
CREATE INDEX IF NOT EXISTS idx_ventas_promocion_id
    ON ventas (promocion_id);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha_venta
    ON ventas (fecha_venta);

-- ─── Inventario ──────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_inventario_producto_id
    ON inventario (producto_id);
CREATE INDEX IF NOT EXISTS idx_inventario_fecha_id
    ON inventario (fecha_id);
CREATE INDEX IF NOT EXISTS idx_inventario_proveedor_id
    ON inventario (proveedor_id);

-- ─── Devoluciones ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_devoluciones_venta_id
    ON devoluciones (venta_id);
CREATE INDEX IF NOT EXISTS idx_devoluciones_producto_id
    ON devoluciones (producto_id);
CREATE INDEX IF NOT EXISTS idx_devoluciones_cliente_id
    ON devoluciones (cliente_id);
CREATE INDEX IF NOT EXISTS idx_devoluciones_fecha_id
    ON devoluciones (fecha_id);

-- ─── Logistica ───────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_logistica_venta_id
    ON logistica (venta_id);
CREATE INDEX IF NOT EXISTS idx_logistica_proveedor_id
    ON logistica (proveedor_id);
CREATE INDEX IF NOT EXISTS idx_logistica_fecha_entrega_id
    ON logistica (fecha_entrega_id);
CREATE INDEX IF NOT EXISTS idx_logistica_estado
    ON logistica (estado);

-- ─── Productos ───────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_productos_categoria_id
    ON productos (categoria_id);
CREATE INDEX IF NOT EXISTS idx_productos_proveedor_id
    ON productos (proveedor_id);

-- ─── Promociones ─────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_promociones_categoria_id
    ON promociones (categoria_id);
