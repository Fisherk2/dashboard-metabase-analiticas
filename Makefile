# Makefile — Dashboard Metabase + Colección Analítica para E-commerce
# Uso: make [target] | make help
# Documentación completa: docs/ y specs/spec-makefile.md

include .env
export

# ─── Variables ───────────────────────────────────────────────
DOCKER_COMPOSE = docker compose
DOCKER_FILE = docker/docker-compose.yml
PSQL = docker exec -i metabase-postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
PYTHON = venv/bin/python
PIP = venv/bin/pip
GENERATOR = docker exec -i metabase-generator

# ─── Default ─────────────────────────────────────────────────
.DEFAULT_GOAL := help

# ─── Help ────────────────────────────────────────────────────
help: ## Mostrar ayuda con todos los comandos disponibles
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ─── Infrastructure ──────────────────────────────────────────
.PHONY: up down restart logs logs-pg logs-mb status validate destroy

up: ## Levantar PostgreSQL + Metabase
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) up -d

down: ## Detener todos los servicios
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) down

restart: down up ## Reiniciar servicios

logs: ## Ver logs de todos los servicios
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) logs -f

logs-pg: ## Ver logs de PostgreSQL
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) logs -f postgres

logs-mb: ## Ver logs de Metabase
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) logs -f metabase

status: ## Estado de los servicios
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) ps

validate: ## Validar docker-compose.yml
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) config

destroy: ## ⚠️ Detener y eliminar volúmenes (pierde datos)
	$(DOCKER_COMPOSE) -f $(DOCKER_FILE) down -v

# ─── Database ────────────────────────────────────────────────
.PHONY: db-shell db-init db-reset db-check

db-shell: ## Conectar a psql interactivo
	docker exec -it metabase-postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-init: ## Ejecutar schema inicial + índices (scripts/init.sql + sql/indexes/create_indexes.sql)
	$(PSQL) < scripts/init.sql
	$(PSQL) < sql/indexes/create_indexes.sql

db-reset: ## ⚠️ Reiniciar BD desde cero (drop + recreate + init + indexes)
	$(PSQL) -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	$(MAKE) db-init

db-check: ## Verificar que PostgreSQL está listo
	docker exec -i metabase-postgres pg_isready -U $(POSTGRES_USER)

# ─── Data Generation ─────────────────────────────────────────
.PHONY: venv deps data-generate data-debug data-count

venv: ## Crear .venv local e instalar dependencias para make test y metabase-setup
	python3 -m venv venv
	venv/bin/python3 -m pip install --quiet -r scripts/requirements.txt

deps: ## Instalar dependencias Python en el contenedor data-generator
	$(GENERATOR) pip install -r /scripts/requirements.txt

data-generate: ## Generar datos sintéticos
	$(GENERATOR) python /scripts/generate_data.py

data-debug: ## Generar datos con logs detallados
	$(GENERATOR) python /scripts/generate_data.py --debug

data-count: ## Contar registros en tablas del proyecto
	@echo "=== Registros por tabla (proyecto) ==="
	$(PSQL) -c "SELECT tabla, total::int FROM (SELECT 'categorias' AS tabla, COUNT(*) AS total FROM categorias UNION ALL SELECT 'proveedores', COUNT(*) FROM proveedores UNION ALL SELECT 'productos', COUNT(*) FROM productos UNION ALL SELECT 'clientes', COUNT(*) FROM clientes UNION ALL SELECT 'tiempo', COUNT(*) FROM tiempo UNION ALL SELECT 'promociones', COUNT(*) FROM promociones UNION ALL SELECT 'ventas', COUNT(*) FROM ventas UNION ALL SELECT 'inventario', COUNT(*) FROM inventario UNION ALL SELECT 'devoluciones', COUNT(*) FROM devoluciones UNION ALL SELECT 'logistica', COUNT(*) FROM logistica) sub ORDER BY tabla;" 2>/dev/null
	@echo "---"
	$(PSQL) -t -A -c "SELECT SUM(total)::text FROM (SELECT COUNT(*) AS total FROM categorias UNION ALL SELECT COUNT(*) FROM proveedores UNION ALL SELECT COUNT(*) FROM productos UNION ALL SELECT COUNT(*) FROM clientes UNION ALL SELECT COUNT(*) FROM tiempo UNION ALL SELECT COUNT(*) FROM promociones UNION ALL SELECT COUNT(*) FROM ventas UNION ALL SELECT COUNT(*) FROM inventario UNION ALL SELECT COUNT(*) FROM devoluciones UNION ALL SELECT COUNT(*) FROM logistica) sub;" 2>/dev/null | sed 's/^/  TOTAL: /'

# ─── SQL Optimization ────────────────────────────────────────
.PHONY: create-views mv-refresh indexes-check

create-views: ## Crear vistas materializadas desde sql/views/*.sql
	@ls sql/views/*.sql >/dev/null 2>&1 || { echo "Error: no SQL files found in sql/views/"; exit 1; }
	@for f in sql/views/*.sql; do \
		echo "  Running: $$f"; \
		$(PSQL) < $$f; \
	done

mv-refresh: ## Refrescar vistas materializadas
	@test -f scripts/refresh_materialized_views.sql || { echo "Error: scripts/refresh_materialized_views.sql not found"; exit 1; }
	$(PSQL) < scripts/refresh_materialized_views.sql

indexes-check: ## Listar todos los índices
	$(PSQL) -c "SELECT indexname, tablename, indexdef FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;"

# ─── Metabase Setup ─────────────────────────────────────────
.PHONY: metabase-setup metabase-export metabase-pulse-test

metabase-setup: ## Configurar Metabase: DB connection + questions + dashboard + pulses via API
	$(PYTHON) scripts/setup_metabase.py --full

metabase-export: ## Exportar colección Metabase a JSON
	$(PYTHON) scripts/setup_metabase.py --export-only

metabase-pulse-test: ## Verificar Pulses via setup script (idempotente)
	$(PYTHON) scripts/setup_metabase.py --pulses

# ─── Testing ─────────────────────────────────────────────────
.PHONY: test test-queries test-integrity test-full

test: ## Ejecutar suite de tests (pytest)
	$(PYTHON) -m pytest tests/ -v

test-queries: ## Validar rendimiento de queries críticas (p95 <2s via measure_query_performance.py)
	@echo "=== Validación de rendimiento: Dashboard Queries ==="
	@docker info >/dev/null 2>&1 || { echo "ERROR: Docker no disponible. Este target requiere Docker."; exit 1; }
	$(GENERATOR) python /scripts/measure_query_performance.py

test-integrity: ## Validar integridad referencial
	@echo "=== Validación de integridad referencial ==="
	$(PSQL) -c "WITH fk_check AS (SELECT COUNT(*) AS orphan_count FROM ventas v LEFT JOIN productos p ON v.producto_id = p.id WHERE p.id IS NULL) SELECT CASE WHEN orphan_count = 0 THEN 'OK' ELSE 'PROBLEMA: ' || orphan_count || ' huérfanos' END AS integridad_ventas FROM fk_check;"
	$(PSQL) -c "WITH fk_check AS (SELECT COUNT(*) AS orphan_count FROM inventario i LEFT JOIN productos p ON i.producto_id = p.id WHERE p.id IS NULL) SELECT CASE WHEN orphan_count = 0 THEN 'OK' ELSE 'PROBLEMA: ' || orphan_count || ' huérfanos' END AS integridad_inventario FROM fk_check;"

test-full: test-queries test-integrity ## Ejecutar todas las validaciones

# ─── Utilities ───────────────────────────────────────────────
.PHONY: setup clean venv

setup: venv up deps db-init data-generate create-views mv-refresh ## 🚀 Setup completo: venv → up → deps → db-init → data-generate → MVs

clean: ## Limpiar archivos temporales
	@echo "Limpiando __pycache__, *.pyc, *.pyo, .pytest_cache..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	@echo "Limpieza completada."
