# Metabase Exports — Exportación de Paneles

**Fecha:** 2026-07-06 | **Fase:** F4 (Pruebas)

---

## Endpoints de Exportación

| Formato | Endpoint | Uso |
|---------|----------|-----|
| **CSV** | `GET /api/card/{id}/query/csv` | Exportar datos tabulares |
| **XLSX** | `GET /api/card/{id}/query/xlsx` | Exportar a Excel |
| **JSON** | `GET /api/card/{id}/query/json` | Exportar datos crudos |
| **PNG** | Solo disponible vía UI (no REST) | Captura visual del card |

**Headers requeridos:**
- `X-Metabase-Session: <token>` (autenticación via API session)
- No requiere `Content-Type` especial para GET

## Script de Validación

```bash
python scripts/validate_dashboard_exports.py
```

Este script:
1. Se autentica en Metabase API
2. Obtiene todos los cards (saved questions)
3. Descarga cada card en formato CSV y XLSX
4. Valida CSV: parseable con `csv.DictReader` + ≥1 fila + columnas legibles
5. Valida XLSX: header PK (ZIP) + tamaño >100 bytes
6. Reporta tabla con resultados

## Parámetros de Exportación

| Parámetro | CSV | XLSX | JSON |
|-----------|-----|------|------|
| Encoding | UTF-8 con BOM | Binary | UTF-8 |
| Fecha | ISO 8601 | Fecha Excel | ISO 8601 |
| Nulos | Vacío | Celda vacía | `null` |
| Límite filas | 10000 (Metabase default) | 10000 | 10000 |

## Troubleshooting

### Error: No questions found
- Ejecutar `make metabase-setup` para crear las questions
- Verificar que el token de sesión sea válido (`make metabase-setup --db-only`)

### Error: HTTP 404 al exportar
- El card_id puede no existir (fue eliminado)
- Re-ejecutar `make metabase-setup --questions` para recrear
- Verificar con `curl -H "X-Metabase-Session: $TOKEN" http://localhost:3000/api/card`

### Error: CSV vacío (0 rows)
- La query no retorna datos con los parámetros actuales
- Verificar que `make mv-refresh` se haya ejecutado
- Probar la query directamente en Metabase SQL editor

### Error: Timeout en exportaciones
- Aumentar timeout en `validate_dashboard_exports.py` (parámetro `timeout=30` → 60)
- Verificar que PostgreSQL no esté bloqueado
- Reducir el límite de filas en la query (añadir `LIMIT 1000`)

### PNG no disponible via REST
La exportación a PNG solo está disponible mediante la UI de Metabase:
1. Ir a http://localhost:3000
2. Abrir el dashboard "E-commerce Analytics"
3. Click en "···" → "Download as PNG"
4. Verificar que el archivo `.png` se descarga correctamente

## Validación Manual

```bash
# Exportar CSV de un card específico
TOKEN=$(python -c "import requests; print(requests.post('http://localhost:3000/api/session', json={'username':'admin@example.com','password':'Metabase1'}).json()['id'])")
curl -s -H "X-Metabase-Session: $TOKEN" http://localhost:3000/api/card/1/query/csv | head -5

# Verificar PNG (solo UI)
# Abrir http://localhost:3000/dashboard/1 → Download as PNG
```
