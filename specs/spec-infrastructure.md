# Spec: Infrastructure — Docker Compose Setup

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Fase:** F1

---

## 1. Objetivo

Levantar un entorno reproducible con PostgreSQL 15+ y Metabase OSS mediante Docker Compose. Los servicios deben comunicarse por red interna, persistir datos en volúmenes, y usar credenciales seguras desde `.env`.

---

## 2. Servicios

### 2.1 PostgreSQL

| **Parámetro**       | **Valor**                              |
| ------------------- | -------------------------------------- |
| **Imagen**          | `postgres:15`                          |
| **Puerto interno**  | `5432`                                 |
| **Puerto host**     | No exponer (solo red interna Docker)   |
| **Volumen**         | `pg_data:/var/lib/postgresql/data`     |
| **Variables**       | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| **Healthcheck**     | `pg_isready -U $POSTGRES_USER`         |
| **Red**             | `ecommerce_net` (interna)              |

### 2.2 Metabase

| **Parámetro**       | **Valor**                              |
| ------------------- | -------------------------------------- |
| **Imagen**          | `metabase/metabase:latest`             |
| **Puerto interno**  | `3000`                                 |
| **Puerto host**     | `3000` (acceso local)                  |
| **Volumen**         | `mb_data:/metabase-data`               |
| **Variables**       | `MB_DB_TYPE`, `MB_DB_DBNAME`, `MB_DB_PORT`, `MB_DB_USER`, `MB_DB_PASS`, `MB_DB_HOST` |
| **Dependencia**     | `depends_on: postgres (condition: service_healthy)` |
| **Red**             | `ecommerce_net` (interna)              |

---

## 3. Archivos

| **Archivo**                    | **Ubicación**                  | **Propósito**                              |
| ------------------------------ | ------------------------------ | ------------------------------------------ |
| `docker-compose.yml`           | `docker/docker-compose.yml`    | Orquestación de servicios                  |
| `.env`                         | `/.env`                        | Credenciales (NO commitear)                |
| `.env.example`                 | `/.env.example`                | Template de variables (SÍ commitear)       |
| `.gitignore`                   | `/.gitignore`                  | Excluir `.env`, `*.pyc`, `data/`, `*.log`  |
| `Makefile`                     | `/Makefile`                    | Automatización de comandos (ver [spec-makefile.md](spec-makefile.md)) |

---

## 4. Criterios de Aceptación

- [ ] `make validate` valida sin errores.
- [ ] `make up` levanta ambos servicios.
- [ ] PostgreSQL acepta conexiones desde Metabase (verificar en logs).
- [ ] Metabase accesible en `http://localhost:3000`.
- [ ] Datos persisten tras `make down && make up`.
- [ ] Puerto 5432 NO es accesible desde el host (solo red interna).
- [ ] `.env` está en `.gitignore`.

---

## 5. Dependencias

- **Requiere:** F0 (Preparación — estructura de carpetas).
- **Habilita:** F2 (Núcleo — schema y datos).

---

## 6. Verificación

```bash
# Validar configuración
make validate

# Levantar servicios
make up

# Verificar estado
make status

# Verificar conexión PostgreSQL
make db-check

# Verificar logs
make logs-pg
make logs-mb

# Verificar persistencia
make down
make up
make db-shell -c "SELECT 1;"
```

---

## 7. Notas

- Usar `service_healthy` en `depends_on` para garantizar que PostgreSQL esté listo antes de que Metabase intente conectar.
- El volumen `pg_data` asegura que los datos sobrevivan reinicios de contenedores.
- Metabase usa su propia base de datos interna (H2 por defecto) para configuración de paneles.
