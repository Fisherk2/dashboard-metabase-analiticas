# Spec: Star Schema — Diseño de Esquema Estrella

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Fase:** F2

---

## 1. Objetivo

Implementar un schema estrella en PostgreSQL con tablas de hechos y dimensiones optimizado para cargas analíticas (OLAP). El schema debe soportar consultas de rotación, stock, ventas y alertas con rendimiento <2s.

**Detalle completo:** Ver [docs/SCHEMA.md](../docs/SCHEMA.md) para el modelo ER, definición de tablas y queries críticas.

---

## 2. Tablas de Dimensiones (5+)

| **Tabla**     | **Registros Esperados** | **Propósito**                          |
| ------------- | ----------------------- | -------------------------------------- |
| `categorias`  | 10–50                   | Clasificación de productos             |
| `proveedores` | 20–100                  | Proveedores de productos               |
| `productos`   | 1K–10K                  | Catálogo de productos (dimensión rica) |
| `clientes`    | 1K–10K                  | Clientes del e-commerce                |
| `tiempo`      | 365–730                 | Dimensión temporal (día, mes, año, trimestre) |
| `promociones` | 10–50                   | Promociones aplicables a ventas        |

---

## 3. Tablas de Hechos (3+)

| **Tabla**      | **Registros Esperados** | **Propósito**                          |
| -------------- | ----------------------- | -------------------------------------- |
| `ventas`       | 50K–200K                | Transacciones de venta                 |
| `inventario`   | 50K–200K                | Movimientos de inventario              |
| `devoluciones` | 5K–20K                  | Devoluciones asociadas a ventas        |
| `logistica`    | 10K–50K                 | Envíos y logística (opcional)          |

---

## 4. Constraints y Índices

### Primary Keys
- Todas las tablas tienen `id SERIAL PRIMARY KEY`.

### Foreign Keys
- Todas las columnas FK tienen índices B-tree.
- FKs referencian tablas de dimensiones desde tablas de hechos.

### Check Constraints
- `productos.stock_actual >= 0`
- `productos.stock_minimo >= 0`
- `productos.precio > 0`
- `ventas.cantidad > 0`
- `ventas.precio_unitario > 0`
- `inventario.stock_inicial >= 0`
- `inventario.stock_final >= 0`
- `devoluciones.cantidad > 0`
- `promociones.descuento >= 0`

### Índices Críticos
| **Índice**                  | **Tabla**    | **Columna**       |
| --------------------------- | ------------ | ----------------- |
| `idx_ventas_producto_id`    | `ventas`     | `producto_id`     |
| `idx_ventas_cliente_id`     | `ventas`     | `cliente_id`      |
| `idx_ventas_fecha_id`       | `ventas`     | `fecha_id`        |
| `idx_inventario_producto_id`| `inventario` | `producto_id`     |
| `idx_inventario_fecha_id`   | `inventario` | `fecha_id`        |
| `idx_productos_categoria_id`| `productos`  | `categoria_id`    |
| `idx_productos_proveedor_id`| `productos`  | `proveedor_id`    |

---

## 5. Archivos

| **Archivo**           | **Ubicación**          | **Propósito**                          |
| --------------------- | ---------------------- | -------------------------------------- |
| `init.sql`            | `scripts/init.sql`     | Script de inicialización del schema    |
| `create_indexes.sql`  | `sql/indexes/`         | Creación de índices                    |
| `partition_ventas.sql`| `sql/partitions/`      | Particionamiento de `ventas` (opcional)|

---

## 6. Criterios de Aceptación

- [ ] Script `init.sql` ejecuta sin errores en PostgreSQL.
- [ ] 8+ tablas creadas (5+ dimensiones, 3+ hechos).
- [ ] Todas las tablas tienen PRIMARY KEY.
- [ ] Todas las columnas FK tienen índices.
- [ ] CHECK constraints validados (ej: `stock_actual >= 0`).
- [ ] `SELECT * FROM information_schema.tables WHERE table_schema = 'public';` muestra todas las tablas.
- [ ] `SELECT * FROM pg_indexes WHERE schemaname = 'public';` muestra todos los índices.

---

## 7. Dependencias

- **Requiere:** F1 (Infraestructura — PostgreSQL corriendo).
- **Habilita:** F2 (Generación de datos), F3 (Dashboards).

---

## 8. Verificación

```sql
-- Conectar a PostgreSQL
\c ecommerce

-- Verificar tablas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' ORDER BY table_name;

-- Verificar índices
SELECT indexname, tablename FROM pg_indexes 
WHERE schemaname = 'public' ORDER BY tablename;

-- Verificar constraints
SELECT conname, conrelid::regclass, contype 
FROM pg_constraint 
WHERE connamespace = 'public'::regnamespace;

-- Contar registros (después de generar datos)
SELECT 'productos' AS tabla, COUNT(*) FROM productos
UNION ALL SELECT 'ventas', COUNT(*) FROM ventas
UNION ALL SELECT 'inventario', COUNT(*) FROM inventario;
```
