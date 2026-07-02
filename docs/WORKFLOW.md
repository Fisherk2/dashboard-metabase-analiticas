# Workflow – Dashboard Metabase + Colección Analítica para E-commerce v1.0

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Metodología:** Iterativo

---

## 1. Visión de Fases


| **Fase**                | **Objetivo**                                                    | **Entregables**                                                                                  | **Duración Estimada** |
| ----------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------- |
| **F0: Preparación**     | Configurar entorno base, convenciones y documentación inicial.  | Estructura de carpetas, `.gitignore`, `README.md` (borrador), `AGENTS.md`, `ARCHITECTURE.md`.    | 1 día                 |
| **F1: Infraestructura** | Levantar servicios de PostgreSQL y Metabase con Docker.         | `docker-compose.yml`, credenciales seguras, conexión funcional entre Metabase y PostgreSQL.      | 1 día                 |
| **F2: Núcleo**          | Implementar schema estrella, generar datos y optimizar queries. | Script `generate_data.py`, schema SQL, índices, vistas materializadas, particionamiento.         | 2 días                |
| **F3: Interfaces**      | Configurar paneles en Metabase y validar queries.               | 3+ paneles en Metabase (rotación, stock, ventas), queries optimizadas.                           | 1 día                 |
| **F4: Pruebas**         | Validar rendimiento, exportación y flujos completos.            | Resultados de `EXPLAIN ANALYZE`, pruebas de exportación, validación de paneles.                  | 1 día                 |
| **F5: Despliegue**      | Documentar el proyecto y preparar para portafolio.              | `README.md` final con badges, guías de usuario, capturas de pantalla, video tutorial (opcional). | 1 día                 |
| **F6: Cierre**          | Revisión final y lecciones aprendidas.                          | Retrospectiva documentada, actualización de `AGENTS.md` y `WORKFLOW.md`.                         | 0.5 días              |


---

## 2. Desglose por Fase

### Fase 0: Preparación

**Objetivo:** Establecer la base del proyecto con estructura clara y documentación inicial.


| **ID** | **Tarea**                                                              | **Responsable** | **Estimación** | **DoD (Definition of Done)**                                                                    |
| ------ | ---------------------------------------------------------------------- | --------------- | -------------- | ----------------------------------------------------------------------------------------------- |
| F0-01  | Crear estructura de carpetas (`/docs`, `/scripts`, `/sql`, `/docker`). | Fisherk2     | 1 hora         | Estructura de carpetas validada y versionada en Git.                                            |
| F0-02  | Configurar `.gitignore` para Python, SQL, Docker y Metabase.           | Fisherk2     | 0.5 horas      | Archivo `.gitignore` incluye patrones para `.env`, `*.pyc`, `*.log`, `data/`, etc.              |
| F0-03  | Crear `README.md` inicial con descripción del proyecto y badges.       | Fisherk2     | 1 hora         | `README.md` incluye: título, descripción, stack tecnológico, badges, y enlaces a documentación. |
| F0-04  | Crear `AGENTS.md` (este documento) y `ARCHITECTURE.md`.                | Fisherk2     | 2 horas        | Documentos completos y revisados.                                                               |
| F0-05  | Configurar linters/formateadores para SQL y Python (opcional).         | Fisherk2     | 1 hora         | Configuración de `sqlfluff` (SQL) y `black`/`flake8` (Python) en pre-commit.                    |


**Dependencias:**

- **Requeridas:** Ninguna.
- **Opcionales:** Herramientas de linter (ej: `sqlfluff`, `black`).

---

### Fase 1: Infraestructura

**Objetivo:** Levantar un entorno reproducible con PostgreSQL y Metabase.


| **ID** | **Tarea**                                                             | **Responsable** | **Estimación** | **DoD (Definition of Done)**                                          |
| ------ | --------------------------------------------------------------------- | --------------- | -------------- | --------------------------------------------------------------------- |
| F1-01  | Crear `docker-compose.yml` con servicios para PostgreSQL y Metabase.  | Fisherk2     | 1 hora         | Archivo valida con `docker-compose config`.                           |
| F1-02  | Configurar credenciales seguras en variables de entorno (`.env`).     | Fisherk2     | 0.5 horas      | `.env` incluye `POSTGRES_PASSWORD`, `POSTGRES_USER`, y `POSTGRES_DB`. |
| F1-03  | Levantar servicios con `docker-compose up -d`.                        | Fisherk2     | 0.5 horas      | PostgreSQL y Metabase están en ejecución sin errores.                 |
| F1-04  | Verificar conexión entre Metabase y PostgreSQL.                       | Fisherk2     | 0.5 horas      | Metabase muestra la base de datos PostgreSQL como opción de conexión. |
| F1-05  | Configurar persistencia de datos en PostgreSQL (volúmenes de Docker). | Fisherk2     | 0.5 horas      | Datos persisten tras reiniciar contenedores.                          |


**Dependencias:**

- **Requeridas:** F0 (Preparación).

---

### Fase 2: Núcleo

**Objetivo:** Implementar el schema estrella, generar datos sintéticos y optimizar queries.


| **ID** | **Tarea**                                                                        | **Responsable** | **Estimación** | **DoD (Definition of Done)**                                                            |
| ------ | -------------------------------------------------------------------------------- | --------------- | -------------- | --------------------------------------------------------------------------------------- |
| F2-01  | Crear script `init.sql` con el schema estrella (tablas de hechos y dimensiones). | Fisherk2     | 2 horas        | Script ejecuta sin errores en PostgreSQL.                                               |
| F2-02  | Ejecutar `init.sql` en PostgreSQL para crear el schema.                          | Fisherk2     | 0.5 horas      | Tablas creadas y validadas con `SELECT * FROM information_schema.tables;`.              |
| F2-03  | Desarrollar script `generate_data.py` para generar datos sintéticos.             | Fisherk2     | 3 horas        | Script genera 50K–200K registros por tabla de hechos y 1K–10K por tabla de dimensiones. |
| F2-04  | Ejecutar `generate_data.py` para poblar la base de datos.                        | Fisherk2     | 1 hora         | Datos insertados y validados con `SELECT COUNT(*) FROM tabla;`.                         |
| F2-05  | Crear índices en columnas críticas (ej: `producto_id`, `fecha_id`).              | Fisherk2     | 1 hora         | Índices creados y validados con `SELECT * FROM pg_indexes;`.                            |
| F2-06  | Crear vistas materializadas para KPIs críticos (rotación, stock, ventas).        | Fisherk2     | 1 hora         | Vistas creadas y actualizadas con `REFRESH MATERIALIZED VIEW`.                          |
| F2-07  | Particionar tabla `ventas` por rango de fechas (opcional).                       | Fisherk2     | 1 hora         | Tabla `ventas` particionada y validada con `SELECT * FROM pg_partitions;`.              |


**Dependencias:**

- **Requeridas:** F1 (Infraestructura).

---

### Fase 3: Interfaces

**Objetivo:** Configurar paneles en Metabase y validar queries.


| **ID** | **Tarea**                                                           | **Responsable** | **Estimación** | **DoD (Definition of Done)**                                                      |
| ------ | ------------------------------------------------------------------- | --------------- | -------------- | --------------------------------------------------------------------------------- |
| F3-01  | Conectar Metabase a PostgreSQL y configurar permisos.               | Fisherk2     | 0.5 horas      | Metabase puede ejecutar queries en PostgreSQL.                                    |
| F3-02  | Crear panel "Rotación por Categoría" en Metabase.                   | Fisherk2     | 1 hora         | Panel muestra datos correctos y se carga en <2s.                                  |
| F3-03  | Crear panel "Stock Actual vs. Mínimo" en Metabase.                  | Fisherk2     | 1 hora         | Panel muestra alertas de stock mínimo y se carga en <2s.                          |
| F3-04  | Crear panel "Ventas por Producto (Top 10)" en Metabase.             | Fisherk2     | 1 hora         | Panel muestra los 10 productos con más ventas y se carga en <2s.                  |
| F3-05  | Validar que todas las queries usen índices y vistas materializadas. | Fisherk2     | 1 hora         | `EXPLAIN ANALYZE` muestra planes de ejecución optimizados para todas las queries. |
| F3-06  | Configurar alertas de stock mínimo en Metabase (opcional).          | Fisherk2     | 0.5 horas      | Alertas configuradas y visibles en el dashboard.                                  |


**Dependencias:**

- **Requeridas:** F2 (Núcleo).

---

### Fase 4: Pruebas

**Objetivo:** Validar rendimiento, exportación y flujos completos.


| **ID** | **Tarea**                                                                  | **Responsable** | **Estimación** | **DoD (Definition of Done)**                      |
| ------ | -------------------------------------------------------------------------- | --------------- | -------------- | ------------------------------------------------- |
| F4-01  | Ejecutar `EXPLAIN ANALYZE` en todas las queries críticas.                  | Fisherk2     | 1 hora         | Todas las queries cargan en <2s.                  |
| F4-02  | Validar exportación de paneles a PNG/CSV.                                  | Fisherk2     | 0.5 horas      | Archivos exportados son correctos y legibles.     |
| F4-03  | Probar flujos de navegación en Metabase (ej: filtrar por fecha/categoría). | Fisherk2     | 1 hora         | Todos los flujos funcionan sin errores.           |
| F4-04  | Validar persistencia de datos tras reiniciar contenedores.                 | Fisherk2     | 0.5 horas      | Datos persisten y los paneles siguen funcionando. |
| F4-05  | Probar conexión fallida a PostgreSQL y validar manejo de errores.          | Fisherk2     | 0.5 horas      | Metabase muestra mensaje de error claro.          |


**Dependencias:**

- **Requeridas:** F3 (Interfaces).

---

### Fase 5: Despliegue

**Objetivo:** Documentar el proyecto y preparar para portafolio.


| **ID** | **Tarea**                                                | **Responsable** | **Estimación** | **DoD (Definition of Done)**                                             |
| ------ | -------------------------------------------------------- | --------------- | -------------- | ------------------------------------------------------------------------ |
| F5-01  | Actualizar `README.md` (ver detalle abajo).              | Fisherk2        | 2 horas        | `README.md` completo y revisado.                                         |
| F5-02  | Crear guía de usuario en `/docs/USER_GUIDE.md`.          | Fisherk2        | 1 hora         | Guía incluye: cómo usar Metabase, interpretar paneles, y exportar datos. |
| F5-03  | Crear guía técnica en `/docs/TECHNICAL_GUIDE.md`.        | Fisherk2        | 1 hora         | Guía incluye: arquitectura, schema, queries, y optimizaciones.           |
| F5-04  | Grabar video tutorial (opcional).                        | Fisherk2        | 1 hora         | Video de 5–10 min mostrando el flujo completo.                           |
| F5-05  | Validar que el proyecto es reproducible en otro entorno. | Fisherk2        | 1 hora         | Proyecto funciona en al menos 2 entornos locales diferentes.             |

**Detalle F5-01 — Actualizar `README.md` con:**
- Pasos para levantar el proyecto.
- Capturas de pantalla de los paneles.
- Badges de tecnologías.

**Dependencias:**

- **Requeridas:** F4 (Pruebas).

---

### Fase 6: Cierre

**Objetivo:** Revisión final y documentación de lecciones aprendidas.


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

---

## 4. Estrategia de Pruebas por Fase


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

## 5. Revisiones Técnicas Formales (FTRs)


| **Gate**                | **Artefacto a Revisar**               | **Checklist**      | **Participantes** | **Resultado** |
| ----------------------- | ------------------------------------- | ------------------ | ----------------- | ------------- |
| **F0: Preparación**     | Estructura de carpetas y `AGENTS.md`. | Ver detalle abajo. | Fisherk2          | Pendiente     |
| **F1: Infraestructura** | `docker-compose.yml` y `.env`.        | Ver detalle abajo. | Fisherk2          | Pendiente     |
| **F2: Núcleo**          | Schema, datos, índices, vistas.       | Ver detalle abajo. | Fisherk2          | Pendiente     |
| **F3: Interfaces**      | Paneles en Metabase.                  | Ver detalle abajo. | Fisherk2          | Pendiente     |
| **F4: Pruebas**         | Resultados de pruebas.                | Ver detalle abajo. | Fisherk2          | Pendiente     |
| **F5: Despliegue**      | `README.md` y documentación final.    | Ver detalle abajo. | Fisherk2          | Pendiente     |

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
  - 3+ paneles funcionales.
  - Queries cargan en <2s.
  - Exportación funciona.
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
    F0: Preparación          :a1, 2026-07-02, 1d
    F1: Infraestructura     :a2, after a1, 1d
    F2: Núcleo              :a3, after a2, 2d
    F3: Interfaces          :a4, after a3, 1d
    F4: Pruebas             :a5, after a4, 1d
    F5: Despliegue          :a6, after a5, 1d
    F6: Cierre              :a7, after a6, 0.5d
    
    section Hitos
    MVP Listo para Pruebas  :milestone1, after a3, 0d
    MVP Validado            :milestone2, after a5, 0d
    Proyecto Completado     :milestone3, after a7, 0d
```

### Hitos Clave


| **Hito**                   | **Fecha Estimada** | **Criterio**                                         |
| -------------------------- | ------------------ | ---------------------------------------------------- |
| **MVP Listo para Pruebas** | 2026-07-05         | Fases F0, F1, F2, F3 completadas.                    |
| **MVP Validado**           | 2026-07-06         | Fases F4 completadas, todas las queries <2s.         |
| **Proyecto Completado**    | 2026-07-07         | Fases F5 y F6 completadas, documentación finalizada. |


---

## 9. Control de Cambios y Lecciones Aprendidas


| **Versión** | **Fecha**  | **Autor** | **Cambio**                         | **Lecciones Aprendidas**                                                                                                                                                                                                |
| ----------- | ---------- | --------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0         | 2026-07-02 | Fisherk2  | Versión inicial del `WORKFLOW.md`. | Priorizar tareas críticas (F0, F1, F2, F3) para garantizar el MVP; Usar vistas materializadas para queries frecuentes mejora el rendimiento significativamente; Docker Compose simplifica la orquestación de servicios. |


---

**Nota:** Este documento debe actualizarse tras cada cambio significativo en el proyecto. Usa el formato de la tabla anterior para registrar cambios y lecciones.