# TESTING – Estrategia de Pruebas

**Fecha:** 2026-07-02 | **Autor:** Fisherk2

---

## 1. Estrategia de Pruebas en 3 Fases

| **Fase**        | **Tipo de Prueba**               | **Herramienta**                   | **Criterio de Éxito**                                                          |
| --------------- | -------------------------------- | --------------------------------- | ------------------------------------------------------------------------------ |
| **Unitarias**   | Pruebas de queries SQL.          | PostgreSQL (`EXPLAIN ANALYZE`)    | Todas las queries cargan en <2s.                                               |
| **Integración** | Conexión Metabase-PostgreSQL.    | Metabase + PostgreSQL             | Metabase muestra datos correctamente y sin errores de conexión.                |
| **Integración** | Generación de datos.             | Python (`pytest`)                 | El script genera datos válidos (ej: `producto_id` existe en `productos`).      |
| **E2E**         | Flujo completo de visualización. | Metabase                          | Los paneles en Metabase muestran los KPIs esperados (rotación, stock, ventas). |
| **Rendimiento** | Carga bajo volumen alto.         | PostgreSQL (`pg_stat_statements`) | Queries mantienen <2s con 200K registros por tabla.                            |
| **Seguridad**   | Acceso a datos.                  | PostgreSQL + Docker               | Credenciales no están expuestas en logs o archivos.                            |

---

## 2. Frameworks y Fixtures

| **Tipo**                   | **Herramienta**   | **Uso**                                                     |
| -------------------------- | ----------------- | ----------------------------------------------------------- |
| **Pruebas SQL**            | `EXPLAIN ANALYZE` | Validar planes de ejecución de queries.                     |
| **Pruebas Python**         | `pytest`          | Validar lógica de generación de datos.                      |
| **Pruebas de Integración** | `docker-compose`  | Validar que los servicios se levantan correctamente.        |
| **Fixtures**               | Datos sintéticos  | Usar el mismo script de generación para pruebas repetibles. |

---

## 3. Métricas de Calidad

| **Métrica**                 | **Valor Objetivo**            | **Herramienta de Medición**                  |
| --------------------------- | ----------------------------- | -------------------------------------------- |
| **Cobertura de Queries**    | 100% de queries críticas.     | `EXPLAIN ANALYZE` + revisión manual.         |
| **Tiempo de Carga**         | <2s por query.                | Cronómetro manual en Metabase.               |
| **Volumen de Datos**        | 50K–200K registros por tabla. | `SELECT COUNT(*) FROM tabla;` en PostgreSQL. |
| **Complejidad Ciclomática** | <10 por query.                | Análisis manual de queries.                  |
| **Deuda Técnica**           | 0 (para MVP).                 | Revisión de código y schema.                 |

---

## 4. Estrategia de Mockeo y Aislamiento

- **PostgreSQL:** Usar **vistas** para aislar datos de pruebas (ej: `v_test_ventas`).
- **Metabase:** Usar **colecciones separadas** para pruebas (no afectar paneles de producción).
- **Python:** Usar **fixtures** con datos de prueba pequeños (ej: 100 registros) para pruebas unitarias.

---

## 5. Pruebas por Fase del Workflow

| **Fase** | **Tipo de Prueba**            | **Herramienta**                | **Criterio de Éxito**                                                  |
| -------- | ----------------------------- | ------------------------------ | ---------------------------------------------------------------------- |
| F0       | Revisión de documentación.    | Markdown + Git                 | Documentos completos y sin errores de formato.                         |
| F1       | Conexión entre servicios.     | Docker Compose + Metabase      | PostgreSQL y Metabase se comunican sin errores.                        |
| F2       | Validación de schema y datos. | PostgreSQL (`psql`)            | Schema creado, datos generados y válidos.                              |
| F2       | Rendimiento de queries.       | PostgreSQL (`EXPLAIN ANALYZE`) | Todas las queries cargan en <2s.                                       |
| F3       | Funcionalidad de paneles.     | Metabase                       | Paneles muestran datos correctos y se exportan a PNG/CSV.              |
| F4       | Pruebas de estrés.            | PostgreSQL + Metabase          | Sistema mantiene rendimiento bajo carga (ej: 10 usuarios simultáneos). |
| F4       | Pruebas de error.             | Docker + Metabase              | Mensajes de error claros y recuperables.                               |
| F5       | Reproducibilidad.             | Docker Compose                 | Proyecto funciona en al menos 2 entornos locales diferentes.           |

---

## 6. Validación de Queries Críticas

Cada query crítica debe validarse con `EXPLAIN ANALYZE` antes de implementarse en Metabase.

### Ejemplo de Validación

```sql
-- Validar rendimiento de query de rotación por categoría
EXPLAIN ANALYZE
SELECT 
    c.nombre AS categoria,
    t.mes,
    t.anio,
    SUM(v.cantidad) AS ventas_totales,
    SUM(v.total) AS ingresos_totales
FROM ventas v
JOIN productos p ON v.producto_id = p.id
JOIN categorias c ON p.categoria_id = c.id
JOIN tiempo t ON v.fecha_id = t.id
GROUP BY c.nombre, t.mes, t.anio
ORDER BY t.anio, t.mes, ventas_totales DESC;
```

### Criterios de Aceptación

- **Tiempo de ejecución:** <2 segundos.
- **Tipo de scan:** Preferir Index Scan o Index Only Scan sobre Seq Scan.
- **Uso de índices:** Confirmar que los índices en `producto_id`, `fecha_id`, `categoria_id` son utilizados.
- **Filas procesadas:** Validar que el número de filas es consistente con el volumen esperado.
