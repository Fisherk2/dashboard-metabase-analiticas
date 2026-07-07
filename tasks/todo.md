# TODO — F6: Cierre

**Fecha:** 2026-07-07 | **Estado:** 📋 PLAN APROBADO — Listo para ejecutar
**Referencia:** [plan.md](plan.md)

---

## Slice 1: Document Review (F6-01)

- [ ] **F6-01.1** — Actualizar `docs/PRD.md`: fecha 2026-07-07, estado "Borrador" → "✅ Aprobado v1.0.0", record counts (~182K), version 1.0.0
- [ ] **F6-01.2** — Actualizar `docs/TRD.md`: fecha 2026-07-07, estado "Borrador" → "✅ Aprobado v1.0.0", record counts, version 1.0.0
- [ ] **F6-01.3** — Verificar `docs/AGENTS.md`: confirmar v2.4, todos los links relativos existen
- [ ] **F6-01.4** — Verificar `docs/WORKFLOW.md`: F0-F5 marcado correcto, F6 marcado al cerrar, Gantt actualizado
- [ ] **F6-01.5** — Cross-ref check: USER_GUIDE/TECHNICAL_GUIDE/REPRODUCIBILITY vs PRD/TRD (sin contradicciones en record counts, comandos, nombres de paneles, versiones)
- [ ] **F6-01.6** — Spot-check: ARCHITECTURE/SCHEMA/TESTING/SECURITY/CODE_STYLE/METABASE_SETUP/METABASE_EXPORTS/APPFLOW — links no rotos
- [ ] **F6-01.7** — Validar con `make test` que no hay regresión

## Checkpoint 1: Document Review ✅

- [ ] PRD.md y TRD.md con status Aprobado v1.0.0
- [ ] AGENTS.md y WORKFLOW.md verificados
- [ ] Cross-ref check sin contradicciones
- [ ] Tech docs spot-checked
- [ ] `make test` exit 0
- [ ] `wc -l docs/*.md` documentado

---

## Slice 2: Technical Debt (F6-01.b)

- [ ] **F6-02.1** — Llenar `docs/TECH_DEBT.md` con 4 items reales:
  - TD-001 (Resuelto F5): `make setup` no incluía `create-views`
  - TD-002 (Abierto): Particionamiento requiere migración manual
  - TD-003 (Abierto): Tests runtime con credenciales hardcodeadas
  - TD-004 (Abierto): 9 fallas pre-existentes en test suite runtime
- [ ] **F6-02.2** — Actualizar header de TECH_DEBT.md: fecha, autor, estado
- [ ] **F6-02.3** — Añadir sección "Ítems Cerrados" con TD-001

## Checkpoint 2: Technical Debt ✅

- [ ] TECH_DEBT.md con 3+ items abiertos documentados
- [ ] 1+ item cerrado en v1.0.0 (TD-001)
- [ ] Formato consistente con plantilla (sin placeholders)
- [ ] Header completo

---

## Slice 3: Lessons Learned (F6-02)

- [ ] **F6-03.1** — Crear `docs/LESSONS_LEARNED.md` con 6 secciones (F0-F5) + Cross-Phase Patterns
- [ ] **F6-03.2** — Sintetizar lecciones de WORKFLOW.md v1.0-v1.5, TECHNICAL_GUIDE §10, REPRODUCIBILITY, code review findings
- [ ] **F6-03.3** — Añadir sección "Cross-Phase Patterns" (TDD, slicing vertical, code review multi-eje, source-driven, documentar para portafolio)

## Checkpoint 3: Lessons Learned ✅

- [ ] `docs/LESSONS_LEARNED.md` existe, ≥200 líneas
- [ ] 6 fases cubiertas con 3-5 lecciones cada una
- [ ] Formato: Problema → Solución → Lección
- [ ] Cross-Phase con 5+ patterns

---

## Slice 4: Git Workflow Release v1.0.0 (F6-03)

- [ ] **F6-04.1** — `git checkout develop && git merge --no-ff feat/mvp-dashboard`
- [ ] **F6-04.2** — `git checkout -b release/v1.0.0 develop`
- [ ] **F6-04.3** — Empirical testing (con asistencia del agente):
  - `make down` → `make destroy` → `cp .env.example .env` → `make setup`
  - `make test` → `make test-queries`
  - `make metabase-setup` → `make metabase-pulse-test`
  - Verificar 4 dashboards + 2 pulses en Metabase UI
- [ ] **F6-04.4** — Merge a main + tag v1.0.0 + push:
  - `git checkout main && git merge --no-ff release/v1.0.0`
  - `git tag -a v1.0.0 -m 'Release v1.0.0'`
  - `git push origin main develop --tags`
- [ ] **F6-04.5** — Sync back: `git checkout develop && git merge --no-ff main` + `git push origin develop`
- [ ] **F6-04.6** — Cleanup: `git branch -d release/v1.0.0`
- [ ] **F6-04.7** — Verificación final: `git log`, `git tag -l`, `curl GitHub API`

## Checkpoint 4: Release v1.0.0 ✅

- [ ] Merge a develop exitoso
- [ ] Release branch creada
- [ ] Empirical testing: todos los comandos exit 0
- [ ] Dashboards visibles en Metabase
- [ ] Merge a main exitoso
- [ ] Tag v1.0.0 creado y pusheado
- [ ] Sync back a develop exitoso
- [ ] `git log main..develop` VACÍO
- [ ] Release visible en GitHub

---

## Progreso

- **Total tareas:** 17 (7 + 3 + 3 + 7)
- **Tareas completadas:** 0/17
- **Checkpoints pendientes:** 4/4
- **Tiempo estimado:** 4-6h (~0.5 días)
- **Commits esperados:** 4 atómicos (uno por slice) + posibles hotfix
- **Archivos a modificar:** 4 (PRD, TRD, AGENTS, WORKFLOW)
- **Archivos a crear:** 2 (TECH_DEBT, LESSONS_LEARNED)
- **Remote:** `https://github.com/Fisherk2/dashboard-metabase-analiticas`

---

## Notas

- **Empirical testing** requiere sesión interactiva con el usuario (no se puede automatizar completamente)
- **Tag v1.0.0** solo se crea si T4.3 (empirical testing) pasa sin issues
- **Si empirical test falla**: hotfix en release branch, retest, luego merge
- **Push** asume que el remote `origin` tiene permisos de escritura (verificar con `git push --dry-run`)
