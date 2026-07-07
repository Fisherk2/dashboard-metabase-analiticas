# ADR-005: Foreign Keys y Particionamiento en PostgreSQL

**Fecha:** 2026-07-03 | **Estado:** Aceptado

## Contexto

Al particionar la tabla `ventas` por rango de fecha (`PARTITION BY RANGE (fecha_venta)`), PostgreSQL exige que:
- La PRIMARY KEY incluya la columna de partición (`PRIMARY KEY (id, fecha_venta)`)
- Cualquier índice UNIQUE incluya la columna de partición

Esto impide que tablas como `devoluciones` y `logistica` tengan FOREIGN KEY referenciando `ventas(id)` (único), porque no existe una constraint UNIQUE en `ventas(id)` sin incluir `fecha_venta`.

## Decisión

Se eliminan las FOREIGN KEY constraints entre `devoluciones → ventas` y `logistica → ventas`.

## Justificación

- **Datos sintéticos**: La integridad referencial se garantiza mediante el script generador (`generate_data.py`), no mediante constraints de BD
- **Rendimiento**: El particionamiento es una optimización de performance demostrable para portafolio, que pesa más que la integridad a nivel BD en este contexto
- **Índices B-tree**: Las columnas FK (`devoluciones.venta_id`, `logistica.venta_id`) mantienen sus índices para JOINs rápidos
- **Fase del proyecto**: F2 es núcleo analítico (OLAP), no transaccional (OLTP). Las FKs son menos críticas en cargas OLAP

## Consecuencias

- Queries que crucen `devoluciones JOIN ventas` seguirán funcionando (los índices existen)
- El script de generación (`generate_data.py`) nunca genera registros huérfanos
- En producción real con datos no sintéticos, se recomendaría:
  - Usar triggers para validación de integridad
  - O aceptar el riesgo de datos huérfanos (OLAP)

## Archivos Afectados

- `sql/partitions/partition_ventas.sql`: No recrea FKs de devoluciones/logistica
- `specs/adr/adr-005-partitioning-fks.md`: Este documento
