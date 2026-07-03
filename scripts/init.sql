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
    fecha_creacion      TIMESTAMP     NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_productos_categoria_id
    ON productos (categoria_id);
CREATE INDEX IF NOT EXISTS idx_productos_proveedor_id
    ON productos (proveedor_id);

COMMENT ON TABLE productos IS 'Catalogo de productos con stock y precios';

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
    anio       VARCHAR(4)   NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_promociones_categoria_id
    ON promociones (categoria_id);

COMMENT ON TABLE promociones IS 'Promociones aplicables a ventas';
