# Spec: SQL Optimization — Vistas Materializadas, Índices y Particionamiento

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Fase:** F2

---

## 1. Objetivo

Optimizar las queries críticas del dashboard mediante vistas materializadas, índices estratégicos y particionamiento. Todas las queries deben ejecutarse en <2s con 200K registros por tabla.

---

## 2. Estrategia de Optimización

### 2.1 Índices

Crear índices B-tree en columnas usadas en `WHERE`, `JOIN`, y `GROUP BY`:

| **Índice**                       | **Tabla**    | **Columna(s)**              | **Propósito**                    |
| -------------------------------- | ------------ | --------------------------- | -------------------------------- |
| `idx_ventas_producto_id`         | `ventas`     | `producto_id`               | JOIN con productos               |
| `idx_ventas_fecha_id`            | `ventas`     | `fecha_id`                  | Filtros por fecha                |
| `idx_ventas_cliente_id`          | `ventas`     | `cliente_id`                | JOIN con clientes                |
| `idx_inventario_producto_id`     | `inventario` | `producto_id`               | JOIN con productos               |
| `idx_inventario_fecha_id`        | `inventario` | `fecha_id`                  | Filtros por fecha                |
| `idx_productos_categoria_id`     | `productos`  | `categoria_id`              | JOIN con categorias              |
| `idx_productos_proveedor_id`     | `productos`  | `proveedor_id`              | JOIN con proveedores             |
| `idx_devoluciones_venta_id`      | `devoluciones`| `venta_id`                 | JOIN con ventas                  |
| `idx_ventas_fecha_venta`         | `ventas`     | `fecha_venta`               | Particionamiento / rango fechas  |

### 2.2 Vistas Materializadas

Pre-calcular KPIs críticos para queries frecuentes:

#### `mv_rotacion_mensual`

```sql
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

-- Índice para acelerar consultas
CREATE INDEX idx_mv_rotacion_categoria ON mv_rotacion_mensual (categoria);
CREATE INDEX idx_mv_rotacion_mes_anio ON mv_rotacion_mensual (mes, anio);

-- Refresh
REFRESH MATERIALIZED VIEW mv_rotacion_mensual;
```

#### `mv_stock_actual`

```sql
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

CREATE INDEX idx_mv_stock_estado ON mv_stock_actual (estado);
CREATE INDEX idx_mv_stock_producto ON mv_stock_actual (producto_id);

REFRESH MATERIALIZED VIEW mv_stock_actual;
```

#### `mv_top_productos`

```sql
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

CREATE INDEX idx_mv_top_productos_ranking ON mv_top_productos (ingresos_totales DESC);

REFRESH MATERIALIZED VIEW mv_top_productos;
```

### 2.3 Particionamiento (Opcional)

Particionar la tabla `ventas` por rango de fechas para mejorar rendimiento en queries con filtros temporales:

```sql
-- Crear tabla particionada
CREATE TABLE ventas (
    id SERIAL,
    producto_id INT NOT NULL,
    cliente_id INT NOT NULL,
    fecha_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    promocion_id INT,
    fecha_venta TIMESTAMP NOT NULL
) PARTITION BY RANGE (fecha_venta);

-- Crear particiones mensuales
CREATE TABLE ventas_2026_01 PARTITION OF ventas 
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE ventas_2026_02 PARTITION OF ventas 
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
-- ... (12 particiones para 1 año)
```

---

## 3. Script de Refresh

```sql
-- refresh_materialized_views.sql
REFRESH MATERIALIZED VIEW mv_rotacion_mensual;
REFRESH MATERIALIZED VIEW mv_stock_actual;
REFRESH MATERIALIZED VIEW mv_top_productos;
```

---

## 4. Archivos

| **Archivo**                      | **Ubicación**                    | **Propósito**                    |
| -------------------------------- | -------------------------------- | -------------------------------- |
| `create_indexes.sql`             | `sql/indexes/`                   | Creación de índices              |
| `mv_rotacion_mensual.sql`        | `sql/views/`                     | Vista materializada de rotación  |
| `mv_stock_actual.sql`            | `sql/views/`                     | Vista materializada de stock     |
| `mv_top_productos.sql`           | `sql/views/`                     | Vista materializada de top       |
| `refresh_materialized_views.sql` | `scripts/`                       | Refresh de todas las MVs         |
| `partition_ventas.sql`           | `sql/partitions/`                | Particionamiento (opcional)      |

---

## 5. Criterios de Aceptación

- [ ] Todos los índices creados y visibles en `pg_indexes`.
- [ ] Vistas materializadas creadas y con datos (`WITH DATA`).
- [ ] `REFRESH MATERIALIZED VIEW` ejecuta sin errores.
- [ ] Queries contra MVs cargan en <2s (`EXPLAIN ANALYZE`).
- [ ] Particionamiento validado (si se implementa).
- [ ] Plan de ejecución usa Index Scan (no Seq Scan) en queries críticas.

---

## 6. Dependencias

- **Requiere:** F2 (Schema + datos generados).
- **Habilita:** F3 (Dashboards usan MVs para rendimiento).

---

## 7. Verificación

```sql
-- Validar índices
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Validar vistas materializadas
SELECT matviewname FROM pg_matviews WHERE schemaname = 'public';

-- Validar rendimiento
EXPLAIN ANALYZE
SELECT categoria, mes, anio, ventas_totales 
FROM mv_rotacion_mensual 
WHERE anio = '2026' AND mes = 'Enero'
ORDER BY ventas_totales DESC;

-- Validar particionamiento (si aplica)
SELECT * FROM pg_partition_tree('ventas');
```
