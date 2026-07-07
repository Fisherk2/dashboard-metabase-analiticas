# User Guide — Dashboard Metabase + Colección Analítica

**Fecha:** 2026-07-07 | **Fase:** F5 (Despliegue)
**Audiencia:** Usuarios finales que quieren explorar los dashboards
**Proyecto:** Dashboard Metabase + Colección Analítica para E-commerce

---

## 1. Prerrequisitos

Antes de comenzar, necesitas:

- **Docker** 20+ y **Docker Compose** 2+ instalados
- **Python** 3.8+ y **pip**
- **GNU Make** 4.0+
- **Git**
- Navegador web (Chrome, Firefox, Edge)
- Conexión a internet (para las imágenes de Docker)

## 2. Setup (5 minutos)

```bash
# 1. Clonar el repositorio
git clone <repo-url> dashboard-metabase
cd dashboard-metabase

# 2. Crear archivo de credenciales
cp .env.example .env

# 3. Setup completo — instala deps, levanta servicios, crea BD, genera datos
make setup
```

**Qué hace `make setup`:**
1. `make deps` — Instala dependencias Python (Faker, psycopg2, requests)
2. `make up` — Levanta PostgreSQL y Metabase en contenedores Docker
3. `make db-init` — Crea el schema estrella (tablas + índices)
4. `make data-generate` — Genera ~182K registros sintéticos
5. `make create-views` — Crea las 3 vistas materializadas desde `sql/views/*.sql`
6. `make mv-refresh` — Refresca las vistas materializadas con datos actuales

**Verificar que todo funciona:**
```bash
make status          # Ambos servicios deben mostrar "healthy"
make data-count      # Muestra conteo de registros por tabla
```

## 3. Acceder a Metabase

1. Abrir `http://localhost:3000` en el navegador
2. Completar el registro inicial:
   - **Nombre:** tu nombre
   - **Email:** admin@example.com (o el configurado en `MB_USER` del `.env`)
   - **Contraseña:** la configurada en `MB_PASSWORD` del `.env`

3. En el paso "Agregar datos", **saltar** la conexión (la BD ya está configurada via script):
   - Hacer clic en "I'll add my data later"
   - La conexión a PostgreSQL se configura automáticamente con `make metabase-setup`

4. Si prefieres configuración manual:
   ```bash
   python scripts/setup_metabase.py --full
   ```
   Esto configura: conexión BD, 4 questions guardadas, 1 dashboard, 2 pulses.

### Configurar Conexión Manual

Si necesitas conectar PostgreSQL manualmente desde la UI de Metabase:

| Campo | Valor |
|-------|-------|
| Database type | PostgreSQL |
| Host | `postgres` |
| Port | `5432` |
| Database name | `ecommerce` |
| Username | `dashboard_user` (ver `.env`) |
| Password | (ver `.env` > `POSTGRES_PASSWORD`) |

> **Nota:** El host es `postgres` (nombre del servicio Docker), no `localhost`. Metabase y PostgreSQL están en la misma red Docker.

## 4. Tour del Dashboard

Después del setup, tendrás acceso al dashboard **"E-commerce Analytics"** con 4 paneles. Cada panel se explica a continuación.

### Panel 1: Rotación por Categoría

**Propósito:** Visualizar qué categorías de productos tienen mayor rotación mensual.

| Atributo | Detalle |
|----------|---------|
| **Pregunta que responde** | ¿Qué categorías venden más y cómo evoluciona su rotación mes a mes? |
| **Fuente de datos** | `mv_rotacion_mensual` (vista materializada) |
| **Tipo de gráfico** | Bar chart (barras agrupadas por categoría, eje X = mes) |
| **Tiempo de carga** | <2 segundos (pre-agregado en MV) |

**Interpretación:**
- **Barras altas** = alta rotación (productos se venden rápido)
- **Tendencia creciente** = la categoría está ganando tracción
- **Tendencia decreciente** = la categoría está perdiendo demanda
- **Categorías sin barras** = sin ventas en ese período (puede indicar stock agotado)

**Ejemplo de query subyacente:**
```sql
SELECT c.nombre AS categoria, t.mes, SUM(v.cantidad) AS total_vendido
FROM mv_rotacion_mensual v
JOIN productos p ON v.producto_id = p.id
JOIN categorias c ON p.categoria_id = c.id
JOIN tiempo t ON v.fecha_id = t.id
GROUP BY c.nombre, t.mes
ORDER BY t.mes, total_vendido DESC;
```

### Panel 2: Stock Actual vs. Mínimo

**Propósito:** Monitorear el nivel de inventario actual contra el umbral mínimo definido para cada producto.

| Atributo | Detalle |
|----------|---------|
| **Pregunta que responde** | ¿Qué productos tienen stock bajo o están por debajo del mínimo? |
| **Fuente de datos** | `mv_stock_actual` (vista materializada) |
| **Tipo de visualización** | Table con formato condicional |
| **Filtros disponibles** | Por estado (ALERTA / OK), por categoría |
| **Tiempo de carga** | <2 segundos |

**Interpretación de estados:**

| Estado | Indicador | Significado | Acción recomendada |
|--------|-----------|-------------|-------------------|
| 🟢 **OK** | stock_actual > stock_minimo * 1.5 | Inventario saludable | Monitoreo normal |
| 🟡 **BAJO** | stock_minimo < stock_actual <= stock_minimo * 1.5 | Se acerca al mínimo | Considerar reabastecimiento |
| 🔴 **ALERTA** | stock_actual <= stock_minimo | Stock crítico | Reabastecer urgente |

**Columnas del panel:**
- `producto` — Nombre del producto
- `categoria` — Categoría a la que pertenece
- `stock_actual` — Unidades disponibles
- `stock_minimo` — Umbral mínimo definido
- `estado` — ALERTA, BAJO, o OK (derivado de la comparación)

### Panel 3: Top 10 Ventas

**Propósito:** Identificar los productos con mayores ingresos.

| Atributo | Detalle |
|----------|---------|
| **Pregunta que responde** | ¿Cuáles son los 10 productos que más ingresos generan? |
| **Fuente de datos** | `mv_top_productos` (vista materializada) |
| **Tipo de gráfico** | Row chart (horizontal, ordenado de mayor a menor) |
| **Tiempo de carga** | <20 milisegundos |

**Interpretación:**
- **Barra más larga** = producto estrella (mayor ingreso)
- **Productos agrupados cerca** = competencia fuerte en ingresos
- **Caída abrupta después del #1** = dependencia excesiva en un solo producto

**Ejemplo de query subyacente:**
```sql
SELECT p.nombre, SUM(v.total) AS ingresos_totales
FROM mv_top_productos v
JOIN productos p ON v.producto_id = p.id
GROUP BY p.nombre
ORDER BY ingresos_totales DESC
LIMIT 10;
```

### Panel 4: Alertas de Stock Mínimo

**Propósito:** Listar todos los productos que actualmente están en estado crítico (stock por debajo del mínimo).

| Atributo | Detalle |
|----------|---------|
| **Pregunta que responde** | ¿Qué productos necesitan reabastecimiento urgente? |
| **Fuente de datos** | Tablas base (`productos`, `inventario`) con filtro `stock_actual <= stock_minimo` |
| **Tipo de visualización** | Table |
| **Tiempo de carga** | <100 milisegundos |

**Interpretación:**
- **Cada fila** = un producto en estado crítico
- **stock_actual** muy por debajo de **stock_minimo** = riesgo de ruptura de inventario
- Si no hay filas = todos los productos tienen stock suficiente

**Ejemplo de query subyacente:**
```sql
SELECT p.nombre AS producto, i.stock_actual, i.stock_minimo,
       (i.stock_actual - i.stock_minimo) AS diferencia
FROM inventario i
JOIN productos p ON i.producto_id = p.id
WHERE i.stock_actual <= i.stock_minimo
ORDER BY diferencia ASC;
```

## 5. Alertas Automáticas (Metabase Pulses)

El proyecto incluye 2 alertas programadas que se envían por email (requiere configuración SMTP en Metabase):

| Alerta | Horario | Contenido |
|--------|---------|-----------|
| **Stock Crítico** | Diario 09:00 | Lista de productos con stock_actual <= stock_minimo |
| **Resumen Ventas** | Diario 18:00 | Top 5 productos del día + ingresos totales |

Para configurar las alertas:
```bash
python scripts/setup_metabase.py --pulses
```

## 6. Exportar Datos

Cada panel se puede exportar desde la UI de Metabase o via API REST.

### Desde la UI

1. Abrir el dashboard en `http://localhost:3000`
2. Hover sobre el panel deseado
3. Click en los tres puntos (···) → "Download results"
4. Seleccionar formato: **CSV** (tabla), **XLSX** (Excel), o **PNG** (imagen del gráfico)

> **Nota:** PNG solo está disponible desde la UI, no via API REST.

### Via API REST

```bash
# Autenticarse
TOKEN=$(curl -s -X POST http://localhost:3000/api/session \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$MB_USER\",\"password\":\"$MB_PASSWORD\"}" | \
  python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

# Exportar CSV del card con ID 1
curl -s -H "X-Metabase-Session: $TOKEN" \
  http://localhost:3000/api/card/1/query/csv > export.csv
```

Ver [docs/METABASE_EXPORTS.md](METABASE_EXPORTS.md) para documentación completa de exportación.

## 7. Troubleshooting

### Problema 1: Metabase no carga (pantalla blanca o error 502)

**Causa:** Metabase puede estar inicializándose (tarda ~30s en primer inicio).
**Solución:**
```bash
# Verificar estado
curl http://localhost:3000/api/health
# Debe retornar {"status":"ok"}

# Ver logs
make logs | grep -i "initialization\|error"

# Esperar 30 segundos y reintentar
```

### Problema 2: El dashboard no muestra datos (tablas vacías)

**Causa:** Las vistas materializadas no se han refrescado después de generar datos.
**Solución:**
```bash
make mv-refresh
# O desde psql: REFRESH MATERIALIZED VIEW mv_rotacion_mensual;
```

### Problema 3: Error de conexión a PostgreSQL desde Metabase

**Causa:** Las credenciales en Metabase no coinciden con el `.env`.
**Solución:**
```bash
# Verificar que PostgreSQL está funcionando
make db-check

# Re-configurar la conexión en Metabase
python scripts/setup_metabase.py --db-only
```

## 8. FAQ

**P: ¿Puedo usar esto con datos reales?**
R: El proyecto está diseñado para datos sintéticos (Faker). Para usar datos reales, necesitarías adaptar el schema y los scripts de generación.

**P: ¿Cómo agrego un nuevo panel?**
R: 1) Escribir la query SQL en Metabase, 2) Añadirla al dashboard, 3) Opcional: agregarla al script `setup_metabase.py`.

**P: ¿Los datos persisten si reinicio los contenedores?**
R: Sí. Los volúmenes Docker (`postgres-data`, `metabase-data`) aseguran persistencia. `make restart` mantiene los datos.

**P: ¿Cómo cambio las credenciales?**
R: Editar `.env` y ejecutar `make destroy && make setup` para recrear todo con las nuevas credenciales.

**P: ¿Puedo exponer PostgreSQL a mi red local?**
R: No recomendado. Por seguridad, PostgreSQL solo escucha en la red interna de Docker. Para acceder desde fuera, usa `make db-shell`.

## 9. Referencias

| Recurso | Enlace |
|---------|--------|
| Setup de Metabase | [docs/METABASE_SETUP.md](METABASE_SETUP.md) |
| Exportación de datos | [docs/METABASE_EXPORTS.md](METABASE_EXPORTS.md) |
| Documentación técnica | [README.md](../README.md) |
| Schema de base de datos | [docs/SCHEMA.md](SCHEMA.md) |
| Guía de seguridad | [docs/SECURITY.md](SECURITY.md) |
