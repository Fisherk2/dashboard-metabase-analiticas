# SECURITY – Guías de Seguridad

**Fecha:** 2026-07-02 | **Autor:** Fisherk2

---

## 1. Validación de Inputs y Sanitización

| **Componente**    | **Riesgo**             | **Mitigación**                                                      |
| ----------------- | ---------------------- | ------------------------------------------------------------------- |
| **PostgreSQL**    | Inyección SQL.         | Usar **prepared statements** en Python (`psycopg2`).                |
| **Metabase**      | Acceso no autorizado.  | Configurar **permisos de usuario** en Metabase.                     |
| **Script Python** | Inyección de código.   | Validar inputs (ej: `n` debe ser entero en `generate_products(n)`). |
| **Docker**        | Exposición de puertos. | Usar **red interna de Docker** (no exponer PostgreSQL a `0.0.0.0`). |

---

## 2. Control de Excepciones, Timeouts y Rate Limiting

| **Componente**    | **Riesgo**                 | **Mitigación**                                                             |
| ----------------- | -------------------------- | -------------------------------------------------------------------------- |
| **PostgreSQL**    | Queries infinitas.         | Configurar `statement_timeout = 5000` (5s) en PostgreSQL.                  |
| **Metabase**      | Sobrecarga de consultas.   | Limitar el número de paneles simultáneos (configuración de Metabase).      |
| **Script Python** | Conexión colgada.          | Usar `timeout` en conexiones a la BD (ej: `psycopg2.connect(timeout=10)`). |
| **Docker**        | Contenedores sin recursos. | Limitar recursos en `docker-compose.yml` (ej: `mem_limit: 2g`).            |

---

## 3. Gestión de Secretos

- **Nunca** hardcodear credenciales en:
  - Archivos SQL.
  - Scripts Python.
  - `docker-compose.yml` (usar variables de entorno o `.env`).

### Ejemplo Seguro

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # Definido en .env
```

```bash
# .env
POSTGRES_PASSWORD=mi_contraseña_segura
```

### Reglas

- El archivo `.env` **nunca** se commitea (está en `.gitignore`).
- Usar contraseñas fuertes (mínimo 16 caracteres, mezcla de tipos).
- Rotar credenciales si se exponen accidentalmente.

---

## 4. Lista Explicita de Prácticas Prohibidas

| **Práctica Prohibida**                    | **Razón**                                             | **Alternativa**                                                              |
| ----------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| Hardcodear credenciales.                  | Riesgo de exposición en repositorios públicos.        | Usar variables de entorno o secretos de Docker.                              |
| Usar `SELECT *`.                          | Ineficiente y propenso a errores si el schema cambia. | Listar columnas explícitamente.                                              |
| Queries sin índices en columnas críticas. | Rendimiento pobre con volumen alto.                   | Crear índices en columnas usadas en `WHERE`, `JOIN`, `GROUP BY`.             |
| No validar inputs en scripts Python.      | Riesgo de inyección SQL o errores de tipo.            | Validar tipos y sanitizar inputs.                                            |
| Usar `root` o `superuser` en PostgreSQL.  | Riesgo de seguridad (acceso ilimitado).               | Crear usuarios con permisos mínimos (ej: `SELECT` solo).                     |
| No documentar cambios en el schema.       | Dificulta el mantenimiento y la trazabilidad.         | Usar migraciones con convención de nombres (ej: `YYYYMMDD_descripcion.sql`). |
| Ejecutar queries sin `EXPLAIN ANALYZE`.   | No se puede validar el rendimiento.                   | Siempre validar con `EXPLAIN ANALYZE` antes de implementar.                  |
| Usar `JOIN` implícitos.                   | Menos legible y propenso a errores.                   | Usar `JOIN` explícitos (ej: `INNER JOIN`, `LEFT JOIN`).                      |
| No usar transacciones en scripts Python.  | Riesgo de datos inconsistentes si el script falla.    | Usar `BEGIN` y `COMMIT`/`ROLLBACK` en bloques de inserción.                  |
| Exponer PostgreSQL a internet.            | Riesgo de ataques externos.                           | Usar red interna de Docker o firewall.                                       |

---

## 5. Seguridad en Docker

### Red Interna

- PostgreSQL **solo** es accesible desde la red interna de Docker.
- Metabase se conecta a PostgreSQL usando el nombre del servicio (ej: `postgres:5432`).
- El puerto 5432 **no** se expone al host (`0.0.0.0`).

### Volúmenes

- Los datos de PostgreSQL se persisten en volúmenes de Docker (no en el filesystem del host directamente).
- Los volúmenes se limpian con `docker-compose down -v` (solo en desarrollo).

### Imágenes

- Usar imágenes oficiales de Docker Hub (`postgres:15`, `metabase/metabase`).
- No construir imágenes personalizadas con credenciales embebidas.

---

## 6. Manejo de Errores y Fallbacks

| **Escenario**                     | **Manejo de Error**                                                                | **Fallback**                                                        |
| --------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Conexión fallida a PostgreSQL** | Metabase muestra error: "No se pudo conectar a la BD".                             | Revisar credenciales en `docker-compose.yml` y reiniciar servicios. |
| **Query lenta (>2s)**             | PostgreSQL loguea la query lenta (configurar `log_min_duration_statement = 2000`). | Usar vistas materializadas o índices.                               |
| **Datos inconsistentes**          | Validar con `CHECK` constraints en PostgreSQL (ej: `stock_actual >= 0`).           | Corregir datos manualmente o regenerar con el script de Python.     |
| **Script de Python falla**        | Loguear error y continuar con el siguiente registro (si aplica).                   | Ejecutar el script en modo debug (`--debug`).                       |
| **Docker Compose falla**          | Mostrar error de Docker (ej: puerto en uso, imagen no encontrada).                 | Liberar puertos, verificar imágenes, reiniciar Docker.              |
