# Dashboard Metabase + Colección Analítica para E-commerce

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Metabase](https://img.shields.io/badge/Metabase-OSS-509EE3?logo=metabase&logoColor=white)](https://www.metabase.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GNU Make](https://img.shields.io/badge/Make-4.0+-A81D33?logo=gnu&logoColor=white)](https://www.gnu.org/software/make/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Panel visual conectado a PostgreSQL que muestra KPIs de inventario, rotación y alertas de stock mínimo para un e-commerce simulado. Proyecto de portafolio que demuestra diseño de schema estrella para OLAP, optimización de queries SQL, integración con Metabase como herramienta BI, y generación de datos sintéticos.

## Quick Start

```bash
# 1. Clonar y configurar
cp .env.example .env
make setup          # Instala deps + levanta servicios + inicializa BD + genera datos
```

Esto levanta PostgreSQL 15+ y Metabase, crea el schema estrella, genera datos sintéticos y deja los servicios listos para explorar.

## Demo

Los dashboards están disponibles en `http://localhost:3000` después de ejecutar `make setup`.

| Dashboard | Descripción |
|-----------|-------------|
| **Rotación por Categoría** | Productos más vendidos y rotación mensual |
| **Stock Actual vs. Mínimo** | Alertas de stock bajo y niveles actuales |
| **Top 10 Ventas** | Productos con mayores ingresos |

## Tech Stack

| Categoría | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Base de datos** | PostgreSQL 15+ | Schema estrella, vistas materializadas, particionamiento |
| **BI / Visualización** | Metabase OSS | Dashboards, queries ad-hoc, exportación PNG/CSV |
| **Orquestación** | Docker Compose | Servicios reproducibles PostgreSQL + Metabase |
| **Generación de datos** | Python + Faker | Datos sintéticos realistas (100K ventas, 5K productos) |
| **Automatización** | GNU Make | Interfaz unificada (`make up`, `make db-init`, `make data-generate`) |

## Estructura del Proyecto

```
├── docker/                   # Docker Compose para PostgreSQL + Metabase
├── sql/                      # SQL: vistas materializadas, índices, particiones
│   ├── views/
│   ├── indexes/
│   └── partitions/
├── scripts/                  # Generación de datos e init SQL
├── metabase/                 # Exportaciones de dashboards (opcional)
├── specs/                    # Especificaciones por feature
│   ├── adr/                  # Architecture Decision Records
│   ├── spec-star-schema.md
│   ├── spec-data-generation.md
│   └── ...
├── docs/                     # Documentación completa
│   ├── ARCHITECTURE.md       # Diagramas y patrones
│   ├── SCHEMA.md             # Diseño del schema estrella
│   ├── TESTING.md            # Estrategia de pruebas
│   └── ...
├── Makefile                  # Automatización de tareas
└── SPEC.md                   # Especificación central
```

## Documentación

| Recurso | Descripción |
|---------|-------------|
| [SPEC.md](SPEC.md) | Especificación central — objetivos, comandos, criterios de éxito |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitectura, patrones, diagramas Mermaid |
| [docs/SCHEMA.md](docs/SCHEMA.md) | Schema estrella — tablas, relaciones, queries de ejemplo |
| [docs/TESTING.md](docs/TESTING.md) | Estrategia de testing (unidad, integración, rendimiento) |
| [docs/WORKFLOW.md](docs/WORKFLOW.md) | Plan de implementación por fases (F0–F6) |

## Lo Que Aprendí

- Diseño de **schema estrella** para cargas OLAP: tablas de hechos vs. dimensiones, surrogate keys, granularidad.
- Optimización de queries con **vistas materializadas**, índices compuestos y particionamiento por rango de fechas.
- Integración de **Metabase** con PostgreSQL vía JDBC: conexión, consultas nativas, filtros y exportación.
- Generación de datos sintéticos con **Python + Faker** respetando reglas de negocio (distribución de ventas, rotación de inventario).
- Automatización del flujo completo con **Docker Compose + Makefile** para reproducibilidad.

## Licencia

MIT — ver [LICENSE](LICENSE) para detalles.
