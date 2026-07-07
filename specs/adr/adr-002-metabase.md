# ADR-002: Metabase OSS como Herramienta BI

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Estado:** Aceptado

---

## Decisión

Usar **Metabase Open Source (OSS)** como herramienta de visualización BI para el dashboard de e-commerce.

---

## Contexto

El proyecto requiere una herramienta de visualización que:

- Se conecte directamente a PostgreSQL mediante JDBC
- Permita crear paneles con queries SQL personalizadas
- Soporte filtros dinámicos (año, mes, categoría, proveedor)
- Permita exportación a PNG y CSV
- Sea fácil de configurar y reproducir con Docker
- No requiera licencias costosas (proyecto de portafolio)

---

## Alternativas Consideradas

### Tableau

**Ventajas:**
- Líder del mercado en BI
- Visualizaciones muy pulidas y profesionales
- Soporte para fuentes de datos diversas

**Desventajas:**
- Licencia costosa (~$70/mes por usuario para Tableau Creator)
- No es open-source
- Requiere instalación de Tableau Server o uso de Tableau Public (limitado)
- Overkill para un proyecto de portafolio con datos sintéticos
- No se puede levantar con Docker de forma sencilla

**Conclusión:** Descartado por costo y complejidad innecesaria para el alcance del proyecto.

---

### Power BI

**Ventajas:**
- Integración con ecosistema Microsoft
- Visualizaciones interactivas robustas
- Amplia adopción empresarial

**Desventajas:**
- Requiere licencia Power BI Pro (~$10/mes) para compartir dashboards
- No es open-source
- No soporta Docker (requiere Power BI Desktop o Service)
- Dependencia de plataforma Windows (Desktop) o Microsoft Cloud (Service)
- Conexión a PostgreSQL requiere gateway adicional

**Conclusión:** Descartado por dependencia de plataforma propietaria y costos de licencia.

---

### Grafana

**Ventajas:**
- Open-source y gratuito
- Soporte para Docker
- Excelente para métricas en tiempo real

**Desventajas:**
- Orientado a series temporales y monitoreo (no OLAP)
- SQL editor menos intuitivo que Metabase
- No soporta exportación a PNG de dashboards completos (solo paneles individuales)
- Configuración de paneles analíticos menos natural que Metabase
- Mejor para infraestructura/DevOps que para BI de negocio

**Conclusión:** Descartado por enfoque en monitoreo en lugar de análisis de negocio.

---

## Razones para Elegir Metabase

1. **Open-source y gratuito:** Sin costos de licencia, ideal para portafolio.
2. **Conexión JDBC directa a PostgreSQL:** Configuración sencilla sin gateways adicionales.
3. **SQL editor integrado:** Permite escribir queries SQL personalizadas con variables de filtro.
4. **Dashboards interactivos:** Filtros dinámicos, drill-down, y visualizaciones variadas.
5. **Exportación a PNG/CSV:** Funcionalidad nativa para todos los paneles.
6. **Docker support:** Imagen oficial `metabase/metabase:latest` para reproducibilidad.
7. **Curva de aprendizaje baja:** Interfaz intuitiva, no requiere conocimiento avanzado de BI.
8. **Preguntas guardadas:** Permite guardar queries SQL como "preguntas" reutilizables.
9. **Colecciones:** Organización de dashboards en colecciones (útil para portafolio).

---

## Consecuencias

### Positivas
- Configuración rápida con Docker Compose (Metabase + PostgreSQL).
- Sin costos de licencia — todo el stack es open-source.
- Exportación nativa a PNG/CSV para documentación de portafolio.
- SQL editor permite demostrar habilidades de SQL analítico.
- Comunidad activa y documentación extensa.

### Negativas
- Versión OSS no soporta SSO/OAuth (solo autenticación básica).
- No soporta deep linking a paneles específicos (limitación conocida).
- Alertas automáticas (Pulse) requieren configuración de email/Slack adicional.
- Rendimiento depende de la optimización de queries en PostgreSQL.

### Neutrales
- Metabase usa su propia base de datos interna (H2 por defecto) para configuración.
- La versión OSS es suficiente para el alcance del proyecto (3+ paneles, filtros, exportación).

---

## Validación

```bash
# Levantar Metabase con Docker
docker-compose up -d metabase

# Acceder a Metabase
open http://localhost:3000

# Configurar conexión a PostgreSQL
# Admin → Databases → Add database → PostgreSQL
# Host: postgres, Port: 5432, Database: ecommerce
# User: admin, Password: ${POSTGRES_PASSWORD}

# Crear panel con query SQL
# Questions → New → SQL Query
SELECT * FROM mv_rotacion_mensual LIMIT 10;

# Exportar panel
# ⋮ → Export to PNG / Export to CSV
```

---

## Referencias

- [Metabase Documentation](https://www.metabase.com/docs/latest/)
- [Metabase Docker Image](https://hub.docker.com/r/metabase/metabase)
- [Metabase SQL Variables](https://www.metabase.com/docs/latest/questions/sharing/variables)
- [Metabase OSS vs Enterprise](https://www.metabase.com/pricing)
