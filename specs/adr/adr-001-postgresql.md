# ADR-001: PostgreSQL 15+ como Base de Datos Analítica

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Estado:** Aceptado

---

## Decisión

Usar **PostgreSQL 15+** como base de datos analítica para el dashboard de e-commerce.

---

## Contexto

El proyecto requiere una base de datos que soporte:

- Schema estrella para cargas OLAP (tablas de hechos + dimensiones)
- Vistas materializadas para pre-calcular KPIs críticos
- Particionamiento por rango de fechas para optimizar queries temporales
- Índices B-tree eficientes en columnas de JOIN y WHERE
- Soporte nativo para JSON (flexibilidad futura)
- Conexión JDBC para integración con Metabase

---

## Alternativas Consideradas

### MySQL 8.0+

**Ventajas:**
- Amplia adopción y documentación
- Soporte para vistas materializadas (desde 8.0)
- Buen rendimiento en cargas OLTP

**Desventajas:**
- Particionamiento menos flexible que PostgreSQL
- Menos opciones de índices (no soporta índices parciales, expresiones)
- Soporte limitado para CTEs complejos y window functions avanzadas
- Menos madurez en cargas analíticas puras

**Conclusión:** Descartado por limitaciones en particionamiento y optimización analítica.

---

### SQLite

**Ventajas:**
- Ligero, sin servidor
- Ideal para prototipos rápidos

**Desventajas:**
- No soporta vistas materializadas
- Particionamiento no disponible
- Rendimiento pobre con volúmenes altos (50K–200K registros)
- No soporta conexiones concurrentes robustas
- No soporta JDBC de forma nativa (requiere drivers adicionales)

**Conclusión:** Descartado por limitaciones de escalabilidad y funcionalidad analítica.

---

### MongoDB

**Ventajas:**
- Flexible para datos no estructurados
- Buen rendimiento en lecturas simples

**Desventajas:**
- No soporta schema relacional (star schema)
- No soporta vistas materializadas (solo aggregation pipelines)
- Queries analíticas complejas son menos eficientes
- No soporta JOINs nativos (requiere `$lookup`, menos eficiente)
- Overkill para datos sintéticos estructurados

**Conclusión:** Descartado por incompatibilidad con el patrón star schema y cargas OLAP.

---

## Razones para Elegir PostgreSQL

1. **Soporte nativo para star schema:** PostgreSQL maneja eficientemente tablas de hechos y dimensiones con JOINs optimizados.
2. **Vistas materializadas:** Pre-cálculo de KPIs críticos (rotación, stock, ventas) con refresh manual.
3. **Particionamiento por rango:** Ideal para particionar `ventas` por fechas (mensual).
4. **Índices avanzados:** B-tree, índices parciales, índices en expresiones.
5. **CTEs y window functions:** Queries analíticas complejas con `EXPLAIN ANALYZE` para validación.
6. **Conexión JDBC:** Integración directa con Metabase sin configuración adicional.
7. **Comunidad y documentación:** Amplia documentación, soporte para `pg_stat_statements` para monitoreo.
8. **Reproducibilidad:** Imagen oficial de Docker (`postgres:15`) con volúmenes persistentes.

---

## Consecuencias

### Positivas
- Rendimiento óptimo para cargas OLAP con 50K–200K registros por tabla.
- Capacidad de optimizar queries con `EXPLAIN ANALYZE` y vistas materializadas.
- Particionamiento permite escalar a volúmenes mayores sin degradación.
- Integración sencilla con Metabase mediante JDBC.

### Negativas
- Requiere configuración inicial de índices y vistas materializadas.
- Particionamiento agrega complejidad al schema (pero es opcional para MVP).
- PostgreSQL es más pesado que SQLite (pero necesario para funcionalidad analítica).

### Neutrales
- PostgreSQL 15+ es estable y ampliamente adoptado (no es una apuesta arriesgada).
- La curva de aprendizaje es moderada (SQL estándar + extensiones analíticas).

---

## Validación

```sql
-- Verificar versión
SELECT version();

-- Verificar soporte para vistas materializadas
SELECT matviewname FROM pg_matviews WHERE schemaname = 'public';

-- Verificar soporte para particionamiento
SELECT * FROM pg_partition_tree('ventas');  -- Si se implementa
```

---

## Referencias

- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [PostgreSQL Materialized Views](https://www.postgresql.org/docs/15/rules-materializedviews.html)
- [PostgreSQL Table Partitioning](https://www.postgresql.org/docs/15/ddl-partitioning.html)
- [PostgreSQL JDBC Driver](https://jdbc.postgresql.org/)
