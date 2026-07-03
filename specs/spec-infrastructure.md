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

---

## 4. Criterios de Aceptación

- [ ] `docker-compose config` valida sin errores.
- [ ] `docker-compose up -d` levanta ambos servicios.
- [ ] PostgreSQL acepta conexiones desde Metabase (verificar en logs).
- [ ] Metabase accesible en `http://localhost:3000`.
- [ ] Datos persisten tras `docker-compose down && docker-compose up -d`.
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
docker-compose config

# Levantar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Verificar conexión PostgreSQL
docker exec -it postgres pg_isready -U admin

# Verificar logs
docker-compose logs -f postgres
docker-compose logs -f metabase

# Verificar persistencia
docker-compose down
docker-compose up -d
docker exec -it postgres psql -U admin -d ecommerce -c "SELECT 1;"
```

---

## 7. Notas

- Usar `service_healthy` en `depends_on` para garantizar que PostgreSQL esté listo antes de que Metabase intente conectar.
- El volumen `pg_data` asegura que los datos sobrevivan reinicios de contenedores.
- Metabase usa su propia base de datos interna (H2 por defecto) para configuración de paneles.
