# Spec: Makefile — Automatización de Comandos del Proyecto

**Fecha:** 2026-07-03 | **Autor:** Fisherk2 | **Fase:** F0

---

## 1. Objetivo

Crear un `Makefile` en la raíz del proyecto que centralice y simplifique todos los comandos de desarrollo, infraestructura, generación de datos, validación y limpieza. El Makefile actúa como **única interfaz de comandos** del proyecto, eliminando la necesidad de recordar comandos largos o rutas específicas.

---

## 2. Decisiones de Diseño

| **Aspecto**          | **Decisión**                                                                 |
| -------------------- | -------------------------------------------------------------------------- |
| **Herramienta**      | `make` (GNU Make) — preinstalado en Linux/macOS, universal                 |
| **Ubicación**        | `Makefile` en la raíz del proyecto                                         |
| **Convención**       | Targets en `kebab-case` (ej: `make db-init`, `make data-generate`)         |
| **Variables**        | Usar `include .env` para cargar credenciales automáticamente               |
| **Phony targets**    | Declarar `.PHONY` para todos los targets no-file                           |
| **Help**             | Target `make help` como default — lista todos los comandos disponibles     |
| **Idempotencia**     | Targets de setup deben ser seguros de ejecutar múltiples veces             |

---

## 3. Targets Requeridos

### 3.1 Infraestructura (Docker)

| **Target**           | **Comando Equivalente**                    | **Descripción**                          |
| -------------------- | ------------------------------------------ | ---------------------------------------- |
| `make up`            | `docker-compose up -d`                     | Levantar PostgreSQL + Metabase           |
| `make down`          | `docker-compose down`                      | Detener todos los servicios              |
| `make restart`       | `make down && make up`                     | Reiniciar servicios                      |
| `make logs`          | `docker-compose logs -f`                   | Ver logs de todos los servicios          |
| `make logs-pg`       | `docker-compose logs -f postgres`          | Ver logs de PostgreSQL                   |
| `make logs-mb`       | `docker-compose logs -f metabase`          | Ver logs de Metabase                     |
| `make status`        | `docker-compose ps`                        | Estado de los servicios                  |
| `make validate`      | `docker-compose config`                    | Validar docker-compose.yml               |
| `make destroy`       | `docker-compose down -v`                   | Detener y eliminar volúmenes (⚠️ datos)  |

### 3.2 Base de Datos

| **Target**           | **Comando Equivalente**                              | **Descripción**                    |
| -------------------- | ---------------------------------------------------- | ---------------------------------- |
| `make db-shell`      | `docker exec -it postgres psql -U admin -d ecommerce`| Conectar a psql interactivo        |
| `make db-init`       | `psql ... -f scripts/init.sql`                       | Ejecutar schema inicial            |
| `make db-reset`      | Drop + recreate + init.sql                           | Reiniciar BD desde cero            |
| `make db-check`      | `docker exec -it postgres pg_isready -U admin`       | Verificar que PostgreSQL está listo|

### 3.3 Datos Sintéticos

| **Target**           | **Comando Equivalente**                              | **Descripción**                    |
| -------------------- | ---------------------------------------------------- | ---------------------------------- |
| `make deps`          | `pip install -r scripts/requirements.txt`            | Instalar dependencias Python       |
| `make data-generate` | `python scripts/generate_data.py`                    | Generar datos sintéticos           |
| `make data-debug`    | `python scripts/generate_data.py --debug`            | Generar datos con logs detallados  |
| `make data-count`    | `SELECT COUNT(*) ...` para todas las tablas          | Contar registros por tabla         |

### 3.4 Optimización SQL

| **Target**           | **Comando Equivalente**                              | **Descripción**                    |
| -------------------- | ---------------------------------------------------- | ---------------------------------- |
| `make mv-refresh`    | `psql ... -f scripts/refresh_materialized_views.sql` | Refrescar vistas materializadas    |
| `make indexes-check` | `SELECT * FROM pg_indexes ...`                       | Listar todos los índices           |

### 3.5 Validación y Testing

| **Target**           | **Comando Equivalente**                              | **Descripción**                    |
| -------------------- | ---------------------------------------------------- | ---------------------------------- |
| `make test-queries`  | Ejecutar `EXPLAIN ANALYZE` en queries críticas       | Validar rendimiento <2s            |
| `make test-integrity`| Verificar integridad referencial (FKs válidas)       | Validar datos generados            |
| `make test-full`     | `make test-queries && make test-integrity`           | Ejecutar todas las pruebas         |

### 3.6 Utilidades

| **Target**           | **Comando Equivalente**                              | **Descripción**                    |
| -------------------- | ---------------------------------------------------- | ---------------------------------- |
| `make help`          | Listar todos los targets con descripciones           | **Target default**                 |
| `make setup`         | `make deps && make up && make db-init && make data-generate` | Setup completo del proyecto  |
| `make clean`         | Eliminar `__pycache__`, `*.pyc`, logs                | Limpiar archivos temporales        |

---

## 4. Estructura del Makefile

```makefile
# Makefile — Dashboard Metabase + Colección Analítica
# Uso: make [target] | make help

# ─── Variables ───────────────────────────────────────────────
include .env
export

DOCKER_COMPOSE = docker-compose
PSQL = docker exec -it postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
PYTHON = python
PIP = pip

# ─── Default ─────────────────────────────────────────────────
.DEFAULT_GOAL := help

# ─── Help ────────────────────────────────────────────────────
help: ## Mostrar ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ─── Infrastructure ──────────────────────────────────────────
.PHONY: up down restart logs logs-pg logs-mb status validate destroy

up: ## Levantar PostgreSQL + Metabase
	$(DOCKER_COMPOSE) up -d

down: ## Detener servicios
	$(DOCKER_COMPOSE) down

restart: down up ## Reiniciar servicios

logs: ## Ver logs de todos los servicios
	$(DOCKER_COMPOSE) logs -f

logs-pg: ## Ver logs de PostgreSQL
	$(DOCKER_COMPOSE) logs -f postgres

logs-mb: ## Ver logs de Metabase
	$(DOCKER_COMPOSE) logs -f metabase

status: ## Estado de los servicios
	$(DOCKER_COMPOSE) ps

validate: ## Validar docker-compose.yml
	$(DOCKER_COMPOSE) config

destroy: ## ⚠️ Detener y eliminar volúmenes (pierde datos)
	$(DOCKER_COMPOSE) down -v

# ─── Database ────────────────────────────────────────────────
.PHONY: db-shell db-init db-reset db-check

db-shell: ## Conectar a psql interactivo
	docker exec -it postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-init: ## Ejecutar schema inicial
	$(PSQL) -f scripts/init.sql

db-reset: db-destroy db-init ## ⚠️ Reiniciar BD desde cero

db-check: ## Verificar que PostgreSQL está listo
	docker exec -it postgres pg_isready -U $(POSTGRES_USER)

# ─── Data Generation ─────────────────────────────────────────
.PHONY: deps data-generate data-debug data-count

deps: ## Instalar dependencias Python
	$(PIP) install -r scripts/requirements.txt

data-generate: ## Generar datos sintéticos
	$(PYTHON) scripts/generate_data.py

data-debug: ## Generar datos con logs detallados
	$(PYTHON) scripts/generate_data.py --debug

data-count: ## Contar registros por tabla
	$(PSQL) -c "SELECT 'productos' AS tabla, COUNT(*) FROM productos ..."

# ─── SQL Optimization ────────────────────────────────────────
.PHONY: mv-refresh indexes-check

mv-refresh: ## Refrescar vistas materializadas
	$(PSQL) -f scripts/refresh_materialized_views.sql

indexes-check: ## Listar todos los índices
	$(PSQL) -c "SELECT indexname, tablename FROM pg_indexes ..."

# ─── Testing ─────────────────────────────────────────────────
.PHONY: test-queries test-integrity test-full

test-queries: ## Validar rendimiento de queries (<2s)
	$(PSQL) -c "EXPLAIN ANALYZE SELECT ..."

test-integrity: ## Validar integridad referencial
	$(PSQL) -c "SELECT COUNT(*) AS orphan_sales ..."

test-full: test-queries test-integrity ## Ejecutar todas las pruebas

# ─── Utilities ───────────────────────────────────────────────
.PHONY: setup clean

setup: deps up db-init data-generate ## Setup completo del proyecto

clean: ## Limpiar archivos temporales
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

---

## 5. Convenciones

1. **Targets en `kebab-case`:** `make db-init`, no `make db_init` ni `make DbInit`.
2. **Comentarios `##`:** Cada target tiene un comentario `##` para `make help`.
3. **`.PHONY` declarado:** Todos los targets no-file deben declararse `.PHONY`.
4. **Variables desde `.env`:** El Makefile carga `.env` automáticamente con `include .env`.
5. **Target `help` como default:** `.DEFAULT_GOAL := help` — ejecutar `make` sin args muestra ayuda.
6. **Targets destructivos con advertencia:** `destroy` y `db-reset` incluyen `⚠️` en la descripción.
7. **Agrupación por sección:** Infrastructure, Database, Data, SQL, Testing, Utilities.
8. **Variables reutilizables:** `$(DOCKER_COMPOSE)`, `$(PSQL)`, `$(PYTHON)` — no repetir comandos largos.

---

## 6. Archivos

| **Archivo**   | **Ubicación**  | **Propósito**                              |
| ------------- | -------------- | ------------------------------------------ |
| `Makefile`    | `/Makefile`    | Automatización de comandos del proyecto    |

---

## 7. Criterios de Aceptación

- [ ] `make help` muestra todos los targets con descripciones.
- [ ] `make up` levanta PostgreSQL + Metabase sin errores.
- [ ] `make down` detiene servicios correctamente.
- [ ] `make db-shell` abre sesión psql interactiva.
- [ ] `make db-init` ejecuta `init.sql` sin errores.
- [ ] `make deps` instala dependencias Python.
- [ ] `make data-generate` genera datos sintéticos.
- [ ] `make mv-refresh` refresca vistas materializadas.
- [ ] `make setup` ejecuta el flujo completo (deps → up → db-init → data-generate).
- [ ] `make destroy` elimina contenedores y volúmenes.
- [ ] Variables cargadas desde `.env` (no hardcodeadas en Makefile).
- [ ] Todos los targets destructivos tienen advertencia `⚠️`.

---

## 8. Dependencias

- **Requiere:** F0 (Preparación — estructura de carpetas, `.env`).
- **Habilita:** Todos los targets de infraestructura, BD, datos, y testing.

---

## 9. Verificación

```bash
# Ver ayuda
make help

# Setup completo
make setup

# Verificar servicios
make status

# Conectar a BD
make db-shell

# Generar datos
make data-generate

# Contar registros
make data-count

# Refrescar vistas
make mv-refresh

# Limpiar
make clean
```

---

## 10. Notas

- El Makefile **no** reemplaza los scripts individuales (`init.sql`, `generate_data.py`) — los invoca.
- `make destroy` y `make db-reset` son destructivos — confirmar antes de ejecutar.
- El Makefile asume que `docker-compose` está en el PATH (Docker Compose v2 usa `docker compose` sin guión; ajustar si es necesario).
- Para Docker Compose v2, cambiar `DOCKER_COMPOSE = docker-compose` por `DOCKER_COMPOSE = docker compose`.
