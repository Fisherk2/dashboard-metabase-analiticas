# TODO — F5: Despliegue

**Fecha:** 2026-07-07 | **Estado:** 📋 PLAN APROBADO — Listo para ejecutar
**Referencia:** [plan.md](plan.md)

---

## Slice 1: README Premium (F5-01)

- [ ] **F5-01.1** — Reestructurar `README.md`: añadir secciones (Descripción, Features, Demo, Tech Stack, Architecture, Quick Start, Installation, Usage, Documentation, Project Structure, Development, Testing, Performance, Security, License, Contributing). Mantener badges.
- [ ] **F5-01.2** — Añadir diagrama Mermaid de arquitectura (services + flujo) en README.
- [ ] **F5-01.3** — Añadir tabla de "What You'll Learn" (skills demostradas).
- [ ] **F5-01.4** — Validar `python -m pytest tests/test_f0.py` que los tests de README siguen pasando.

## Checkpoint 1: README Premium ✅

- [ ] README ≥200 líneas con todas las secciones
- [ ] Diagrama Mermaid renderizable
- [ ] `make test` exit 0 (sin regresión F0)
- [ ] Tiempo de lectura: ~2 min

---

## Slice 2: User Guide (F5-02)

- [ ] **F5-02.1** — Crear `docs/USER_GUIDE.md` con secciones: Prerequisites, Setup, Acceder a Metabase, Tour del Dashboard (4 paneles), Exportar datos, Troubleshooting, FAQ.
- [ ] **F5-02.2** — Para cada panel documentar: nombre, pregunta, fuente (MV/tabla), interpretación de estados.

## Checkpoint 2: User Guide ✅

- [ ] `docs/USER_GUIDE.md` ≥150 líneas
- [ ] 4 paneles con interpretación completa
- [ ] Top 3 issues en Troubleshooting
- [ ] Link a METABASE_EXPORTS.md

---

## Slice 3: Technical Guide (F5-03)

- [ ] **F5-03.1** — Crear `docs/TECHNICAL_GUIDE.md` con secciones: Architecture Overview, Star Schema, Materialized Views, Query Optimization, Partitioning, Metabase, Testing, Performance, Reproducibility.
- [ ] **F5-03.2** — Añadir sección "Lessons Learned" (5+ decisiones documentadas).
- [ ] **F5-03.3** — Añadir diagrama Mermaid de flujos de datos (PG → MVs → Metabase → User).

## Checkpoint 3: Technical Guide ✅

- [ ] `docs/TECHNICAL_GUIDE.md` ≥300 líneas
- [ ] Cubre las 9 secciones listadas
- [ ] 5+ lecciones aprendidas
- [ ] Diagrama de flujos presente

---

## Slice 4: Reproducibilidad (F5-05)

- [ ] **F5-04.1** — Clonar repo en `/tmp/f5-repro-test/`. Ejecutar `make setup` desde cero. Verificar exit 0.
- [ ] **F5-04.2** — Ejecutar `make test` y `make test-queries` en directorio nuevo. Verificar exit 0.
- [ ] **F5-04.3** — Ejecutar `ALLOW_DESTRUCTIVE=1 ./scripts/test_persistence.sh` en directorio nuevo. Verificar exit 0.
- [ ] **F5-04.4** — Documentar resultados en `docs/REPRODUCIBILITY.md` (entorno, comandos, tiempo, resultados).

## Checkpoint 4: Reproducibilidad Validada ✅

- [ ] `make setup` exit 0 en directorio nuevo
- [ ] `make test` y `make test-queries` exit 0
- [ ] Roundtrip completo exit 0
- [ ] `docs/REPRODUCIBILITY.md` ≥50 líneas

---

## Progreso

- **Total tareas:** 13 (4 + 2 + 3 + 4)
- **Tareas completadas:** 0/13
- **Checkpoints pendientes:** 4/4
- **Tiempo estimado:** 8-10h (~1 día)
- **Commits esperados:** 5-7 atómicos
- **Documentación a crear:** 3 archivos (USER_GUIDE, TECHNICAL_GUIDE, REPRODUCIBILITY)
- **Documentación a expandir:** 1 archivo (README.md)

---

## Notas

- **F5-04 (video tutorial)** descartado por decisión del usuario
- **Screenshots** descartados — solo texto + diagramas Mermaid
- **Reproducibilidad** en mismo host/máquina (clonar repo en otra carpeta)
