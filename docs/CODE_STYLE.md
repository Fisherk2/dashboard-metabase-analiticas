# CODE_STYLE – Convenciones de Estilo de Código

**Fecha:** 2026-07-02 | **Autor:** Fisherk2

---

## 1. SQL

### Formato

- **Identación:** 4 espacios (no tabs).
- **Mayúsculas:** Palabras clave SQL en mayúsculas (`SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`).
- **Comentarios:** Usar `--` para comentarios en línea, `/* */` para bloques.
- **Nombres de columnas:** Descriptivos y en inglés (ej: `customer_id`, no `cli_id`).
- **JOINs:** Siempre explícitos (`INNER JOIN`, `LEFT JOIN`) — nunca implícitos.

### Convenciones de Nomenclatura

| **Tipo**                  | **Convención**                                        | **Ejemplo**                              |
| ------------------------- | ----------------------------------------------------- | ---------------------------------------- |
| **Tablas**                | Minúsculas, singular, separadas por guión bajo (`_`). | `ventas`, `productos`                    |
| **Columnas**              | Minúsculas, separadas por guión bajo (`_`).           | `producto_id`, `fecha_venta`             |
| **Índices**               | `idx_<tabla>_<columna>`                               | `idx_ventas_producto_id`                 |
| **Vistas Materializadas** | `mv_<descripción>`                                    | `mv_rotacion_mensual`                    |
| **Vistas**                | `v_<descripción>`                                     | `v_stock_alerts`                         |
| **Migraciones**           | `YYYYMMDD_HHMMSS_descripcion.sql`                     | `20260702_140000_crear_tabla_ventas.sql` |

### Ejemplo

```sql
-- Consulta de rotación por categoría
SELECT 
    c.name AS category,
    t.month,
    SUM(v.quantity) AS total_sales
FROM sales v
JOIN products p ON v.product_id = p.id
JOIN categories c ON p.category_id = c.id
JOIN time t ON v.time_id = t.id
GROUP BY c.name, t.month
ORDER BY total_sales DESC;
```

### Checklist Pre-Commit (SQL)

- [ ] Todas las tablas tienen `PRIMARY KEY`.
- [ ] Todas las columnas `FOREIGN KEY` tienen índices.
- [ ] Las queries usan `JOIN` explícitos (no `JOIN` implícitos).
- [ ] Las vistas materializadas están actualizadas (`REFRESH MATERIALIZED VIEW`).
- [ ] No se usa `SELECT *` — siempre listar columnas explícitamente.
- [ ] Se validó rendimiento con `EXPLAIN ANALYZE`.

---

## 2. Python

### Formato

- **Identación:** 4 espacios (PEP 8).
- **Nombres:** `snake_case` para variables y funciones, `PascalCase` para clases.
- **Docstrings:** Usar formato Google para funciones y clases.
- **Imports:** Agrupar al inicio del archivo (stdlib → third-party → local).
- **Tipado:** Usar type hints en funciones públicas.

### Convenciones de Nomenclatura

| **Tipo**           | **Convención**  | **Ejemplo**              |
| ------------------ | --------------- | ------------------------ |
| **Variables**      | `snake_case`    | `total_sales`            |
| **Funciones**      | `snake_case`    | `generate_products()`    |
| **Clases**         | `PascalCase`    | `DataGenerator`          |
| **Constantes**     | `UPPER_SNAKE`   | `MAX_RETRIES`            |
| **Módulos**        | `snake_case.py` | `generate_data.py`       |
| **Variables Entorno** | `UPPER_SNAKE` | `POSTGRES_PASSWORD`     |

### Ejemplo

```python
from faker import Faker
import psycopg2

def generate_products(n: int, conn: psycopg2.extensions.connection) -> None:
    """Generates n fake products and inserts them into the database.
    
    Args:
        n: Number of products to generate.
        conn: PostgreSQL connection object.
    """
    fake = Faker()
    cursor = conn.cursor()
    for _ in range(n):
        name = fake.word()
        price = fake.random_int(10, 1000)
        cursor.execute(
            "INSERT INTO products (name, price) VALUES (%s, %s)",
            (name, price)
        )
    conn.commit()
```

### Checklist Pre-Commit (Python)

- [ ] El código sigue PEP 8.
- [ ] Todas las funciones tienen docstrings.
- [ ] No hay credenciales hardcodeadas (usar variables de entorno).
- [ ] El script maneja excepciones (ej: `try/except` para conexiones a la BD).
- [ ] Se usan transacciones (`BEGIN`/`COMMIT`) en scripts de inserción.
- [ ] Type hints en funciones públicas.

---

## 3. Docker

### Convenciones

- **docker-compose.yml:** Usar variables de entorno para credenciales (nunca valores hardcodeados).
- **Volúmenes:** Configurar para persistencia de datos.
- **Dependencias:** Usar `depends_on` para orden de inicio.
- **Red:** Usar red interna de Docker (no exponer PostgreSQL a `0.0.0.0`).

### Checklist Pre-Commit (Docker)

- [ ] El `docker-compose.yml` usa variables de entorno para credenciales.
- [ ] Los volúmenes están configurados para persistencia.
- [ ] Los servicios dependen unos de otros (`depends_on`).
- [ ] No se exponen puertos sensibles a `0.0.0.0`.
- [ ] Se validó con `docker-compose config`.

---

## 4. Variables de Entorno

| **Variable**          | **Uso**                          | **Ejemplo**              |
| --------------------- | -------------------------------- | ------------------------ |
| `POSTGRES_PASSWORD`   | Contraseña de PostgreSQL         | `mi_contraseña_segura`   |
| `POSTGRES_USER`       | Usuario de PostgreSQL            | `admin`                  |
| `POSTGRES_DB`         | Nombre de la base de datos       | `ecommerce`              |
| `POSTGRES_PORT`       | Puerto de PostgreSQL             | `5432`                   |
| `METABASE_PORT`       | Puerto de Metabase               | `3000`                   |

**Nunca** hardcodear estas variables en archivos SQL, Python, o YAML. Siempre usar `.env`.
