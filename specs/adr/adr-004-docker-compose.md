# ADR-004: Docker Compose para Orquestación de Servicios

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Estado:** Aceptado

---

## Decisión

Usar **Docker Compose** para orquestar los servicios del proyecto (PostgreSQL + Metabase).

---

## Contexto

El proyecto requiere:

- Levantar PostgreSQL 15+ y Metabase de forma reproducible
- Aislar servicios en contenedores independientes
- Configurar red interna para comunicación segura
- Persistir datos en volúmenes
- Facilitar la reproducción del entorno en diferentes máquinas
- No requerir configuración manual de servicios

---

## Alternativas Consideradas

### Instalación Nativa

**Ventajas:**
- Sin dependencia de Docker
- Rendimiento ligeramente superior (sin overhead de contenedores)

**Desventajas:**
- Requiere instalar PostgreSQL y Metabase manualmente en cada máquina
- Configuración diferente en cada sistema operativo (Linux, macOS, Windows)
- Difícil reproducir el entorno exacto en otras máquinas
- No aísla servicios (conflictos de puertos, versiones)
- Limpieza compleja (desinstalar servicios, eliminar datos)

**Conclusión:** Descartado por falta de reproducibilidad y portabilidad.

---

### Kubernetes (K8s)

**Ventajas:**
- Orquestación profesional a escala
- Soporte para alta disponibilidad y escalado automático
- Estándar de la industria para producción

**Desventajas:**
- Overkill para un proyecto de portafolio con 2 servicios
- Curva de aprendizaje alta (pods, deployments, services, ingress)
- Requiere cluster de Kubernetes (minikube, kind, o cloud)
- Complejidad innecesaria para desarrollo local
- No es necesario para demostrar habilidades de SQL/BI

**Conclusión:** Descartado por complejidad innecesaria y alcance del proyecto.

---

### Vagrant

**Ventajas:**
- Permite crear máquinas virtuales completas
- Útil para entornos de desarrollo complejos

**Desventajas:**
- Requiere VirtualBox o VMware (overhead de VM completa)
- Más pesado que Docker (VM vs contenedores)
- Menos adoptado que Docker en la industria
- No es ideal para orquestar múltiples servicios ligeros

**Conclusión:** Descartado por overhead innecesario y menor adopción.

---

### Instalación con Binarios Directos

**Ventajas:**
- Control total sobre la configuración
- Sin dependencia de herramientas externas

**Desventajas:**
- Requiere descargar y configurar PostgreSQL y Metabase manualmente
- Diferentes pasos para cada sistema operativo
- Difícil de documentar y reproducir
- No aísla servicios (conflictos de puertos, dependencias)
- Limpieza manual compleja

**Conclusión:** Descartado por falta de reproducibilidad y portabilidad.

---

## Razones para Elegir Docker Compose

1. **Reproducibilidad:** `docker-compose up -d` levanta el entorno completo en cualquier máquina con Docker instalado.
2. **Aislamiento:** Cada servicio corre en su propio contenedor (PostgreSQL, Metabase).
3. **Red interna:** Servicios se comunican por red Docker (`ecommerce_net`), sin exponer puertos sensibles.
4. **Volúmenes persistentes:** Datos de PostgreSQL sobreviven reinicios de contenedores.
5. **Portabilidad:** Funciona en Linux, macOS, y Windows con Docker Desktop.
6. **Simplicidad:** Un solo archivo `docker-compose.yml` define toda la infraestructura.
7. **Dependencias claras:** `depends_on` con `service_healthy` garantiza orden de inicio.
8. **Limpieza sencilla:** `docker-compose down -v` elimina todo (contenedores + volúmenes).
9. **Estándar de la industria:** Docker Compose es ampliamente adoptado para desarrollo local.
10. **Documentación clara:** Fácil de documentar y reproducir para portafolio.

---

## Estructura de Docker Compose

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks:
      - ecommerce_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  metabase:
    image: metabase/metabase:latest
    container_name: metabase
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: h2
      MB_DB_FILE: /metabase-data/metabase.db
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - mb_data:/metabase-data
    networks:
      - ecommerce_net

volumes:
  pg_data:
  mb_data:

networks:
  ecommerce_net:
    driver: bridge
```

---

## Consecuencias

### Positivas
- Entorno reproducible en cualquier máquina con Docker.
- Aislamiento de servicios (PostgreSQL no expuesto al host).
- Persistencia de datos con volúmenes Docker.
- Fácil de documentar y compartir para portafolio.
- Limpieza sencilla con `docker-compose down -v`.

### Negativas
- Requiere Docker instalado (20+ recomendado).
- Overhead mínimo de contenedores vs instalación nativa.
- Dependencia de imágenes de Docker Hub (requiere internet para pull inicial).

### Neutrales
- Docker Compose es estándar para desarrollo local (no para producción).
- El proyecto es local-only, por lo que Docker Compose es adecuado.

---

## Validación

```bash
# Validar configuración
docker-compose config

# Levantar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Verificar logs
docker-compose logs -f postgres
docker-compose logs -f metabase

# Verificar conexión
docker exec -it postgres pg_isready -U admin

# Verificar persistencia
docker-compose down
docker-compose up -d
docker exec -it postgres psql -U admin -d ecommerce -c "SELECT 1;"

# Limpieza completa
docker-compose down -v
```

---

## Referencias

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Compose PostgreSQL](https://hub.docker.com/_/postgres)
- [Docker Compose Metabase](https://hub.docker.com/r/metabase/metabase)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)
- [Docker Networks](https://docs.docker.com/network/)
