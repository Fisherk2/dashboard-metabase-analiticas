# METABASE_SETUP — Configuración de Dashboards

**Fecha:** 2026-07-06 | **Fase:** F3 (Interfaces)
**Proyecto:** Dashboard Metabase + Colección Analítica para E-commerce

---

## Setup Rápido

```bash
# 1. Asegurar que los servicios están funcionando
make up && make db-init && make data-generate && make mv-refresh

# 2. Instalar dependencias necesarias
pip install requests python-dotenv

# 3. Ejecutar setup completo de Metabase (crea conexión, questions, dashboard, pulses, export)
python scripts/setup_metabase.py --full
```

## Setup Paso a Paso

### 1. Database Connection
```bash
python scripts/setup_metabase.py --db-only
```
Crea la conexión PostgreSQL en Metabase con host=`postgres`, port=`5432`.

### 2. Questions (Saved SQL)
```bash
python scripts/setup_metabase.py --questions
```
Crea 4 queries guardadas:
- Rotación por Categoría (bar chart)
- Stock Actual vs Mínimo (table with conditional formatting)
- Top 10 Productos por Ventas (row chart)
- Alertas de Stock Mínimo (table with variable `{{umbral_multiplier}}`)

### 3. Dashboard + Cards
```bash
python scripts/setup_metabase.py --dashboard
```
Crea dashboard "E-commerce Analytics" con 4 cards en layout 2x2.

### 4. Pulses (Alertas)
```bash
python scripts/setup_metabase.py --pulses
```
Configura 2 alertas automáticas:
- Alerta Stock Crítico: diario 09:00
- Resumen Ventas Diarias: diario 18:00

## Re-configuración

El script es **idempotente** — se puede ejecutar múltiples veces sin duplicar recursos.

```bash
# Forzar recreación completa (pierde configuraciones manuales)
python scripts/setup_metabase.py --full
```

## Troubleshooting

### Metabase no responde
```bash
# Verificar que Metabase está funcionando
curl http://localhost:3000/api/health
# Debe retornar: {"status":"ok"}

# Verificar logs
make logs-mb
```

### Error de autenticación
```bash
# Verificar credenciales en .env
grep MB_USER .env
grep MB_PASSWORD .env
# Valores por defecto si no están configurados:
# MB_USER=admin@local
# MB_PASSWORD=admin
```

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL está funcionando
make db-check

# Verificar credenciales
grep POSTGRES_ .env

# Conectar directamente
make db-shell
```

### El script crea duplicados
El script verifica con GET antes de POST (idempotencia). Si ves duplicados:
```bash
# Limpiar y recrear
# 1. Borrar manualmente desde la UI de Metabase
# 2. Re-ejecutar el script
```

### Error de puerto ocupado
```bash
# Verificar que el puerto 3000 no está ocupado
lsof -i :3000

# Cambiar puerto en docker-compose.yml y .env
```

## Archivos

| Archivo | Propósito |
|---------|-----------|
| `scripts/setup_metabase.py` | Script principal de configuración vía API REST |
| `metabase/collections/dashboard_ecommerce.json` | Export de la colección (snapshot portable) |
| `sql/queries_dashboard.sql` | Queries de los paneles con EXPLAIN ANALYZE |
| `docker/docker-compose.yml` | Servicios PostgreSQL + Metabase |

## Endpoints de la API Rest Utilizados

| Endpoint | Método | Propósito |
|----------|--------|-----------|
| `/api/session` | POST | Autenticación |
| `/api/database` | GET, POST | Gestión de conexiones |
| `/api/card` | GET, POST | Gestión de preguntas (queries) |
| `/api/dashboard` | GET, POST | Gestión de dashboards |
| `/api/dashboard/{id}/cards` | POST | Añadir cards al dashboard |
| `/api/pulse` | GET, POST | Gestión de alertas |
| `/api/collection/root` | GET | Obtener colección raíz |
| `/api/collection/{id}/items` | GET | Exportar items de colección |
