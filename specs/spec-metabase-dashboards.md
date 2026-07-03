# Spec: Metabase Dashboards — Configuración de Paneles

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Fase:** F3

---

## 1. Objetivo

Configurar 3+ paneles en Metabase que visualicen KPIs de rotación, stock y ventas. Los paneles deben cargar en <2s, permitir exportación a PNG/CSV, y usar vistas materializadas para optimización.

---

## 2. Paneles Requeridos

### 2.1 Panel: Rotación por Categoría

**Propósito:** Visualizar ventas e ingresos por categoría de producto a lo largo del tiempo.

**Query Base:**
```sql
SELECT 
    categoria,
    mes,
    anio,
    ventas_totales,
    ingresos_totales,
    productos_vendidos
FROM mv_rotacion_mensual
WHERE anio = {{anio}} 
  AND mes = {{mes}}
ORDER BY ventas_totales DESC;
```

**Visualización:**
- **Tipo:** Gráfico de barras agrupadas (categorías en eje X, ventas en eje Y).
- **Filtros:** Año, Mes (variables `{{anio}}`, `{{mes}}`).
- **KPIs mostrados:** Total ventas, total ingresos, # productos vendidos.
- **Exportación:** PNG, CSV.

---

### 2.2 Panel: Stock Actual vs. Mínimo

**Propósito:** Mostrar alertas de stock mínimo y estado de inventario por producto.

**Query Base:**
```sql
SELECT 
    producto_id,
    nombre,
    categoria,
    proveedor,
    stock_actual,
    stock_minimo,
    estado
FROM mv_stock_actual
WHERE estado IN ('ALERTA', 'PRECAUCION')
ORDER BY stock_actual ASC;
```

**Visualización:**
- **Tipo:** Tabla con indicadores de color (rojo = ALERTA, amarillo = PRECAUCION, verde = OK).
- **Filtros:** Categoría, Proveedor, Estado.
- **KPIs mostrados:** # productos en ALERTA, # productos en PRECAUCION, # productos OK.
- **Exportación:** PNG, CSV.

---

### 2.3 Panel: Top 10 Productos por Ventas

**Propósito:** Identificar los productos con mayores ingresos.

**Query Base:**
```sql
SELECT 
    producto_id,
    nombre,
    categoria,
    unidades_vendidas,
    ingresos_totales,
    numero_ventas
FROM mv_top_productos
ORDER BY ingresos_totales DESC
LIMIT 10;
```

**Visualización:**
- **Tipo:** Gráfico de barras horizontales (productos en eje Y, ingresos en eje X).
- **Filtros:** Categoría.
- **KPIs mostrados:** Total ingresos Top 10, total unidades vendidas Top 10.
- **Exportación:** PNG, CSV.

---

### 2.4 Panel: Alertas de Stock Mínimo (Opcional)

**Propósito:** Dashboard dedicado a alertas de stock con configuración de umbrales.

**Query Base:**
```sql
SELECT 
    p.id,
    p.nombre,
    p.stock_actual,
    p.stock_minimo,
    pr.nombre AS proveedor,
    pr.email AS contacto_proveedor
FROM productos p
JOIN proveedores pr ON p.proveedor_id = pr.id
WHERE p.stock_actual <= p.stock_minimo * {{umbral_multiplier}}
ORDER BY p.stock_actual ASC;
```

**Visualización:**
- **Tipo:** Tabla con alertas.
- **Filtros:** Proveedor, Umbral multiplicador (variable `{{umbral_multiplier}}`).
- **Exportación:** PNG, CSV.

---

## 3. Configuración de Metabase

### 3.1 Conexión a PostgreSQL

| **Parámetro**       | **Valor**                              |
| ------------------- | -------------------------------------- |
| **Host**            | `postgres` (nombre del servicio Docker)|
| **Port**            | `5432`                                 |
| **Database**        | `ecommerce`                            |
| **User**            | `admin`                                |
| **Password**        | `${POSTGRES_PASSWORD}`                 |

### 3.2 Permisos de Usuario

- **Gerente de Operaciones:** Acceso a todos los paneles, exportación, configuración de alertas.
- **Analista de Datos:** Acceso a paneles y queries personalizadas, exportación.
- **Desarrollador:** Acceso a configuración de conexión, logs.
- **Dueño del E-commerce:** Acceso a paneles de alertas y KPIs de alto nivel.

---

## 4. Filtros Globales

| **Filtro**      | **Variable**         | **Tipo**   | **Aplica a**                          |
| --------------- | -------------------- | ---------- | ------------------------------------- |
| Año             | `{{anio}}`           | Dropdown   | Panel Rotación                        |
| Mes             | `{{mes}}`            | Dropdown   | Panel Rotación                        |
| Categoría       | `{{categoria}}`      | Dropdown   | Paneles Rotación, Stock, Top Productos|
| Proveedor       | `{{proveedor}}`      | Dropdown   | Panel Stock, Alertas                  |
| Estado          | `{{estado}}`         | Dropdown   | Panel Stock                           |
| Umbral          | `{{umbral_multiplier}}` | Number  | Panel Alertas (opcional)              |

---

## 5. Archivos

| **Archivo**              | **Ubicación**              | **Propósito**                          |
| ------------------------ | -------------------------- | -------------------------------------- |
| `dashboard_rotacion.json`| `metabase/collections/`    | Exportación de configuración (opcional)|
| `dashboard_stock.json`   | `metabase/collections/`    | Exportación de configuración (opcional)|
| `dashboard_top.json`     | `metabase/collections/`    | Exportación de configuración (opcional)|

---

## 6. Criterios de Aceptación

- [ ] 3+ paneles configurados y funcionales.
- [ ] Todos los paneles cargan en <2s (validar en Metabase).
- [ ] Filtros funcionan correctamente (año, mes, categoría, proveedor).
- [ ] Exportación a PNG funciona para todos los paneles.
- [ ] Exportación a CSV funciona para todos los paneles.
- [ ] Queries usan vistas materializadas (no tablas base).
- [ ] `EXPLAIN ANALYZE` confirma Index Scan en queries críticas.
- [ ] Permisos de usuario configurados correctamente.

---

## 7. Dependencias

- **Requiere:** F2 (Schema + datos + vistas materializadas).
- **Habilita:** F4 (Pruebas), F5 (Despliegue).

---

## 8. Verificación

```bash
# Conectar a Metabase
open http://localhost:3000

# Configurar conexión a PostgreSQL
# Admin → Databases → Add database → PostgreSQL
# Host: postgres, Port: 5432, Database: ecommerce
# User: admin, Password: ${POSTGRES_PASSWORD}

# Crear paneles
# Questions → New → SQL Query → Pegar query base
# Save → Add to dashboard

# Validar rendimiento
# En Metabase: Questions → Ver tiempo de carga (debe ser <2s)

# Exportar
# En cada panel: ⋮ → Export to PNG / Export to CSV
```

---

## 9. Notas

- Metabase OSS no soporta deep linking a paneles específicos (limitación conocida).
- Las variables de filtro (`{{anio}}`, `{{mes}}`) se configuran en el editor de queries de Metabase.
- Para alertas automáticas, usar Metabase Pulse (requiere configuración de email/Slack).
