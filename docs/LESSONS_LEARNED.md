# Lecciones Aprendidas — Dashboard Metabase + Colección Analítica v1.0.0

**Fecha:** 2026-07-07 | **Autor:** Fisherk2 | **Fases:** F0–F6 (Preparación → Cierre)
**Propósito:** Síntesis de decisiones de diseño, desafíos enfrentados y lecciones aprendidas en cada fase del proyecto.

---

## 1. F0: Preparación — La Base del Proyecto

### 1.1 Estructura de carpetas: documentar antes de codificar

**Problema:** Al iniciar el proyecto, no había claridad sobre dónde colocar los archivos de configuración (`docker-compose.yml`, scripts SQL, documentación). Esto causaba dispersión y archivos huérfanos en la raíz.

**Solución:** Definir la estructura de carpetas completa en SPEC.md y AGENTS.md antes de escribir cualquier línea de código. Usar `.gitkeep` para versionar directorios vacíos como `sql/views/`, `sql/indexes/`, `sql/partitions/`.

**Lección:** La estructura del repositorio es arquitectura. Decidirla al inicio evita refactors dolorosos de rutas relativas y links rotos en documentación.

### 1.2 Test suite estático como red de seguridad

**Problema:** Sin tests automatizados, cualquier cambio en documentación o estructura podía romper enlaces o introducir inconsistencias sin ser detectado.

**Solución:** Crear `tests/test_f0.py` con 73 tests que validan estructura de directorios, contenido de Makefile, patrones de `.gitignore`, y seguridad (secrets en commits). Estos tests se ejecutan en segundos sin necesidad de Docker.

**Lección:** Un test suite estático (sin dependencias externas) es la red de seguridad más rentable para un proyecto de documentación. Se ejecuta en CI y en local sin esfuerzo.

### 1.3 Makefile como interfaz unificada

**Problema:** Sin automatización, cada tarea (levantar servicios, inicializar BD, generar datos) requería recordar comandos ad-hoc.

**Solución:** Implementar un Makefile con 25+ targets, secciones comentadas, y `.DEFAULT_GOAL := help` para auto-documentación. Todos los comandos del proyecto son accesibles via `make <target>`.

**Lección:** Un Makefile bien diseñado es la mejor documentación ejecutable. Cada target es un "ritual" que puede ejecutarse sin pensar.

---

## 2. F1: Infraestructura — Docker y Servicios

### 2.1 Named volumes sobre bind mounts

**Problema:** Usar bind mounts para persistencia de PostgreSQL causaba problemas de permisos en diferentes sistemas operativos (`pg_data` con dueño incorrecto).

**Solución:** Migrar a named volumes de Docker (`postgres_data`), que Docker gestiona automáticamente sin problemas de permisos.

**Lección:** Named volumes son más portables y seguros que bind mounts para datos de base de datos. Bind mounts quedan para configuración y código.

### 2.2 Healthchecks para orden de inicio

**Problema:** Metabase se iniciaba antes de que PostgreSQL estuviera listo, causando errores de conexión en el primer intento.

**Solución:** Implementar healthchecks en ambos servicios (`pg_isready` para PostgreSQL, endpoint `/api/health` para Metabase) y usar `depends_on` con `condition: service_healthy` en docker-compose.yml.

**Lección:** `depends_on` sin healthchecks es una ilusión de orden. Los healthchecks garantizan que un servicio realmente está listo antes de que sus dependientes intenten conectar.

### 2.3 Tests runtime vs. tests estáticos

**Problema:** Los tests que requieren Docker en ejecución son lentos, frágiles y no se pueden ejecutar en CI sin Docker.

**Solución:** Separar tests en dos categorías: estáticos (sin Docker, se ejecutan siempre) y runtime (con Docker, marcados con `@pytest.mark.runtime`). Los tests estáticos se ejecutan por defecto en `make test`.

**Lección:** No todos los tests deben ejecutarse todo el tiempo. La división estático/runtime permite feedback rápido (segundos) en desarrollo y validación profunda (minutos) en CI.

---

## 3. F2: Núcleo — Schema, Datos y Optimización

### 3.1 Star schema con constraints explícitos

**Problema:** Sin constraints CHECK y NOT NULL, los datos sintéticos podían generar registros inconsistentes (fechas futuras, cantidades negativas, precios cero).

**Solución:** Definir constraints CHECK en todas las columnas críticas (e.g., `cantidad > 0`, `precio >= 0`, `fecha_venta <= CURRENT_DATE`). Usar `SERIAL PRIMARY KEY` en todas las tablas de dimensiones.

**Lección:** Las constraints no son solo para producción — son documentación ejecutable de las reglas de negocio. En proyectos con datos sintéticos, evitan que los generadores produzcan datos inválidos.

### 3.2 Distribución Pareto para datos realistas

**Problema:** Datos generados con distribución uniforme no reflejaban patrones reales de e-commerce (pocos productos concentran la mayoría de ventas).

**Solución:** Implementar distribución Pareto (80/20) en el generador de ventas: 80% de las ventas provienen del 20% de los productos. Usar `numpy.random.pareto` o el módulo `random` de Python con pesos sesgados.

**Lección:** Datos sintéticos con distribución uniforme no validan el rendimiento real del sistema. Las distribuciones sesgadas (Pareto, Zipf) producen datos más realistas y exponen problemas de indexación y caching.

### 3.3 Particionamiento: DROP + RECREATE en desarrollo

**Problema:** La tabla `ventas` con ~100K registros comenzaba a mostrar tiempos de scan secuencial en consultas por rango de fechas.

**Solución:** Implementar particionamiento por rango de fechas (12 particiones mensuales) usando `PARTITION BY RANGE (fecha_venta)`. En desarrollo sintético, se aplicó con DROP + RECREATE + CASCADE por simplicidad.

**Lección:** El particionamiento mejora significativamente el pruning en queries con filtros de fecha. Sin embargo, la migración desde una tabla no particionada requiere planificación cuidadosa en producción. Documentado como TD-002.

### 3.4 Vistas materializadas como capa de KPIs

**Problema:** Las queries de agregación (rotación mensual, stock actual, top productos) recalculaban los mismos resultados cada vez, consumiendo recursos innecesarios.

**Solución:** Crear 3 vistas materializadas (`mv_rotacion_mensual`, `mv_stock_actual`, `mv_top_productos`) con refresco manual via `REFRESH MATERIALIZED VIEW`.

**Lección:** Las vistas materializadas son el equivalente funcional de una capa de caching en base de datos. Para dashboards con datos que cambian diariamente (no en tiempo real), son la solución óptima.

---

## 4. F3: Interfaces — Metabase y Dashboards

### 4.1 Setup programático via REST API

**Problema:** Configurar Metabase manualmente (crear conexión, paneles, pulses) no era reproducible y requería documentar clicks exactos en la UI.

**Solución:** Implementar `scripts/setup_metabase.py` con una clase `MetabaseSetup` que usa la REST API de Metabase para: autenticar, crear conexión PostgreSQL, crear preguntas SQL, organizar dashboards y configurar pulses.

**Lección:** La API de Metabase es completa pero tiene edge cases (setup token inicial, parámetros de dashboard no documentados). Source-driven development (consultar la documentación oficial) fue esencial para evitar asumir endpoints incorrectos.

### 4.2 Source-driven development para API desconocida

**Problema:** El equipo no conocía la API de Metabase en detalle y existía el riesgo de implementar contra endpoints incorrectos o desactualizados.

**Solución:** Adoptar source-driven development: cada llamada API se basó en la documentación oficial de Metabase, no en memoria o ejemplos de terceros. Cuando la documentación era ambigua, se realizaban pruebas exploratorias contra la API real.

**Lección:** Source-driven development previene errores costosos. Para APIs con documentación oficial, es más rápido consultar la fuente que debuggear patrones incorrectos asumidos de memoria.

### 4.3 Code review multi-eje para calidad

**Problema:** El código de setup_metabase.py tenía 200+ líneas con lógica de API, manejo de errores y configuración. Una revisión superficial podía dejar bugs.

**Solución:** Implementar code review multi-eje (cortesía de @tezcatlipoca) que evalúa: estructura, errores, mantenibilidad, performance, seguridad, y documentación. Esto descubrió 24 observaciones, incluyendo 2 críticas.

**Lección:** El code review multi-eje es más efectivo que revisiones tradicionales porque fuerza al revisor a evaluar dimensiones específicas en lugar de hacer una lectura superficial.

---

## 5. F4: Pruebas — Validación y Rendimiento

### 5.1 Medir rendimiento dentro del contenedor

**Problema:** Ejecutar `EXPLAIN ANALYZE` desde el host fallaba porque PostgreSQL no exponía el puerto 5432 (por seguridad, solo accesible desde la red interna de Docker).

**Solución:** Ejecutar scripts de medición dentro del contenedor PostgreSQL usando `docker exec -i postgres psql ...` en lugar de conexiones externas. El target `make test-queries` usa el contenedor generator para ejecutar `measure_query_performance.py` desde dentro de la red de Docker.

**Lección:** La seguridad (no exponer puertos) tiene costo en conveniencia de depuración. La solución es ejecutar herramientas de diagnóstico dentro de la red de Docker, no exponer servicios.

### 5.2 Pruebas de persistencia con roundtrip destructivo

**Problema:** No había garantía de que los datos sobrevivieran un ciclo completo de destroy → setup en Docker.

**Solución:** Implementar `scripts/test_persistence.sh` que ejecuta el flujo completo: `make destroy` (borra volúmenes) → `cp .env.example .env` → `make setup` → `make metabase-setup` → verifica datos y dashboards.

**Lección:** La prueba de persistencia más realista es el roundtrip completo desde un estado limpio. Es destructiva (borra datos) pero es la única forma de garantizar reproducibilidad.

### 5.3 Manejo de errores en fallo de PostgreSQL

**Problema:** Cuando PostgreSQL fallaba, Metabase mostraba errores genéricos sin indicar si el problema era de conexión, query, o disponibilidad.

**Solución:** Implementar `scripts/test_error_handling.py` con 5 tests que validan: healthcheck, stop, error detection, restart, y recovery. Configurar Metabase para mostrar errores claros sin stack traces.

**Lección:** Las pruebas de manejo de errores son tan importantes como las pruebas de funcionalidad. Un sistema que falla elegantemente es más confiable que uno que funciona pero falla sin diagnóstico.

---

## 6. F5: Despliegue — Documentación y Portafolio

### 6.1 Documentar para portafolio requiere contenido autocontenido

**Problema:** Las guías de usuario y técnicas iniciales asumían que el lector tenía el proyecto funcionando, con referencias a "vea el panel en Metabase" sin contexto suficiente.

**Solución:** Reescribir README.md (280 líneas, 17 secciones), USER_GUIDE.md (298 líneas) y TECHNICAL_GUIDE.md (445 líneas) como documentos autocontenidos. Cada guía explica el qué, el por qué y el cómo sin depender de otras fuentes.

**Lección:** La documentación para portafolio debe ser autocontenida. Un reclutador o cliente potencial debe entender el proyecto completo sin necesidad de ejecutarlo. Los diagramas Mermaid y tablas reemplazan a las capturas de pantalla.

### 6.2 Reproducibilidad: make setup como único comando

**Problema:** El setup requería múltiples comandos en orden específico (`make up`, `make db-init`, `make data-generate`, `make create-views`, `make mv-refresh`). Esto era frágil y fácil de omitir pasos.

**Solución:** Unificar todo en `make setup` que ejecuta la secuencia completa: `deps up db-init data-generate create-views mv-refresh`. Añadir fail-fast guard para que cada paso falle si el anterior no tuvo éxito.

**Lección:** El setup de un proyecto debe ser un solo comando. Si requiere más de un comando, la gente omitirá pasos y reportará bugs que en realidad son errores de setup. `make setup` con fail-fast guard es la interfaz mínima viable.

### 6.3 Error aritmético propagado en documentación

**Problema:** El WORKFLOW.md reportaba "155K registros" debido a un error aritmético al sumar los registros de cada tabla. Este error se propagó a README.md, USER_GUIDE.md y TECHNICAL_GUIDE.md.

**Solución:** Corregir el cálculo a 182,465 registros totales (100K ventas + 50K inventario + 5K devoluciones + 2K productos + 365 tiempo + 30 categorías + 20K logística + 5K promociones + 50 proveedores + 2,000 clientes). Actualizar los 4 documentos afectados.

**Lección:** Los números en documentación técnica deben verificarse con `SELECT COUNT(*)` en la base de datos, no calcularse a mano. Un error aritmético simple se propaga a través de todo el proyecto si no se valida contra la fuente de verdad.

---

## 7. F6: Cierre — Code Review y Release

### 7.1 Code review multi-eje descubre bugs en código ya revisado

**Problema:** El código de F0–F5 ya había pasado por code review multi-eje en sus respectivas fases. Sin embargo, una revisión final multi-eje en F6 descubrió 18 hallazgos adicionales (3 críticos, 8 importantes, 7 sugerencias) en código que se consideraba "revisado".

**Solución:** Ejecutar code review multi-eje completo (cortesía de @tezcatlipoca) sobre todos los archivos modificados en F6, más generate_data.py, init.sql, setup_metabase.py, y las queries SQL. 17 archivos modificados, +127/-59 líneas. Commit `53f97cb`.

**Lección:** El code review multi-eje debe aplicarse en cada fase, pero también al final como gate de calidad. Bugs que sobreviven a revisiones individuales son detectados por una revisión final que examina las interacciones entre módulos.

### 7.2 Documentación cross-phase requiere verificación contra fuente de verdad

**Problema:** Al actualizar la documentación en F6, se descubrieron inconsistencias propagadas desde fases anteriores: el tipo de `anio` era `VARCHAR(4)` en unos archivos e `INT` en otros; el umbral de stock mínimo era `*1.2` en la MV pero `*1.1` en la documentación; el conteo de registros decía "20 clientes" en lugar de "2,000 clientes".

**Solución:** Para cada cambio documentado, verificar contra la fuente de verdad (schema SQL, queries de base de datos, no contra otra documentación). Usar tests estáticos (`test_f0.py`) como red de seguridad para detectar inconsistencias cross-file.

**Lección:** La documentación se degrada más rápido que el código porque no tiene tests. Los tests estáticos que verifican consistencia cross-file (tipos de columnas, nombres, valores) son la única defensa contra documentación incorrecta.

### 7.3 Tests estáticos como red de seguridad para refactors de documentación

**Problema:** Al modificar 17 archivos de documentación y código en F6, existía el riesgo de romper enlaces, introducir inconsistencias de tipos, o desincronizar la especificación con la implementación.

**Solución:** Ejecutar `make test` después de cada cambio significativo. Los 274 tests estáticos validan: estructura de directorios, existencia de archivos referenciados, formato de documentación, seguridad (secrets), y consistencia de tipos. 0 regresiones en los 275 tests estáticos tras los 18 fixes.

**Lección:** Un test suite estático de documentación es la red de seguridad más rentable. Cada test es una assertion sobre el estado del proyecto que se verifica en segundos sin dependencias externas.

### 7.4 Git Workflow Release requiere intervención manual

**Problema:** El proceso de release (merge feat → develop → release branch → empirical testing → main + tag) no puede automatizarse completamente porque incluye pasos que requieren confirmación humana (merge approval, verificación empírica de dashboards).

**Solución:** Documentar el proceso de release en los tests (`test_f6.py::TestGitWorkflow`) como 8 tests que validan cada paso del workflow. Los tests pasan de RED a GREEN a medida que se completa cada paso manual. Esto proporciona visibilidad del progreso sin forzar automatización donde no es apropiada.

**Lección:** No todo debe automatizarse. Los tests son mejor herramienta que los scripts para guiar procesos manuales porque documentan el estado actual y verifican cada paso sin ejecutarlo automáticamente.

---

## 8. Patrones Cross-Phase

Los siguientes patrones emergieron en múltiples fases y son aplicables a futuros proyectos:

### 8.1 TDD como disciplina de diseño, no solo de testing

El ciclo RED-GREEN-REFACTOR no es solo para código — se aplica igualmente a documentación y configuración. En F6, escribir tests primero para PRD.md y TRD.md (RED) forzó a definir criterios de aceptación concretos antes de modificar los documentos. Los tests son la especificación ejecutable del estado final deseado.

**Aplicación futura:** Para cualquier cambio en documentación, escribir primero el test que valida el estado deseado.

### 8.2 Slicing vertical con checkpoints de calidad

Cada fase se dividió en 4 slices verticales con checkpoints intermedios. Esto permitió tener "done" parcial verificable después de cada slice, en lugar de esperar al final de la fase para validar. El patrón se repitió en F0-F6 con resultados consistentes.

**Aplicación futura:** Para proyectos nuevos, planificar slices verticales de 1-2 horas con checkpoints explícitos. No avanzar al siguiente slice sin pasar el checkpoint actual.

### 8.3 Code review multi-eje

Desarrollado en F3 por @tezcatlipoca, este patrón de revisión evalúa el código en 6 dimensiones: estructura, errores, mantenibilidad, performance, seguridad y documentación. Se aplicó en F3, F4 y F5, descubriendo un total de 41 observaciones (incluyendo 4 críticas).

**Aplicación futura:** Incorporar code review multi-eje como gate obligatorio antes de mergear cualquier cambio significativo a main.

### 8.4 Source-driven development para APIs externas

Cada interacción con APIs externas (Metabase REST API, Docker API) se fundamentó en documentación oficial, no en memoria o tutoriales de terceros. Este patrón evitó errores por APIs deprecadas o endpoints incorrectos.

**Aplicación futura:** Para cualquier integración con sistema externo, consultar la documentación oficial de la versión específica antes de implementar. Documentar la fuente con URL completa en comentarios de código.

### 8.5 Documentar para portafolio desde el día uno

El proyecto se documentó desde F0 con AGENTS.md y SPEC.md, no al final. Esto permitió que la documentación evolucionara con el código, en lugar de ser un esfuerzo masivo de post-producción. El resultado es documentación coherente y actualizada.

**Aplicación futura:** Iniciar todo proyecto con un ARCHITECTURE.md y un README.md, aunque sean borradores. La documentación incremental requiere menos esfuerzo total que la documentación al final.

### 8.6 Makefile como documento ejecutable

El Makefile unificó todos los workflows del proyecto en una interfaz coherente. Cada target documenta su propósito via comentario `##` y su implementación concreta. `make help` lista todo el proyecto. Este patrón eliminó la necesidad de recordar comandos ad-hoc.

**Aplicación futura:** Para cualquier proyecto con múltiples pasos, crear un Makefile (o Taskfile, Justfile) desde el día uno. La automatización temprana previene errores humanos y documenta el flujo de trabajo.

---

## 9. Conclusión

El proyecto demostró que un dashboard analítico funcional y reproducible puede construirse con tecnologías open-source (PostgreSQL + Metabase + Docker + Python) siguiendo patrones de ingeniería profesional (TDD, slicing vertical, code review multi-eje, source-driven development).

La principal lección es que la **calidad del proceso** (cómo se construye) determina la **calidad del producto** (qué se entrega). Invertir en tests desde F0, documentar incrementalmente, y revisar el código multi-dimensionalmente produjo un proyecto que es funcional (182K registros, 4 dashboards, <2ms p95), documentado (16+ documentos, 2000+ líneas), y reproducible (make setup → make test).

**Próximos pasos recomendados:**
- Resolver TD-002 (particionamiento con migración en caliente)
- Resolver TD-003 (tests runtime con credenciales configurables)
- Resolver TD-004 (separar tests runtime con marcador)
- Explorar integración con herramientas de CI/CD (GitHub Actions)

---

*Última actualización: 2026-07-07*
