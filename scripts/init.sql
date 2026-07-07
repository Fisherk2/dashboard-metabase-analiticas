-- =============================================================================
-- Schema Inicial — Dashboard Metabase + Colección Analítica para E-commerce
-- =============================================================================
-- Fecha: 2026-07-03 | Fase: F2 (Núcleo)
-- 
-- Star schema con 6 dimensiones + 4 hechos.
-- Ejecutar con: make db-init (psql -f scripts/init.sql)
-- =============================================================================

-- =============================================================================
-- DIMENSIONES
-- =============================================================================

-- ─── Categorías ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categorias (
    id          SERIAL       PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

COMMENT ON TABLE categorias IS 'Clasificacion de productos';

-- ─── Proveedores ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS proveedores (
    id       SERIAL       PRIMARY KEY,
    nombre   VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    email    VARCHAR(100) UNIQUE
);

COMMENT ON TABLE proveedores IS 'Proveedores de productos';

-- ─── Productos ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS productos (
    id                  SERIAL        PRIMARY KEY,
    nombre              VARCHAR(100)  NOT NULL,
    descripcion         TEXT,
    precio              DECIMAL(10,2) NOT NULL CHECK (precio > 0),
    stock_actual        INT           NOT NULL CHECK (stock_actual >= 0),
    stock_minimo        INT           NOT NULL CHECK (stock_minimo >= 0),
    categoria_id        INT           NOT NULL REFERENCES categorias(id),
    proveedor_id        INT           NOT NULL REFERENCES proveedores(id),
    fecha_creacion      TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE productos IS 'Catalogo de productos con stock y precios';
-- Índices definidos en sql/indexes/create_indexes.sql

-- ─── Clientes ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clientes (
    id             SERIAL       PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(100) UNIQUE,
    direccion      TEXT,
    fecha_registro TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE clientes IS 'Clientes del e-commerce';

-- ─── Tiempo ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tiempo (
    id         SERIAL       PRIMARY KEY,
    fecha      DATE         NOT NULL UNIQUE,
    dia_semana VARCHAR(10)  NOT NULL,
    mes        VARCHAR(10)  NOT NULL,
    anio       INT          NOT NULL,
    trimestre  VARCHAR(10)  NOT NULL
);

COMMENT ON TABLE tiempo IS 'Dimension temporal (dia, mes, anio, trimestre)';

-- ─── Promociones ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS promociones (
    id           SERIAL        PRIMARY KEY,
    nombre       VARCHAR(100)  NOT NULL,
    descuento    DECIMAL(5,2)  NOT NULL CHECK (descuento >= 0),
    fecha_inicio DATE          NOT NULL,
    fecha_fin    DATE          NOT NULL,
    categoria_id INT           REFERENCES categorias(id)
);

COMMENT ON TABLE promociones IS 'Promociones aplicables a ventas';
-- Índices definidos en sql/indexes/create_indexes.sql

-- =============================================================================
-- HECHOS
-- =============================================================================

-- ─── Ventas ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ventas (
    id              SERIAL        PRIMARY KEY,
    producto_id     INT           NOT NULL REFERENCES productos(id),
    cliente_id      INT           NOT NULL REFERENCES clientes(id),
    fecha_id        INT           NOT NULL REFERENCES tiempo(id),
    cantidad        INT           NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario > 0),
    total           DECIMAL(10,2) NOT NULL,
    promocion_id    INT           REFERENCES promociones(id),
    fecha_venta     TIMESTAMP     NOT NULL
);

COMMENT ON TABLE ventas IS 'Transacciones de venta del e-commerce';
-- Índices definidos en sql/indexes/create_indexes.sql

-- ─── Inventario ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventario (
    id              SERIAL        PRIMARY KEY,
    producto_id     INT           NOT NULL REFERENCES productos(id),
    fecha_id        INT           NOT NULL REFERENCES tiempo(id),
    stock_inicial   INT           NOT NULL CHECK (stock_inicial >= 0),
    stock_final     INT           NOT NULL CHECK (stock_final >= 0),
    proveedor_id    INT           REFERENCES proveedores(id),
    fecha_registro  TIMESTAMP     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE inventario IS 'Movimientos diarios de inventario por producto';
-- Índices definidos en sql/indexes/create_indexes.sql

-- ─── Devoluciones ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS devoluciones (
    id               SERIAL       PRIMARY KEY,
    venta_id         INT          NOT NULL REFERENCES ventas(id),
    producto_id      INT          NOT NULL REFERENCES productos(id),
    cliente_id       INT          NOT NULL REFERENCES clientes(id),
    fecha_id         INT          NOT NULL REFERENCES tiempo(id),
    cantidad         INT          NOT NULL CHECK (cantidad > 0),
    motivo           TEXT,
    fecha_devolucion TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE devoluciones IS 'Devoluciones asociadas a ventas';
-- NOTA: Si se ejecuta sql/partitions/partition_ventas.sql, las FK a ventas(id)
-- se eliminan (DROP TABLE ventas CASCADE). Ver ADR-005 en specs/adr/adr-005-partitioning-fks.md.
-- Índices definidos en sql/indexes/create_indexes.sql

-- ─── Logistica ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS logistica (
    id               SERIAL       PRIMARY KEY,
    venta_id         INT          NOT NULL REFERENCES ventas(id),
    proveedor_id     INT          REFERENCES proveedores(id),
    fecha_entrega_id INT          NOT NULL REFERENCES tiempo(id),
    estado           VARCHAR(50)  NOT NULL,
    metodo_envio     VARCHAR(50),
    fecha_entrega    TIMESTAMP
);

COMMENT ON TABLE logistica IS 'Envios y seguimiento de entregas';
-- NOTA: Si se ejecuta sql/partitions/partition_ventas.sql, las FK a ventas(id)
-- se eliminan (DROP TABLE ventas CASCADE). Ver ADR-005 en specs/adr/adr-005-partitioning-fks.md.
-- Índices definidos en sql/indexes/create_indexes.sql
