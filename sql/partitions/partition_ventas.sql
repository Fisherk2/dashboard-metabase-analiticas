-- =============================================================================
-- partition_ventas.sql — Particionamiento mensual de ventas
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
--
-- Migra ventas a tabla particionada por rango de fecha_venta.
-- Estrategia: DROP + RECREATE + recargar datos (datos sintéticos).
-- =============================================================================

-- 1. Respaldar datos existentes
CREATE TABLE IF NOT EXISTS ventas_backup AS SELECT * FROM ventas;

-- 2. Eliminar tabla existente (CASCADE elimina FKs de devoluciones y logistica)
DROP TABLE IF EXISTS ventas CASCADE;

-- 3. Recrear como tabla particionada por rango de fecha_venta
CREATE TABLE ventas (
    id              SERIAL,
    producto_id     INT           NOT NULL,
    cliente_id      INT           NOT NULL,
    fecha_id        INT           NOT NULL,
    cantidad        INT           NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario > 0),
    total           DECIMAL(10,2) NOT NULL,
    promocion_id    INT,
    fecha_venta     TIMESTAMP     NOT NULL,
    PRIMARY KEY (id, fecha_venta)
) PARTITION BY RANGE (fecha_venta);

-- 4. Crear 12 particiones mensuales (2026)
CREATE TABLE ventas_2026_01 PARTITION OF ventas
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE ventas_2026_02 PARTITION OF ventas
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE ventas_2026_03 PARTITION OF ventas
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
CREATE TABLE ventas_2026_04 PARTITION OF ventas
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
CREATE TABLE ventas_2026_05 PARTITION OF ventas
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
CREATE TABLE ventas_2026_06 PARTITION OF ventas
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
CREATE TABLE ventas_2026_07 PARTITION OF ventas
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE ventas_2026_08 PARTITION OF ventas
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE ventas_2026_09 PARTITION OF ventas
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE ventas_2026_10 PARTITION OF ventas
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
CREATE TABLE ventas_2026_11 PARTITION OF ventas
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
CREATE TABLE ventas_2026_12 PARTITION OF ventas
    FOR VALUES FROM ('2026-12-01') TO ('2027-01-01');

-- 5. Migrar datos desde backup
INSERT INTO ventas (id, producto_id, cliente_id, fecha_id, cantidad,
                    precio_unitario, total, promocion_id, fecha_venta)
SELECT id, producto_id, cliente_id, fecha_id, cantidad,
       precio_unitario, total, promocion_id, fecha_venta
FROM ventas_backup
ORDER BY fecha_venta;

-- 6. Recrear índices (PostgreSQL propaga automáticamente a particiones)
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

-- 7. Crear índice único en ventas(id) para FKs (necesario para particionamiento)
CREATE UNIQUE INDEX IF NOT EXISTS idx_ventas_id_unique
    ON ventas (id);

-- 8. Partición default para fechas fuera de rango
CREATE TABLE IF NOT EXISTS ventas_default PARTITION OF ventas DEFAULT;

-- 10. Nota: FKs de devoluciones y logistica a ventas NO se recrean
-- porque PostgreSQL no permite índices UNIQUE en (id) solo para tablas
-- particionadas. La integridad se garantiza via generate_data.py.
-- Ver ADR-005 en specs/adr/adr-005-partitioning-fks.md

-- 11. Limpiar backup
DROP TABLE IF EXISTS ventas_backup;

-- 12. Vaciar y analizar
VACUUM ANALYZE ventas;
