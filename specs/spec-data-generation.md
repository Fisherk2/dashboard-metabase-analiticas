# Spec: Data Generation — Datos Sintéticos con Python + Faker

**Fecha:** 2026-07-02 | **Autor:** Fisherk2 | **Fase:** F2

---

## 1. Objetivo

Generar datos sintéticos realistas para poblar el schema estrella usando Python + Faker. El script debe ser reproducible, usar transacciones, y validar la integridad de los datos generados.

---

## 2. Volúmenes de Datos

| **Tabla**      | **Registros** | **Distribución**                              |
| -------------- | ------------- | --------------------------------------------- |
| `categorias`   | 20            | Fijas (electrónica, ropa, hogar, etc.)        |
| `proveedores`  | 50            | Faker: company, email                         |
| `productos`    | 5,000         | Faker: word, price, stock                     |
| `clientes`     | 2,000         | Faker: name, email, address                   |
| `tiempo`       | 365           | 1 año de fechas (2026-01-01 a 2026-12-31)    |
| `promociones`  | 30            | Faker: word, discount, date range             |
| `ventas`       | 100,000       | Distribución ponderada por categoría          |
| `inventario`   | 50,000        | Movimientos diarios por producto              |
| `devoluciones` | 5,000         | 5% de las ventas (distribución aleatoria)     |
| `logistica`    | 20,000        | Asociada a ventas (opcional)                  |

---

## 3. Reglas de Negocio

1. **Ventas ponderadas:** 70% de las ventas se concentran en el 30% de los productos (distribución Pareto).
2. **Stock coherente:** `stock_actual` en `productos` debe ser consistente con el último registro de `inventario`.
3. **Fechas válidas:** `fecha_venta` en `ventas` debe existir en la tabla `tiempo`.
4. **Devoluciones:** Solo pueden referenciar ventas existentes.
5. **Precios:** `precio_unitario` en `ventas` debe coincidir con `precio` en `productos` al momento de la venta.

---

## 4. Archivos

| **Archivo**          | **Ubicación**                   | **Propósito**                          |
| -------------------- | ------------------------------- | -------------------------------------- |
| `generate_data.py`   | `scripts/generate_data.py`      | Script principal de generación         |
| `requirements.txt`   | `scripts/requirements.txt`      | Dependencias Python                    |

### Dependencias Python

```
faker>=18.0
psycopg2-binary>=2.9
python-dotenv>=1.0
```

---

## 5. Estructura del Script

```python
# generate_data.py — Estructura principal

def main():
    """Main entry point."""
    conn = connect_db()  # Usa variables de entorno
    
    try:
        # Orden de inserción (respeta FKs)
        generate_categorias(conn)      # 20
        generate_proveedores(conn)     # 50
        generate_productos(conn)       # 5,000
        generate_clientes(conn)        # 2,000
        generate_tiempo(conn)          # 365
        generate_promociones(conn)     # 30
        generate_ventas(conn)          # 100,000
        generate_inventario(conn)      # 50,000
        generate_devoluciones(conn)    # 5,000
        generate_logistica(conn)       # 20,000 (opcional)
        
        conn.commit()
        log_summary(conn)
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
```

---

## 6. Criterios de Aceptación

- [ ] `pip install -r scripts/requirements.txt` instala sin errores.
- [ ] `python scripts/generate_data.py` completa sin errores.
- [ ] Volúmenes de datos dentro de rangos esperados.
- [ ] Integridad referencial: todas las FKs son válidas.
- [ ] Transacciones: `BEGIN`/`COMMIT` en cada bloque de inserción.
- [ ] Credenciales desde `.env` (no hardcodeadas).
- [ ] Modo debug: `python scripts/generate_data.py --debug` muestra logs detallados.
- [ ] Reproducible: ejecutar dos veces produce datos válidos (usar `TRUNCATE` + `INSERT`).

---

## 7. Dependencias

- **Requiere:** F2 (Schema estrella creado).
- **Habilita:** F3 (Dashboards), F4 (Pruebas).

---

## 8. Verificación

```bash
# Instalar dependencias
pip install -r scripts/requirements.txt

# Generar datos
python scripts/generate_data.py

# Modo debug
python scripts/generate_data.py --debug

# Validar volúmenes
docker exec -it postgres psql -U admin -d ecommerce -c "
SELECT 'productos' AS tabla, COUNT(*) FROM productos
UNION ALL SELECT 'ventas', COUNT(*) FROM ventas
UNION ALL SELECT 'inventario', COUNT(*) FROM inventario
UNION ALL SELECT 'devoluciones', COUNT(*) FROM devoluciones
ORDER BY tabla;
"

# Validar integridad referencial
docker exec -it postgres psql -U admin -d ecommerce -c "
SELECT COUNT(*) AS ventas_sin_producto 
FROM ventas v LEFT JOIN productos p ON v.producto_id = p.id 
WHERE p.id IS NULL;
"
```
