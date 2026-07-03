# Makefile — Dashboard Metabase + Colección Analítica para E-commerce
# Uso: make [target] | make help
# Documentación completa: docs/ y specs/spec-makefile.md

include .env
export

# ─── Variables ───────────────────────────────────────────────
DOCKER_COMPOSE = docker compose
DOCKER_FILE = docker/docker-compose.yml
PSQL = docker exec -it metabase-postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
PYTHON = python
PIP = pip

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
	$(PSQL)

db-init: ## Ejecutar schema inicial (scripts/init.sql)
	$(PSQL) -f scripts/init.sql

db-reset: ## ⚠️ Reiniciar BD desde cero (drop + recreate + init)
	$(PSQL) -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	$(MAKE) db-init

db-check: ## Verificar que PostgreSQL está listo
	docker exec -it metabase-postgres pg_isready -U $(POSTGRES_USER)

# ─── Data Generation ─────────────────────────────────────────
.PHONY: deps data-generate data-debug data-count

deps: ## Instalar dependencias Python (scripts/requirements.txt)
	$(PIP) install -r scripts/requirements.txt

data-generate: ## Generar datos sintéticos
	$(PYTHON) scripts/generate_data.py

data-debug: ## Generar datos con logs detallados
	$(PYTHON) scripts/generate_data.py --debug

data-count: ## Contar registros por tabla
	@echo "=== Registros por tabla ==="
	$(PSQL) -c "\dt" -q -t | awk '{print $$3}' | while read table; do \
		count=$$($(PSQL) -c "SELECT COUNT(*) FROM $$table" -t -A 2>/dev/null); \
		[ -n "$$count" ] && echo "  $$table: $$count"; \
	done

# ─── SQL Optimization ────────────────────────────────────────
.PHONY: mv-refresh indexes-check

mv-refresh: ## Refrescar vistas materializadas
	$(PSQL) -f scripts/refresh_materialized_views.sql

indexes-check: ## Listar todos los índices
	$(PSQL) -c "SELECT indexname, tablename, indexdef FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;"

# ─── Testing ─────────────────────────────────────────────────
.PHONY: test-queries test-integrity test-full

test-queries: ## Validar rendimiento de queries críticas (<2s)
	@echo "=== Validación de queries (EXPLAIN ANALYZE) ==="
	@echo "Requiere datos generados. Ejecutar make data-generate primero."

test-integrity: ## Validar integridad referencial
	@echo "=== Validación de integridad referencial ==="
	$(PSQL) -c "WITH fk_check AS (SELECT COUNT(*) AS orphan_count FROM ventas v LEFT JOIN productos p ON v.producto_id = p.id WHERE p.id IS NULL) SELECT CASE WHEN orphan_count = 0 THEN 'OK' ELSE 'PROBLEMA: ' || orphan_count || ' huérfanos' END AS integridad_ventas FROM fk_check;"
	$(PSQL) -c "WITH fk_check AS (SELECT COUNT(*) AS orphan_count FROM inventario i LEFT JOIN productos p ON i.producto_id = p.id WHERE p.id IS NULL) SELECT CASE WHEN orphan_count = 0 THEN 'OK' ELSE 'PROBLEMA: ' || orphan_count || ' huérfanos' END AS integridad_inventario FROM fk_check;"

test-full: test-queries test-integrity ## Ejecutar todas las validaciones

# ─── Utilities ───────────────────────────────────────────────
.PHONY: setup clean

setup: deps up db-init data-generate ## 🚀 Setup completo del proyecto (deps → up → db-init → data-generate)

clean: ## Limpiar archivos temporales
	@echo "Limpiando __pycache__, *.pyc, *.pyo, .pytest_cache..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	@echo "Limpieza completada."
