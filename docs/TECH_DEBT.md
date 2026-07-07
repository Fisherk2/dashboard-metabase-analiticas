# Technical Debt Register – Dashboard Metabase + Colección Analítica v1.0.0

**Fecha:** 2026-07-07 | **Autor:** Fisherk2 | **Estado:** Activo
**Coverage actual:** 100% estáticos (test_f0.py + test_f6.py) / runtime con fallas conocidas

---

## 1. Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| Total de ítems | 4 |
| Críticos (P0) | 1 |
| Altos (P1) | 1 |
| Medios (P2) | 2 |
| Bajos (P3) | 1 |
| Ítems cerrados este ciclo | 1 |

---

## 2. Deuda de Infraestructura

### 2.1 Particionamiento de `ventas` rompe FKs de `devoluciones` y `logistica` (TD-002) 🔴 P0

| Campo | Detalle |
|-------|---------|
| **Problema** | La tabla `ventas` está particionada por rango de fechas (12 particiones mensuales), pero el particionamiento se aplicó mediante `DROP + RECREATE` con `CASCADE`. PostgreSQL no permite que tablas externas tengan FOREIGN KEYs hacia una tabla particionada a menos que el índice UNIQUE incluya la partition key. Como resultado, las FKs de `devoluciones.venta_id → ventas.id` y `logistica.venta_id → ventas.id` **no se recrean** tras el particionamiento. La integridad referencial se garantiza solo a nivel de aplicación (via `generate_data.py`). |
| **Por qué está aquí** | El particionamiento se implementó en F2 con datos sintéticos, donde `DROP + RECREATE` era aceptable. Para un escenario de producción, se necesita un enfoque de migración en caliente que preserve las FKs o implemente validaciones alternativas. |
| **Riesgo** | **Crítico** — Integridad referencial rota a nivel de base de datos. Inserción manual o vía scripts externos podría crear huérfanos en `devoluciones` y `logistica`. |
| **Recomendación** | (a) Implementar migración con `pg_partman` (extensión de PostgreSQL) o usar `CREATE TABLE ... PARTITION OF` con captura de datos nuevos mediante triggers. (b) Añadir triggers de validación en `devoluciones` y `logistica` que verifiquen existencia en `ventas`. (c) Documentar explícitamente en SECURITY.md y SCHEMA.md que la integridad se garantiza a nivel de aplicación. |

---

## 3. Deuda de Infraestructura de Pruebas

### 3.1 Tests runtime con credenciales hardcodeadas (TD-003)

| Campo | Detalle |
|-------|---------|
| **Problema** | Los tests de runtime (F1, F2, F3, F4) usan credenciales PostgreSQL hardcodeadas que no coinciden con `.env.example`. Específicamente, asumen `POSTGRES_PASSWORD=postgres` y usuario `postgres` cuando `.env.example` define valores personalizados. |
| **Impacto** | Los tests runtime fallan si el `.env` no coincide con las credenciales hardcodeadas. En CI/CD o en un entorno nuevo, `make test` requiere ajuste manual de credenciales. |
| **Riesgo** | Alto — bloquea la ejecución automatizada de tests runtime en entornos que no sean el del desarrollador original. |
| **Recomendación** | Migrar todos los tests runtime a leer credenciales desde variables de entorno con fallback seguro. Centralizar la configuración de conexión en un helper compartido (`tests/helpers/db.py`). Refactorizar tests para usar fixture de conexión parametrizada. |
| **Progreso** | Parcialmente resuelto en v1.0.0: `test_f2.py` runtime tests ahora leen `POSTGRES_USER`/`POSTGRES_DB` de variables de entorno con fallback a `.env.example`. Pendiente: extender patrón a `test_f1.py`, `test_f3.py`, `test_f4.py` y centralizar en helper compartido. |

### 3.2 Fallas pre-existentes en test suite runtime (TD-004)

| Campo | Detalle |
|-------|---------|
| **Problema** | 9 tests de runtime fallan consistentemente: conflictos de puerto (5432 no expuesto), Metabase no inicializado, y dependencias de Docker no disponibles. Estas fallas son pre-existentes desde F1-F4 y no fueron causadas por cambios recientes. |
| **Impacto** | `make test-full` reporta 9/358 fallas, dando la impresión de código defectuoso. Las fallas son enmascaradas por el CI local que no ejecuta tests runtime. |
| **Riesgo** | Medio — las fallas no afectan la funcionalidad principal (dashboards, queries, datos), pero erosionan la confianza en el test suite y pueden ocultar regresiones reales. |
| **Recomendación** | (a) Mover tests runtime a un marcador separado `@pytest.mark.runtime` que no se ejecute por defecto. (b) Crear un script de CI que ejecute tests runtime solo cuando Docker esté disponible. (c) Documentar en TESTING.md que `make test` solo ejecuta tests estáticos, y `make test-full` incluye runtime. Prioridad: P2. |

---

## 4. Deuda de Proceso

### 4.1 `make setup` no incluía `create-views` (TD-001) — RESUELTO

| Campo | Detalle |
|-------|---------|
| **Problema** | El target `make setup` ejecutaba `up db-init data-generate mv-refresh` pero omitía `create-views`. Esto significaba que las vistas materializadas no se creaban durante el setup inicial, causando errores en `mv-refresh` y en los dashboards de Metabase. |
| **Impacto** | Cualquier persona clonando el repositorio y ejecutando `make setup` obtenía un entorno con datos pero sin vistas, rompiendo los paneles de Metabase que dependen de `mv_rotacion_mensual`, `mv_stock_actual`, y `mv_top_productos`. |
| **Mitigación** | Se añadió el target `create-views` a `make setup` en F5 (commit `7330565`). También se añadió un guard fail-fast para que `mv-refresh` falle temprano si las vistas no existen. |
| **Resolución** | Cerrado en v1.0.0. El Makefile ahora ejecuta: `up → db-init → data-generate → create-views → mv-refresh`. El flujo de setup es reproducible y autocontenido. |

---

## 5. Ítems Cerrados (Histórico)

| ID | Descripción | Cerrado en | Resolución |
|----|-------------|------------|------------|
| TD-001 | `make setup` no incluía `create-views` | v1.0.0 (2026-07-07) | Añadido target `create-views` a `make setup` + fail-fast guard en `mv-refresh`. Commit `7330565`. |

---

## 6. Plan de Reducción (Próximo Ciclo)

| ID | Prioridad | Esfuerzo estimado | Impacto | Asignado a |
|----|-----------|-------------------|---------|------------|
| TD-002 | P0 | 4h | Crítico — integridad referencial rota | Fisherk2 |
| TD-003 | P1 | 4h | Alto — bloquea CI/CD | Fisherk2 |
| TD-004 | P2 | 2h | Medio — confianza en tests | Fisherk2 |

---

*Última actualización: 2026-07-07*
