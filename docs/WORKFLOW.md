# Workflow – Dashboard Metabase + Colección Analítica para E-commerce v1.0

**Fecha:** 2026-07-07 | **Autor:** Fisherk2 | **Metodología:** Iterativo

---

## 1. Visión de Fases


| **Fase**                | **Estado**        | **Objetivo**                                                    | **Entregables**                                                                                  | **Duración**  |
| ----------------------- | ----------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------- |
| **F0: Preparación**     | ✅ COMPLETADO      | Configurar entorno base, convenciones y documentación inicial.  | Estructura de carpetas, `.gitignore`, `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `Makefile`, `tests/test_f0.py` (72 tests). | 1 día         |
| **F1: Infraestructura** | ✅ COMPLETADO      | Levantar servicios de PostgreSQL y Metabase con Docker.         | `docker-compose.yml`, credenciales seguras, conexión funcional, persistencia, tests/test_f1.py (67 tests).     | 1 día         |
| **F2: Núcleo**          | ✅ COMPLETADO      | Implementar schema estrella, generar datos y optimizar queries. | `init.sql` (10 tablas), `generate_data.py` (182K registros), 9+ índices, 3 MVs, particionamiento, `tests/test_f2.py` (+40 tests). | ~2 días       |
| **F3: Interfaces**      | ✅ COMPLETADO      | Configurar paneles en Metabase y validar queries.               | `scripts/setup_metabase.py`, 4 paneles (Rotación, Stock, Top 10, Alertas), 2 Metabase Pulses, `docs/METABASE_SETUP.md`, `tests/test_f3.py` (36 tests). | 1 día         |
| **F4: Pruebas**         | ✅ COMPLETADO      | Validar rendimiento, exportación y flujos completos.            | `measure_query_performance.py`, `validate_dashboard_exports.py`, `test_error_handling.py`, `test_persistence.sh`, `queries_performance.sql`, `METABASE_EXPORTS.md`, `tests/test_f4.py` (39 tests). | 1 día         |
| **F5: Despliegue**      | ✅ COMPLETADO      | Documentar el proyecto y preparar para portafolio.              | `README.md` (280 líneas, 17 secciones), `docs/USER_GUIDE.md` (297 líneas), `docs/TECHNICAL_GUIDE.md` (444 líneas), `docs/REPRODUCIBILITY.md`, Makefile + test fix. | 1 día         |
| **F6: Cierre**          | 📋 LISTO PARA PLANIFICAR | Revisión final y lecciones aprendidas.                          | Retrospectiva documentada, actualización de `AGENTS.md` y `WORKFLOW.md`.                         | 0.5 días      |


---

## 2. Desglose por Fase

### Fase 0: Preparación

**Objetivo:** Establecer la base del proyecto con estructura clara y documentación inicial.


| **ID** | **Tarea**                                                              | **Estado**    | **DoD (Definition of Done)**                                                                    |
| ------ | ---------------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------- |
| F0-01  | Crear estructura de carpetas (`/docs`, `/scripts`, `/sql`, `/docker`). | ✅ Completado  | Estructura de carpetas validada y versionada en Git.                                            |
| F0-02  | Configurar `.gitignore` para Python, SQL, Docker y Metabase.           | ✅ Completado  | Archivo `.gitignore` incluye patrones para `.env`, `*.pyc`, `*.log`, `data/`, etc.              |
| F0-03  | Crear `README.md` inicial con descripción del proyecto y badges.       | ✅ Completado  | `README.md` incluye: título, descripción, stack tecnológico, badges, y enlaces a documentación. |
| F0-04  | Crear `AGENTS.md` y `ARCHITECTURE.md`.                                 | ✅ Completado  | Documentos completos y revisados.                                                               |
| F0-05  | Crear `Makefile` con targets para infraestructura, BD, datos y testing.| ✅ Completado  | `make help` lista todos los targets. `make setup` ejecuta flujo completo.                       |
| F0-06  | Crear `tests/test_f0.py` con 72 tests de validación.                  | ✅ Completado  | Tests estáticos pasan sin Docker. 72 tests verdes.                                              |


**Dependencias:**

- **Requeridas:** Ninguna.
- **Opcionales:** Herramientas de linter (ej: `sqlfluff`, `black`).

---

### Fase 1: Infraestructura

**Objetivo:** Levantar un entorno reproducible con PostgreSQL y Metabase.


| **ID** | **Tarea**                                                             | **Estado**    | **DoD (Definition of Done)**                                          |
| ------ | --------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------- |
| F1-01  | Completar `docker-compose.yml` con environment, ports, volumes, healthcheck, networks, restart, mem_limit. | ✅ Completado | `make validate` exit 0; ambos servicios con healthcheck/depends_on.   |
| F1-02  | Extender `.env.example` con vars MB_DB_* y METABASE_SECRET_KEY.       | ✅ Completado | `.env.example` con 14+ vars, secciones comentadas.                    |
| F1-03  | Crear `.dockerignore` en raíz.                                        | ✅ Completado | 15+ patrones excluyendo venv, tests, .env, git.                       |
| F1-04  | Crear `docker-compose.override.yml` template.                         | ✅ Completado | Merge safe con compose. Renombrado a `.example` para evitar fugas.    |
| F1-05  | Levantar servicios y verificar healthchecks.                          | ✅ Completado | `make up` exit 0; pg_isready healthy; Metabase Initialization Complete.|
| F1-06  | Verificar API health de Metabase.                                     | ✅ Completado | `curl /api/health` retorna `{"status":"ok"}`.                         |
| F1-07  | Verificar persistencia y aislamiento de red.                          | ✅ Completado | Tabla `_f1_test` persiste tras restart; puerto 5432 NO expuesto.      |
| F1-08  | Crear `tests/test_f1.py` con suite automatizada.                      | ✅ Completado | 67 tests (61 estáticos + 6 runtime). Todos verdes.                    |
| F1-09  | Code review + simplificación de código.                               | ✅ Completado | DRY has_docker, guard clauses, dead code removido.                    |
| F1-10  | Revisión multi-eje (Tezcatlipoca) + fixes.                            | ✅ Completado | 10 observaciones corregidas en 5 commits atómicos.                    |


**Dependencias:**

- **Requeridas:** F0 (Preparación).

---

### Fase 2: Núcleo

**Objetivo:** Implementar el schema estrella, generar datos sintéticos y optimizar queries.
**Estado:** ✅ COMPLETADO


| **ID** | **Tarea**                                                                        | **Estado**    | **DoD (Definition of Done)**                                                            |
| ------ | -------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------- |
| F2-01  | Crear script `init.sql` con el schema estrella (tablas de hechos y dimensiones). | ✅ Completado | `init.sql` define 6 dimension tables con SERIAL PK, UNIQUE, CHECK, NOT NULL, COMMENT ON TABLE. |
| F2-02  | Ejecutar `init.sql` en PostgreSQL para crear el schema.                          | ✅ Completado | `init.sql` define 4 fact tables con explicit FKs, CHECK constraints, B-tree indexes.    |
| F2-03  | Desarrollar script `generate_data.py` para generar datos sintéticos.             | ✅ Completado | `generate_data.py` con `DataGenerator` class, argparse `--debug`/`--scale`/`--reset`, 10 seeders, transactions. |
| F2-04  | Ejecutar `generate_data.py` para poblar la base de datos.                        | ✅ Completado | Data generated: 20+50+5000+2000+365+30+100000+50000+5000+20000 = 182,465 records, Pareto distributions. |
| F2-05  | Crear índices en columnas críticas (ej: `producto_id`, `fecha_id`).              | ✅ Completado | `create_indexes.sql` with 9+ B-tree indexes, `IF NOT EXISTS` idempotency; `queries_baseline.sql` with `EXPLAIN ANALYZE`. |
| F2-06  | Crear vistas materializadas para KPIs críticos (rotación, stock, ventas).        | ✅ Completado | 3 MVs: `mv_rotacion_mensual`, `mv_stock_actual`, `mv_top_productos`; `refresh_materialized_views.sql`; queries <2s. |
| F2-07  | Particionar tabla `ventas` por rango de fechas.                                  | ✅ Completado | `ventas` partitioned by `RANGE (fecha_venta)` into 12 monthly partitions; partition pruning active. |


**Dependencias:**

- **Requeridas:** F1 (Infraestructura).

---

### Fase 3: Interfaces

**Objetivo:** Configurar paneles en Metabase y validar queries.
**Estado:** ✅ COMPLETADO


| **ID** | **Tarea**                                                           | **Estado**    | **DoD (Definition of Done)**                                                      |
| ------ | ------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------- |
| F3-01  | Conectar Metabase a PostgreSQL y configurar permisos.               | ✅ Completado | `scripts/setup_metabase.py` con `MetabaseSetup` class, `authenticate()`, `create_database_connection()`. Conexión PostgreSQL funcional via JDBC. |
| F3-02  | Crear panel "Rotación por Categoría" en Metabase.                   | ✅ Completado | Question SQL contra `mv_rotacion_mensual`, display=bar, carga <2s.                |
| F3-03  | Crear panel "Stock Actual vs. Mínimo" en Metabase.                  | ✅ Completado | Question SQL contra `mv_stock_actual`, display=table, filtros estado/categoría.   |
| F3-04  | Crear panel "Ventas por Producto (Top 10)" en Metabase.             | ✅ Completado | Question SQL contra `mv_top_productos`, display=row, LIMIT 10, carga <20ms.       |
| F3-05  | Validar que todas las queries usen índices y vistas materializadas. | ✅ Completado | 3/4 queries usan MVs, 1 usa tablas base (Alertas). EXPLAIN ANALYZE documentado en `sql/queries_dashboard.sql`. |
| F3-06  | Configurar alertas de stock mínimo en Metabase.                     | ✅ Completado | 2 Metabase Pulses: "Alerta Stock Crítico" (09:00) + "Resumen Ventas" (18:00).     |


**Dependencias:**

- **Requeridas:** F2 (Núcleo).

---

### Fase 4: Pruebas

**Objetivo:** Validar rendimiento, exportación y flujos completos.
**Estado:** ✅ COMPLETADO


| **ID** | **Tarea**                                                                  | **Estado**    | **DoD (Definition of Done)**                      |
| ------ | -------------------------------------------------------------------------- | ------------- | ------------------------------------------------- |
| F4-01  | Ejecutar `EXPLAIN ANALYZE` en todas las queries críticas.                  | ✅ Completado | `sql/queries_performance.sql` con resultados reales documentados (4 queries, todas <2s). |
| F4-02  | Script de medición de rendimiento (p50/p95/p99).                           | ✅ Completado | `scripts/measure_query_performance.py` con `_compute_percentiles`. `make test-queries` via generator container. |
| F4-03  | Validar exportación de paneles a CSV/XLSX.                                 | ✅ Completado | `scripts/validate_dashboard_exports.py` con `_fetch_export`, CSV parsing, XLSX header validation. |
| F4-04  | Validar persistencia de datos tras reiniciar contenedores.                 | ✅ Completado | `scripts/test_persistence.sh` con roundtrip destructivo (make destroy → setup → metabase-setup → test). |
| F4-05  | Probar conexión fallida a PostgreSQL y validar manejo de errores.          | ✅ Completado | `scripts/test_error_handling.py` con 5 tests (health, stop, error detection, restart, recovery). |
| F4-06  | Documentar endpoints de exportación y troubleshooting.                     | ✅ Completado | `docs/METABASE_EXPORTS.md` con CSV/XLSX/JSON/PNG endpoints, parámetros, troubleshooting. |
| F4-07  | Test suite F4.                                                             | ✅ Completado | `tests/test_f4.py` con 38 tests estáticos + 2 runtime (39 total), 38/39 passing. |
| F4-08  | Code review multi-eje (Tezcatlipoca).                                      | ✅ Completado | 7 observaciones resueltas (2 críticas, 5 importantes). `cfb869f`. |


**Dependencias:**

- **Requeridas:** F3 (Interfaces).

---

### Fase 5: Despliegue

**Objetivo:** Documentar el proyecto y preparar para portafolio.
**Estado:** ✅ COMPLETADO


| **ID** | **Tarea**                                                | **Estado**      | **DoD (Definition of Done)**                                                                               |
| ------ | -------------------------------------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------- |
| F5-01  | Actualizar `README.md` (ver detalle abajo).              | ✅ Completado   | `README.md` expandido de 79 → 280 líneas con 17 secciones, Mermaid, tabla de features, performance, security. |
| F5-02  | Crear guía de usuario en `/docs/USER_GUIDE.md`.          | ✅ Completado   | `docs/USER_GUIDE.md` (297 líneas): 4 paneles interpretados, troubleshooting, FAQ, exportación API.         |
| F5-03  | Crear guía técnica en `/docs/TECHNICAL_GUIDE.md`.        | ✅ Completado   | `docs/TECHNICAL_GUIDE.md` (444 líneas): 11 secciones, arquitectura, star schema, MVs, queries, lessons learned. |
| F5-04  | Grabar video tutorial (opcional).                        | ❌ Descartado   | Decisión del usuario: sin video, solo documentación escrita.                                                |
| F5-05  | Validar que el proyecto es reproducible en otro entorno. | ✅ Completado   | Clonado a `/tmp/f5-repro-test/`, `make setup` EXIT 0, `make test` 304/318 pass, `make test-queries` ALL PASS. |

**Dependencias:**

- **Requeridas:** F4 (Pruebas).

---

### Fase 6: Cierre

**Objetivo:** Revisión final y documentación de lecciones aprendidas.
**Estado:** 📋 LISTO PARA PLANIFICAR


| **ID** | **Tarea**                                                                      | **Responsable** | **Estimación** | **DoD (Definition of Done)**                                |
| ------ | ------------------------------------------------------------------------------ | --------------- | -------------- | ----------------------------------------------------------- |
| F6-01  | Revisar todos los documentos (`PRD.md`, `TRD.md`, `AGENTS.md`, `WORKFLOW.md`). | Fisherk2        | 1 hora         | Documentos actualizados y sin inconsistencias.              |
| F6-02  | Documentar lecciones aprendidas en `/docs/LESSONS_LEARNED.md`.                 | Fisherk2        | 0.5 horas      | Documento incluye: desafíos, soluciones, y mejoras futuras. |
| F6-03  | Hacer commit final y push a repositorio Git.                                   | Fisherk2        | 0.5 horas      | Todos los cambios están versionados en Git.                 |


**Dependencias:**

- **Requeridas:** F5 (Despliegue).

---

## 3. Diagrama de Dependencia entre Specs

```mermaid
graph TD
    %% F0: Preparación
    F0[F0: Preparación] --> F1[F1: Infraestructura]
    F0 --> F2[F2: Núcleo]
    F0 --> F3[F3: Interfaces]
    F0 --> F4[F4: Pruebas]
    F0 --> F5[F5: Despliegue]
    F0 --> F6[F6: Cierre]
    
    %% F1: Infraestructura
    F1 --> F2
    F1 --> F3
    F1 --> F4
    F1 --> F5
    
    %% F2: Núcleo
    F2 --> F3
    F2 --> F4
    F2 --> F5
    
    %% F3: Interfaces
    F3 --> F4
    F3 --> F5
    
    %% F4: Pruebas
    F4 --> F5
    
    %% F5: Despliegue
    F5 --> F6
    
    %% Estilos
    style F0 fill:#f9f,stroke:#333
    style F1 fill:#bbf,stroke:#333
    style F2 fill:#bbf,stroke:#333
    style F3 fill:#bbf,stroke:#333
    style F4 fill:#bbf,stroke:#333
    style F5 fill:#bbf,stroke:#333
    style F6 fill:#f96,stroke:#333
```

**Leyenda:**

- **F0 (Preparación):** Base para todas las fases.
- **F1 (Infraestructura):** Requerida para F2, F3, F4, F5.
- **F2 (Núcleo):** Requerida para F3, F4, F5.
- **F3 (Interfaces):** Requerida para F4, F5.
- **F4 (Pruebas):** Requerida para F5.
- **F5 (Despliegue):** Requerida para F6.

**Leyenda:**

- **F0 (Preparación):** Base para todas las fases.
- **F1 (Infraestructura):** Requerida para F2, F3, F4, F5.
- **F2 (Núcleo):** Requerida para F3, F4, F5.
- **F3 (Interfaces):** Requerida para F4, F5.
- **F4 (Pruebas):** Requerida para F5.
- **F5 (Despliegue):** Requerida para F6.

---

## 4. Estrategia de Pruebas por Fase


| **Fase** | **Tipo de Prueba**            | **Herramienta**                | **Criterio de Éxito**                                                  |
| -------- | ----------------------------- | ------------------------------ | ---------------------------------------------------------------------- |
| F0       | Revisión de documentación.    | Markdown + Git                 | Documentos completos y sin errores de formato.                         |
| F1       | Conexión entre servicios.     | Docker Compose + Metabase      | PostgreSQL y Metabase se comunican sin errores.                        |
| F2       | Validación de schema y datos. | PostgreSQL (`psql`)            | Schema creado, datos generados y válidos.                              |
| F2       | Rendimiento de queries.       | PostgreSQL (`EXPLAIN ANALYZE`) | Todas las queries cargan en <2s.                                       |
| F3       | Funcionalidad de paneles.     | Metabase                       | Paneles muestran datos correctos y se exportan a PNG/CSV.              |
| F4       | Rendimiento (p50/p95/p99).         | `measure_query_performance.py` + Docker | Todas las queries tienen p95 <2s con 10 ejecuciones. |
| F4       | Validación de exportaciones.       | `validate_dashboard_exports.py` + Metabase | Exportaciones CSV/XLSX válidas (parsable, non-empty). |
| F4       | Persistencia (roundtrip).          | `test_persistence.sh` + Docker   | Flujo completo: destroy → setup → test.               |
| F4       | Manejo de errores (PG failover).   | `test_error_handling.py` + Docker | Metabase retorna error claro (500/503), sin stack traces. |
| F5       | Reproducibilidad.             | Docker Compose                 | Proyecto funciona en al menos 2 entornos locales diferentes.           |


---

## 5. Revisiones Técnicas Formales (FTRs)


| **Gate**                | **Artefacto a Revisar**               | **Checklist**      | **Participantes** | **Resultado** |
| ----------------------- | ------------------------------------- | ------------------ | ----------------- | ------------- |
| **F0: Preparación**     | Estructura de carpetas y `AGENTS.md`. | Ver detalle abajo. | Fisherk2          | ✅ Aprobado   |
| **F1: Infraestructura** | `docker-compose.yml` y `.env`.        | Ver detalle abajo. | Fisherk2          | ✅ Aprobado   |
| **F2: Núcleo**          | Schema, datos, índices, vistas.       | Ver detalle abajo. | Fisherk2          | ✅ Aprobado   |
| **F3: Interfaces**      | Paneles en Metabase.                  | Ver detalle abajo. | Fisherk2          | ✅ Aprobado   |
| **F4: Pruebas**         | Resultados de pruebas.                | Ver detalle abajo. | Fisherk2          | ✅ Aprobado   |
| **F5: Despliegue**      | `README.md` y documentación final.    | Ver detalle abajo. | Fisherk2          | ✅ Aprobado   |

**Checklist por Gate:**

- **F0: Preparación:**
  - Estructura de carpetas valida.
  - `AGENTS.md` completo.
  - `.gitignore` configurado.
- **F1: Infraestructura:**
  - Servicios se levantan sin errores.
  - Credenciales seguras.
  - Persistencia configurada.
- **F2: Núcleo:**
  - Schema estrella implementado.
  - Datos generados y válidos.
  - Queries optimizadas.
- **F3: Interfaces:**
  - 4 paneles funcionales (Rotación, Stock, Top 10, Alertas).
  - Queries cargan en <2s (validado con EXPLAIN ANALYZE).
  - 2 Metabase Pulses configurados (Stock Crítico + Resumen Ventas).
  - Exportación de colección a JSON determinista.
- **F4: Pruebas:**
  - Todas las queries <2s.
  - Exportación válida.
  - Manejo de errores validado.
- **F5: Despliegue:**
  - `README.md` completo.
  - Guías de usuario y técnica.
  - Proyecto reproducible.

---

## 6. Gestión de Riesgos


| **Riesgo**                                  | **Probabilidad** | **Impacto** | **Mitigación**                                                         | **Contingencia**                                 |
| ------------------------------------------- | ---------------- | ----------- | ---------------------------------------------------------------------- | ------------------------------------------------ |
| **Docker no funciona en el entorno local.** | Media            | Alto        | Validar requisitos (Docker 20+, espacio en disco).                     | Usar máquina virtual con Docker preinstalado.    |
| **Queries lentas (>2s).**                   | Alta             | Alto        | Usar índices, vistas materializadas y particionamiento.                | Reducir volumen de datos para pruebas iniciales. |
| **Metabase no se conecta a PostgreSQL.**    | Media            | Alto        | Verificar credenciales, red de Docker, y puertos.                      | Usar `psql` para validar conexión manualmente.   |
| **Datos generados no son realistas.**       | Media            | Medio       | Ajustar parámetros en `generate_data.py` (ej: distribución de ventas). | Usar datos reales anonimizados como alternativa. |
| **Falta de tiempo para completar el MVP.**  | Alta             | Alto        | Priorizar tareas críticas (F0, F1, F2, F3).                            | Reducir alcance (ej: 2 paneles en lugar de 3).   |
| **Problemas de permisos en Docker.**        | Baja             | Medio       | Usar `chmod` para ajustar permisos en archivos.                        | Ejecutar Docker con `--privileged`.              |
| **Inconsistencia en datos.**                | Media            | Alto        | Usar transacciones en scripts de generación.                           | Regenerar datos desde cero.                      |


---

## 7. Métricas de Progreso


| **Métrica**              | **Valor Objetivo**        | **Herramienta de Medición**           | **Frecuencia** |
| ------------------------ | ------------------------- | ------------------------------------- | -------------- |
| **Velocidad**            | 1 fase por día.           | GitHub/GitLab (commits por día).      | Diaria         |
| **Lead Time**            | <1 día por tarea crítica. | Jira/Trello (tiempo por tarea).       | Diaria         |
| **Defect Density**       | 0 defectos críticos.      | Pruebas manuales + `EXPLAIN ANALYZE`. | Por fase       |
| **Cobertura de Queries** | 100% de queries críticas. | `EXPLAIN ANALYZE` + revisión manual.  | Por fase       |
| **Tiempo de Carga**      | <2s por query.            | Cronómetro manual en Metabase.        | Por fase       |
| **Reproducibilidad**     | 100% en 2+ entornos.      | Docker Compose.                       | Final          |


**Definición de "Done" por Capa:**

- **UI (Metabase):** Paneles funcionales, exportación válida, sin errores de visualización.
- **Lógica (PostgreSQL):** Queries optimizadas, vistas materializadas actualizadas.
- **Datos:** Schema completo, datos generados y válidos.
- **Infraestructura:** Servicios levantados, conexión segura, persistencia configurada.

---

## 8. Cronograma y Hitos

### Diagrama de Gantt (Simplificado)

```mermaid
gantt
    title Cronograma del Proyecto
    dateFormat  YYYY-MM-DD
    section Fases
    F0: Preparación          :done, a1, 2026-07-02, 1d
    F1: Infraestructura     :done, a2, after a1, 1d
    F2: Núcleo              :done, a3, after a2, 2d
    F3: Interfaces          :done, a4, after a3, 1d
    F4: Pruebas             :done, a5, after a4, 1d
    F5: Despliegue          :done, a6, after a5, 1d
    F6: Cierre              :active, a7, after a6, 0.5d
    
    section Hitos
    F3 Interfaces Completado :milestone1, after a4, 0d
    MVP Validado            :milestone2, after a5, 0d
    Proyecto Completado     :milestone3, after a7, 0d
```

### Hitos Clave


| **Hito**                   | **Fecha Estimada** | **Criterio**                                                    |
| -------------------------- | ------------------ | --------------------------------------------------------------- |
| **Plan F2 listo**          | 2026-07-03         | Plan de F2 aprobado, dependencias F0+F1 verificadas.           |
| **F2 completado**          | 2026-07-06         | F2 Núcleo completado: schema + datos + índices + MVs + partición. |
| **F3 Interfaces Completado**| 2026-07-06         | F3 Interfaces completado: setup_metabase.py, 4 paneles, 2 Pulses, code review. |
| **F4 Pruebas Completado**  | 2026-07-06         | F4 Pruebas completado: performance validation, exports, error handling, code review. |
| **MVP Validado**           | 2026-07-06         | Fases F0-F4 completadas, todas las queries <2s, exportación válida, manejo de errores probado. |
| **F5 Despliegue Completado** | 2026-07-07      | F5 completado: README premium, USER_GUIDE, TECHNICAL_GUIDE, REPRODUCIBILITY, code review + fixes. |
| **Proyecto Completado**    | 2026-07-08         | F6 Cierre completado, documentación finalizada, lecciones aprendidas documentadas. |


---

## 9. Control de Cambios y Lecciones Aprendidas


| **Versión** | **Fecha**  | **Autor** | **Cambio**                         | **Lecciones Aprendidas**                                                                                                                                                                                                |
| ----------- | ---------- | --------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0         | 2026-07-02 | Fisherk2  | Versión inicial del `WORKFLOW.md`. | Priorizar tareas críticas (F0, F1, F2, F3) para garantizar el MVP; Usar vistas materializadas para queries frecuentes mejora el rendimiento significativamente; Docker Compose simplifica la orquestación de servicios. |
| 1.1         | 2026-07-03 | Fisherk2  | F0+F1 marcados como completados; F2 listo para planificar. | Vertical slicing reduce checkpoints con misma calidad; tests de runtime con marker permiten CI local sin Docker; named volumes eliminan problemas de permisos de bind mount. |
| 1.2         | 2026-07-06 | Fisherk2  | F2 marcado como completado; F3 listo para planificar. | Generadores Python con distribución Pareto mejoran realismo de datos sintéticos; DROP+RECREATE para particionar funciona en entorno sintético pero requiere CASCADE + refrescar MVs; test_f2.py con estáticos + runtime mantiene calidad sin Docker en CI. |
| 1.3         | 2026-07-06 | Fisherk2  | F3 Interfaces completado; F4 listo para planificar. | REST API de Metabase para setup programático es viable pero requiere manejar edge cases (setup token, parámetros de dashboard, pulsos); source-driven development evitó asumir endpoints incorrectos; code review multi-eje descubrió 24 observaciones incluyendo 2 críticas. |
| 1.4         | 2026-07-06 | Fisherk2  | F4 Pruebas completado; F5 listo para planificar. | Medir rendimiento requiere ejecutar scripts **dentro** del contenedor (no desde el host) porque PostgreSQL no expone puertos; las MVs con nombres de mes en español deben filtrarse por nombre ('Marzo' no '03'); `make test-queries` ahora usa `$(GENERATOR)`. |
| 1.5         | 2026-07-07 | Fisherk2  | F5 completado; F6 listo para planificar. | Documentar para portafolio requiere contenido autocontenido sin capturas de pantalla (solo texto + Mermaid); el proceso de code review multi-eje en docs descubre inconsistencias de datos (155K vs 182K) que estaban propagadas desde un error aritmético en WORKFLOW.md; `make setup` debe incluir `create-views` para ser verdaderamente reproducible. |


---

**Nota:** Este documento debe actualizarse tras cada cambio significativo en el proyecto. Usa el formato de la tabla anterior para registrar cambios y lecciones.