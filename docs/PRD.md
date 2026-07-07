# Product Requirements Document – Dashboard Metabase + Colección Analítica para E-commerce v1.0

**Fecha:** 2026-07-07 | **Autor:** Fisherk2 | **Estado:** ✅ Aprobado v1.0.0

---

## 0. Descripción General

Dashboard analítico conectado a **PostgreSQL** para visualizar **KPIs de inventario, rotación y alertas de stock mínimo** en un e-commerce. El proyecto usa **Metabase** como herramienta de visualización y un **schema estrella para OLAP** en PostgreSQL, optimizado para consultas rápidas (<2s por vista).

**Objetivo:** Proporcionar una solución de business intelligence (BI) ligera, escalable y reproducible para análisis de datos en tiempo real, usando tecnologías open-source y patrones arquitectónicos robustos.

---

## 1. Visión y Problema


| **Aspecto**               | **Detalle**                                                                                                                                                                                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Problema que resuelve** | Falta de visibilidad en tiempo real sobre el inventario, rotación de productos y alertas de stock mínimo en e-commerce.                                                                                                                             |
| **Propuesta de valor**    | Dashboard centralizado con KPIs críticos, exportable a PNG/CSV, y consultas optimizadas para toma de decisiones ágil.                                                                                                                               |
| **Alcance del MVP**       | **In:** 3+ paneles en Metabase, conexión segura a PostgreSQL, queries optimizadas, schema estrella, generación de datos sintéticos. **Out:** Lógica de negocio fuera de la BD, integración con sistemas externos (ej: ERP), autenticación avanzada. |


---

## 2. Público Objetivo & Personas


| **Persona**            | **Rol**               | **Necesidad Principal**                                                       | **Frecuencia de Uso** |
| ---------------------- | --------------------- | ----------------------------------------------------------------------------- | --------------------- |
| Gerente de Operaciones | Tomador de decisiones | Monitorear KPIs de inventario y rotación para optimizar cadena de suministro. | Diaria                |
| Analista de Datos      | Usuario técnico       | Extraer insights de ventas e inventario mediante queries y visualizaciones.   | Diaria                |
| Desarrollador Backend  | Implementador         | Validar rendimiento de queries y estructura de la BD.                         | Semanal               |
| Dueño del E-commerce   | Stakeholder           | Recibir alertas de stock mínimo y reportes de rotación.                       | Semanal               |


---

## 3. Historias de Usuario / Casos de Uso (Priorizadas)


| **ID** | **Como [rol]**         | **Quiero [acción]**                                                                     | **Para [beneficio]**                                                      | **Prioridad** | **Criterios de Aceptación**                                                                             |
| ------ | ---------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------- |
| US-01  | Gerente de Operaciones | Ver un panel con KPIs de rotación de productos por categoría.                           | Identificar productos de bajo movimiento y ajustar estrategias de compra. | Alta          | Panel cargado en <2s, datos actualizados, exportable a PNG/CSV.                                         |
| US-02  | Analista de Datos      | Ejecutar queries personalizadas sobre inventario y ventas.                              | Generar reportes ad-hoc sin depender del equipo de desarrollo.            | Alta          | Queries con tiempo de respuesta <2s, acceso a vistas materializadas.                                    |
| US-03  | Desarrollador Backend  | Validar que las queries SQL estén optimizadas.                                          | Garantizar rendimiento del sistema bajo carga.                            | Alta          | `EXPLAIN ANALYZE` muestra planes de ejecución eficientes, índices y vistas materializadas configurados. |
| US-04  | Dueño del E-commerce   | Recibir alertas automáticas cuando el stock de un producto caiga por debajo del mínimo. | Evitar ventas perdidas por falta de inventario.                           | Media         | Alertas visibles en Metabase, configurables por producto/categoría.                                     |
| US-05  | Gerente de Operaciones | Comparar el rendimiento de ventas entre categorías y proveedores.                       | Optimizar la mezcla de productos y relaciones con proveedores.            | Media         | Panel comparativo con gráficos de barras/lines, datos exportables.                                      |


---

## 4. Requisitos Funcionales


| **REQ-ID** | **Descripción**                                                              | **Reglas de Negocio**                                                                                          | **Estado**  | **Trazabilidad**    |
| ---------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------- | ------------------- |
| RF-01      | Conexión segura entre Metabase y PostgreSQL.                                 | Usar credenciales cifradas (variables de entorno en Docker), SSL/TLS opcional.                                 | Completado  | US-01, US-02, US-03 |
| RF-02      | 4 paneles configurados en Metabase (Rotación, Stock, Top 10, Alertas).       | Paneles con filtros por categoría/estado, queries <2s, exportables a PNG/CSV.                                  | Completado  | US-01, US-04, US-05 |
| RF-03      | Exportación de paneles a PNG/CSV/JSON/XLSX.                                  | Metabase permite exportación manual desde la UI y vía API de exportación.                                      | Completado  | US-01, US-02        |
| RF-04      | Queries SQL optimizadas para carga en <2s.                                   | Índices (9+ B-tree), vistas materializadas (3 MVs), y particionamiento mensual en `ventas`.                   | Completado  | US-03               |
| RF-05      | Schema estrella para OLAP en PostgreSQL.                                     | 4 fact tables + 6 dimension tables con explicit FKs, CHECK constraints, B-tree indexes.                       | Completado  | US-01, US-02, US-03 |
| RF-06      | Generación de datos sintéticos con Python + Faker.                           | Script reproducible para ~182K registros totales con distribución Pareto.                                      | Completado  | US-03               |
| RF-07      | Alertas de stock mínimo configurables.                                       | 2 Metabase Pulses configurados: Stock Crítico (09:00) + Resumen Ventas (18:00).                                | Completado  | US-04               |


---

## 5. Requisitos No Funcionales


| **Categoría**      | **Requisito**                                        | **Métrica/Detalle**                                                                  |
| ------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Rendimiento**    | Tiempo de carga por vista en Metabase.               | <2 segundos (validado con `EXPLAIN ANALYZE` en PostgreSQL).                          |
| **Seguridad**      | Conexión segura entre Metabase y PostgreSQL.         | Credenciales en variables de entorno, acceso restringido a la red interna de Docker. |
| **Escalabilidad**  | Capacidad para manejar 50K–200K registros por tabla. | PostgreSQL con configuración por defecto + índices y vistas materializadas.          |
| **Usabilidad**     | Interfaz intuitiva en Metabase.                      | Paneles claros, con filtros por fecha/categoría/proveedor.                           |
| **Disponibilidad** | Entorno reproducible localmente.                     | Docker Compose con servicios de PostgreSQL y Metabase.                               |
| **Mantenibilidad** | Documentación completa y scripts versionados.        | README con badges, guías en Markdown, scripts en `/scripts`.                         |


---

## 6. Métricas de Éxito (KPIs)


| **Métrica**                           | **Valor Objetivo**                   | **Método de Medición**                                           |
| ------------------------------------- | ------------------------------------ | ---------------------------------------------------------------- |
| Tiempo de carga por panel en Metabase | <2 segundos                          | `EXPLAIN ANALYZE` en PostgreSQL + cronómetro manual en Metabase. |
| Cobertura de KPIs                     | 3+ paneles funcionales               | Revisión manual de paneles en Metabase.                          |
| Volumen de datos                      | 50K–200K registros por tabla         | Conteo de filas en PostgreSQL (`SELECT COUNT(*) FROM tabla;`).   |
| Satisfacción del usuario              | 100% de requisitos funcionales       | Validación con stakeholders (ej: Gerente de Operaciones).        |
| Reproducibilidad del entorno          | 100% de éxito en `docker-compose up` | Pruebas en 3 entornos locales diferentes.                        |


---

## 7. Supuestos, Restricciones y Dependencias


| **Tipo**          | **Detalle**                                                                          |
| ----------------- | ------------------------------------------------------------------------------------ |
| **Supuestos**     | - El usuario tiene Docker y Docker Compose instalados.                               |
| &nbsp;            | - PostgreSQL 15+ y Metabase latest son compatibles con el hardware local.            |
| &nbsp;            | - Los datos sintéticos son suficientes para validar el MVP.                          |
| **Restricciones** | - No se implementará lógica de negocio fuera de PostgreSQL (ej: triggers complejos). |
| &nbsp;            | - No se usará autenticación avanzada (ej: OAuth) en Metabase.                        |
| &nbsp;            | - El proyecto es para uso local (no producción).                                     |
| **Dependencias**  | - Docker (v20+), Docker Compose (v2+).                                               |
| &nbsp;            | - Python 3.8+ (para generación de datos).                                            |
| &nbsp;            | - PostgreSQL 15+, Metabase latest.                                                   |


---

## 8. Control de Cambios


| **Versión** | **Fecha**  | **Autor**   | **Cambio**                                        | **Aprobado por** |
| ----------- | ---------- | ----------- | ------------------------------------------------- | ---------------- |
| 1.0         | 2026-07-02 | Fisherk2    | Versión inicial del PRD.                          | Fisherk2         |
| 1.0.0       | 2026-07-07 | Fisherk2    | Actualizado a estado Aprobado v1.0.0 para release.  | Fisherk2         |

---

## 9. Resultados de la Implementación v1.0.0

| **Métrica**                       | **Resultado**                                        |
| --------------------------------- | ---------------------------------------------------- |
| Registros generados               | ~182K totales (100K ventas, 50K inventario, etc.)   |
| Tiempo de carga (p95)             | <2.1ms (4 queries, 10 ejecuciones cada una)         |
| Paneles en Metabase               | 4 (Rotación, Stock, Top 10, Alertas)                |
| Metabase Pulses                   | 2 (Stock Crítico + Resumen Ventas)                  |
| Reproducibilidad                  | ✅ Verificada (make setup exit 0 en entorno limpio) |
| Tests estáticos                   | 73/73 passing (test_f0.py)                          |

___