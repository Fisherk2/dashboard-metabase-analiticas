#!/usr/bin/env python3
"""
generate_data.py — Synthetic data generation for e-commerce star schema.

Populates the star schema (10 tables) with realistic fake data using
Python + Faker. Follows FK order: dimensions first, facts second.

Usage:
    python generate_data.py                         # Full generation
    python generate_data.py --debug                  # Verbose logging
    python generate_data.py --reset                  # TRUNCATE + regenerate
    python generate_data.py --scale 0.5              # 50% data volume

Requires: PostgreSQL running (F1), schema initialized (make db-init).
"""

import argparse
import logging
import os
import random
import sys
from datetime import date, datetime, timedelta

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

# ─── Connection Configuration ────────────────────────────────
# When running inside Docker network, use "postgres" as host;
# when running from host, use "localhost" (requires PG port exposed).
_DB_HOST = os.getenv("MB_DB_HOST", "localhost")
if _DB_HOST == "postgres":
    # Check if we can resolve "postgres" — if not, fall back to localhost
    import socket
    try:
        socket.getaddrinfo("postgres", 5432)
    except socket.gaierror:
        _DB_HOST = "localhost"

DB_CONFIG = {
    "host": _DB_HOST,
    "port": int(os.getenv("MB_DB_PORT", 5432)),
    "dbname": os.getenv("MB_DB_DBNAME", "ecommerce"),
    "user": os.getenv("MB_DB_USER", "ecommerce"),
    "password": os.getenv("POSTGRES_PASSWORD", "change-me-in-production"),
}

# Default volumes (adjus ted by --scale)
DEFAULT_VOLUMES = {
    "categorias": 20,
    "proveedores": 50,
    "productos": 5000,
    "clientes": 2000,
    "tiempo": 365,
    "promociones": 30,
    "ventas": 100000,
    "inventario": 50000,
    "devoluciones": 5000,
    "logistica": 20000,
}


def connect_db() -> psycopg2.extensions.connection:
    """Create and return a PostgreSQL connection using environment variables."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Cannot connect to PostgreSQL: {e}")
        sys.exit(1)


class DataGenerator:
    """Generates synthetic data for all tables in FK-safe order.

    Uses Faker for realistic data and psycopg2 for batch inserts.
    Transactions are committed after each table batch.
    """

    def __init__(self, conn: psycopg2.extensions.connection,
                 debug: bool = False, scale: float = 1.0):
        self.conn = conn
        self.debug = debug
        self.scale = scale
        self.fake = Faker("es_MX")
        Faker.seed(42)  # Reproducibility
        self.cur = conn.cursor()

        # Scale-sensitive volumes
        self.num = {k: max(1, int(v * scale))
                    for k, v in DEFAULT_VOLUMES.items()}
        if debug:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s"
            )

    def _log(self, msg: str) -> None:
        """Log message if debug mode is enabled."""
        if self.debug:
            logging.info(msg)

    # ─── Dimension Seeders ──────────────────────────────────

    def _seed_categorias(self) -> None:
        """Insert 20 fixed categories."""
        categorias = [
            "Electrónica", "Ropa", "Hogar", "Deportes", "Libros",
            "Jardín", "Automotriz", "Juguetes", "Salud", "Belleza",
            "Música", "Oficina", "Mascotas", "Cocina", "Bebidas",
            "Videojuegos", "Fotografía", "Relojes", "Joyas", "Instrumentos",
        ]
        self.cur.execute("BEGIN")
        for nombre in categorias:
            self.cur.execute(
                "INSERT INTO categorias (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING",
                (nombre,)
            )
        self.conn.commit()
        self._log(f"✓ categorias: {len(categorias)} registros")

    def _seed_proveedores(self) -> None:
        """Insert 50 suppliers with Faker."""
        self.cur.execute("BEGIN")
        for _ in range(self.num["proveedores"]):
            self.cur.execute(
                "INSERT INTO proveedores (nombre, contacto, email) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING",
                (self.fake.company(), self.fake.name(), self.fake.email())
            )
        self.conn.commit()
        self.cur.execute("SELECT COUNT(*) FROM proveedores")
        count = self.cur.fetchone()[0]
        self._log(f"✓ proveedores: {count} registros")

    def _seed_productos(self) -> None:
        """Insert 5K products with Pareto distribution across categories.

        Uses weighted random to simulate 70% sales on 30% products.
        Products reference existing categorias and proveedores.
        """
        # Fetch existing FK references
        self.cur.execute("SELECT id FROM categorias")
        categoria_ids = [row[0] for row in self.cur.fetchall()]
        self.cur.execute("SELECT id FROM proveedores")
        proveedor_ids = [row[0] for row in self.cur.fetchall()]

        self.cur.execute("BEGIN")
        for _ in range(self.num["productos"]):
            # Weighted categories: first 30% get 70% probability
            cat_id = random.choices(
                categoria_ids,
                weights=[3 if i < len(categoria_ids) * 0.3 else 1
                         for i in range(len(categoria_ids))],
                k=1
            )[0]
            self.cur.execute(
                """INSERT INTO productos
                   (nombre, descripcion, precio, stock_actual, stock_minimo,
                    categoria_id, proveedor_id, fecha_creacion)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    self.fake.word().capitalize() + f" {random.randint(1, 999)}",
                    self.fake.sentence(nb_words=8),
                    round(random.uniform(5.0, 5000.0), 2),
                    random.randint(0, 500),
                    random.randint(1, 20),
                    cat_id,
                    random.choice(proveedor_ids),
                    self.fake.date_time_between(
                        start_date="-2y", end_date="now"
                    ),
                )
            )
        self.conn.commit()
        self._log(f"✓ productos: {self.num['productos']} registros")

    def _seed_clientes(self) -> None:
        """Insert 2K customers with Faker."""
        self.cur.execute("BEGIN")
        for _ in range(self.num["clientes"]):
            self.cur.execute(
                """INSERT INTO clientes (nombre, email, direccion, fecha_registro)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (email) DO NOTHING""",
                (
                    self.fake.name(),
                    self.fake.email(),
                    self.fake.address(),
                    self.fake.date_time_between(
                        start_date="-3y", end_date="now"
                    ),
                )
            )
        self.conn.commit()
        self.cur.execute("SELECT COUNT(*) FROM clientes")
        count = self.cur.fetchone()[0]
        self._log(f"✓ clientes: {count} registros")

    def _seed_tiempo(self) -> None:
        """Insert 365 days (2026 full year) with computed attributes."""
        self.cur.execute("BEGIN")
        d = date(2026, 1, 1)
        dias = ["Lunes", "Martes", "Miércoles", "Jueves",
                "Viernes", "Sábado", "Domingo"]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        for _ in range(self.num["tiempo"]):
            mes_idx = d.month - 1
            trim = f"Q{(mes_idx // 3) + 1}"
            self.cur.execute(
                """INSERT INTO tiempo (fecha, dia_semana, mes, anio, trimestre)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (fecha) DO NOTHING""",
                (
                    d,
                    dias[d.weekday()],
                    meses[mes_idx],
                    str(d.year),
                    trim,
                )
            )
            d += timedelta(days=1)
        self.conn.commit()
        self._log(f"✓ tiempo: {self.num['tiempo']} registros (2026)")

    def _seed_promociones(self) -> None:
        """Insert 30 promotions with date ranges."""
        self.cur.execute("SELECT id FROM categorias")
        categoria_ids = [row[0] for row in self.cur.fetchall()]

        self.cur.execute("BEGIN")
        for _ in range(self.num["promociones"]):
            start = self.fake.date_between(start_date="-1y", end_date="+6m")
            end = start + timedelta(days=random.randint(7, 60))
            # 50% of promos apply to a specific category
            cat_id = random.choice([None] + categoria_ids)
            self.cur.execute(
                """INSERT INTO promociones
                   (nombre, descuento, fecha_inicio, fecha_fin, categoria_id)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    self.fake.word().capitalize(),
                    round(random.uniform(5.0, 50.0), 2),
                    start,
                    end,
                    cat_id,
                )
            )
        self.conn.commit()
        self._log(f"✓ promociones: {self.num['promociones']} registros")

    # ─── Fact Seeders ───────────────────────────────────────

    def _seed_ventas(self) -> None:
        """Insert 100K sales with Pareto distribution.

        70% of sales concentrate on 30% of products (Pareto principle).
        precio_unitario is fetched from productos at insert time.
        """
        self.cur.execute("SELECT id FROM productos")
        producto_ids = [row[0] for row in self.cur.fetchall()]
        self.cur.execute("SELECT id FROM clientes")
        cliente_ids = [row[0] for row in self.cur.fetchall()]
        self.cur.execute("SELECT id FROM tiempo")
        tiempo_ids = [row[0] for row in self.cur.fetchall()]
        self.cur.execute("SELECT id FROM promociones")
        promo_ids = [row[0] for row in self.cur.fetchall()]

        # Pareto weighting: top 30% of products get 70% probability
        pareto_idx = max(1, int(len(producto_ids) * 0.3))
        pareto_weights = (
            [4] * pareto_idx + [1] * (len(producto_ids) - pareto_idx)
        )

        self.cur.execute("BEGIN")
        batch_count = 0
        for _ in range(self.num["ventas"]):
            producto_id = random.choices(producto_ids, weights=pareto_weights, k=1)[0]
            cliente_id = random.choice(cliente_ids)
            tiempo_id = random.choice(tiempo_ids)

            # Fetch product's precio for this sale
            self.cur.execute(
                "SELECT precio FROM productos WHERE id = %s", (producto_id,)
            )
            precio = self.cur.fetchone()[0]

            cantidad = random.randint(1, 5)
            total = round(cantidad * precio, 2)

            # 30% of sales have a promo
            promocion_id = random.choice([None] * 7 + promo_ids) if promo_ids else None

            # Generate a timestamp within 2026
            fecha_venta = self.fake.date_time_between(
                start_date=datetime(2026, 1, 1),
                end_date=datetime(2026, 12, 31, 23, 59, 59)
            )

            self.cur.execute(
                """INSERT INTO ventas
                   (producto_id, cliente_id, fecha_id, cantidad,
                    precio_unitario, total, promocion_id, fecha_venta)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (producto_id, cliente_id, tiempo_id, cantidad,
                 precio, total, promocion_id, fecha_venta)
            )
            batch_count += 1
            if batch_count % 10000 == 0:
                self._log(f"  ventas progress: {batch_count}/{self.num['ventas']}")

        self.conn.commit()
        self._log(f"✓ ventas: {self.num['ventas']} registros")

    def _seed_inventario(self) -> None:
        """Insert 50K inventory records: daily snapshots per product."""
        self.cur.execute("SELECT id, stock_actual FROM productos")
        productos = self.cur.fetchall()
        self.cur.execute("SELECT id FROM tiempo")
        tiempo_ids = [row[0] for row in self.cur.fetchall()]
        self.cur.execute("SELECT id FROM proveedores")
        proveedor_ids = [row[0] for row in self.cur.fetchall()]

        # Target ~10 records per product (50K for 5K products)
        snaps_per_product = max(1, self.num["inventario"] // len(productos))
        total_records = min(
            self.num["inventario"],
            len(productos) * snaps_per_product
        )

        self.cur.execute("BEGIN")
        batch_count = 0
        for prod_id, stock_actual in productos:
            stock_inicial = stock_actual
            for _ in range(snaps_per_product):
                if batch_count >= total_records:
                    break
                stock_final = max(0, stock_inicial + random.randint(-20, 20))
                self.cur.execute(
                    """INSERT INTO inventario
                       (producto_id, fecha_id, stock_inicial, stock_final, proveedor_id, fecha_registro)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        prod_id,
                        random.choice(tiempo_ids),
                        stock_inicial,
                        stock_final,
                        random.choice(proveedor_ids),
                        self.fake.date_time_between(
                            start_date=datetime(2026, 1, 1),
                            end_date=datetime(2026, 12, 31, 23, 59, 59)
                        ),
                    )
                )
                stock_inicial = stock_final
                batch_count += 1
        self.conn.commit()
        self._log(f"✓ inventario: {batch_count} registros")

    def _seed_devoluciones(self) -> None:
        """Insert 5K returns (5% of ventas)."""
        self.cur.execute("SELECT id, fecha_venta FROM ventas")
        ventas = self.cur.fetchall()
        self.cur.execute("SELECT id FROM tiempo")
        tiempo_ids = [row[0] for row in self.cur.fetchall()]
        self.cur.execute("SELECT id FROM clientes")
        cliente_ids = [row[0] for row in self.cur.fetchall()]

        num_devoluciones = min(self.num["devoluciones"], len(ventas))
        selected_ventas = random.sample(ventas, num_devoluciones)
        motivos = [
            "Producto defectuoso", "No corresponde a la descripción",
            "Talla incorrecta", "Producto equivocado",
            "Ya no lo necesita", "Llegó dañado",
            "Insatisfecho con la calidad", "Cambio de opinión",
            "No compatible", "Retraso en la entrega",
        ]

        self.cur.execute("BEGIN")
        for venta_id, fecha_venta in selected_ventas:
            # Fetch producto_id and cliente_id from the venta
            self.cur.execute(
                "SELECT producto_id, cliente_id FROM ventas WHERE id = %s",
                (venta_id,)
            )
            row = self.cur.fetchone()
            if not row:
                continue
            producto_id, cliente_id = row

            self.cur.execute(
                """INSERT INTO devoluciones
                   (venta_id, producto_id, cliente_id, fecha_id,
                    cantidad, motivo, fecha_devolucion)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    venta_id,
                    producto_id,
                    cliente_id,
                    random.choice(tiempo_ids),
                    random.randint(1, 3),
                    random.choice(motivos),
                    fecha_venta + timedelta(days=random.randint(1, 30)),
                )
            )
        self.conn.commit()
        self._log(f"✓ devoluciones: {num_devoluciones} registros")

    def _seed_logistica(self) -> None:
        """Insert 20K shipping records (20% of ventas)."""
        self.cur.execute("SELECT id, fecha_venta FROM ventas")
        ventas = self.cur.fetchall()
        self.cur.execute("SELECT id FROM tiempo")
        tiempo_ids = [row[0] for row in self.cur.fetchall()]
        self.cur.execute("SELECT id FROM proveedores")
        proveedor_ids = [row[0] for row in self.cur.fetchall()]

        num_logistica = min(self.num["logistica"], len(ventas))
        selected_ventas = random.sample(ventas, num_logistica)
        estados = ["Enviado", "En tránsito", "Entregado", "Pendiente"]
        metodos = ["DHL", "FedEx", "Estafeta", "Correos de México",
                   "UPS", "RedPack"]

        self.cur.execute("BEGIN")
        for venta_id, fecha_venta in selected_ventas:
            dias_entrega = random.randint(1, 10)
            self.cur.execute(
                """INSERT INTO logistica
                   (venta_id, proveedor_id, fecha_entrega_id,
                    estado, metodo_envio, fecha_entrega)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    venta_id,
                    random.choice(proveedor_ids),
                    random.choice(tiempo_ids),
                    random.choice(estados),
                    random.choice(metodos),
                    fecha_venta + timedelta(days=dias_entrega)
                    if random.random() > 0.3 else None,
                )
            )
        self.conn.commit()
        self._log(f"✓ logistica: {num_logistica} registros")

    # ─── Orchestration ──────────────────────────────────────

    def reset(self) -> None:
        """TRUNCATE all tables in reverse FK order."""
        self.cur.execute("BEGIN")
        tables = [
            "logistica", "devoluciones", "inventario", "ventas",
            "promociones", "tiempo", "productos", "clientes",
            "proveedores", "categorias",
        ]
        for table in tables:
            self.cur.execute(f"TRUNCATE TABLE {table} CASCADE")
        self.conn.commit()
        self._log("✓ TRUNCATE CASCADE en 10 tablas")

    def generate_all(self) -> None:
        """Generate all data in FK-safe order."""
        self._log(f"Iniciando generación (scale={self.scale})...")
        self._seed_categorias()
        self._seed_proveedores()
        self._seed_productos()
        self._seed_clientes()
        self._seed_tiempo()
        self._seed_promociones()
        self._seed_ventas()
        self._seed_inventario()
        self._seed_devoluciones()
        self._seed_logistica()
        self._log("✓ Generación completada exitosamente")

    def print_summary(self) -> None:
        """Print record counts per table."""
        tables = [
            "categorias", "proveedores", "productos", "clientes",
            "tiempo", "promociones", "ventas", "inventario",
            "devoluciones", "logistica",
        ]
        total = 0
        print("\n=== RESUMEN DE DATOS GENERADOS ===")
        for table in tables:
            self.cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cur.fetchone()[0]
            print(f"  {table:15s}: {count:>8,} registros")
            total += count
        print(f"  {'---':15s}  {'---':>8}")
        print(f"  {'TOTAL':15s}: {total:>8,} registros\n")
        self.conn.commit()

    def close(self) -> None:
        """Close cursor and connection."""
        self.cur.close()


def main() -> None:
    """Main entry point: parse args, connect, generate or reset data."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic data for e-commerce star schema"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="TRUNCATE all tables before generating"
    )
    parser.add_argument(
        "--scale", type=float, default=1.0,
        help="Scale factor for data volume (default: 1.0)"
    )
    args = parser.parse_args()

    conn = connect_db()
    gen = DataGenerator(conn, debug=args.debug, scale=args.scale)

    try:
        if args.reset:
            gen.reset()
        gen.generate_all()
        gen.print_summary()
    except Exception as e:
        conn.rollback()
        logging.error(f"Error during generation: {e}")
        sys.exit(1)
    finally:
        gen.close()
        conn.close()


if __name__ == "__main__":
    main()
