#!/usr/bin/env python3
"""
measure_query_performance.py — F4-02: Mide p50/p95/p99 de las 4 queries del dashboard.

Uso:
    python scripts/measure_query_performance.py
    python scripts/measure_query_performance.py --runs 5 --threshold 2.0

Requerimientos:
    - PostgreSQL accesible via variables de entorno (.env)
    - Datos generados (make data-generate)
    - Vistas materializadas actualizadas (make mv-refresh)

Exit code:
    0 si todas las queries tienen p95 < threshold (default: 2s)
    1 si alguna query excede el threshold
"""

import argparse
import os
import sys
import time
import statistics
from typing import Callable

import psycopg2


# ─── Queries del Dashboard ──────────────────────────────────

DASHBOARD_QUERIES = [
    {
        "name": "1. Rotación por Categoría",
        "sql": """
            SELECT categoria, mes, anio, ventas_totales, ingresos_totales,
                   productos_vendidos
            FROM mv_rotacion_mensual
            WHERE anio = '2026' AND mes = '03'
            ORDER BY ventas_totales DESC
        """,
    },
    {
        "name": "2. Stock Actual vs Mínimo",
        "sql": """
            SELECT producto_id, nombre, categoria, proveedor, stock_actual,
                   stock_minimo, estado
            FROM mv_stock_actual
            WHERE estado IN ('ALERTA', 'PRECAUCION')
            ORDER BY stock_actual ASC
        """,
    },
    {
        "name": "3. Top 10 Productos por Ventas",
        "sql": """
            SELECT producto_id, nombre, categoria, unidades_vendidas,
                   ingresos_totales, numero_ventas
            FROM mv_top_productos
            ORDER BY ingresos_totales DESC
            LIMIT 10
        """,
    },
    {
        "name": "4. Alertas de Stock Mínimo",
        "sql": """
            SELECT p.id, p.nombre, p.stock_actual, p.stock_minimo,
                   pr.nombre AS proveedor, pr.email AS contacto_proveedor
            FROM productos p
            JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.stock_actual <= p.stock_minimo
            ORDER BY p.stock_actual ASC
        """,
    },
]


# ─── Conexión a PostgreSQL ──────────────────────────────────

def _load_db_config() -> dict:
    """Load database connection config from environment variables."""
    password = os.getenv("POSTGRES_PASSWORD") or os.getenv("MB_DB_PASS")
    if not password:
        raise ValueError(
            "POSTGRES_PASSWORD (or MB_DB_PASS) not set. "
            "Create a .env file from .env.example."
        )
    return {
        "host": os.getenv("MB_DB_HOST", "postgres"),
        "port": int(os.getenv("MB_DB_PORT", 5432)),
        "dbname": os.getenv("MB_DB_DBNAME", "ecommerce"),
        "user": os.getenv("MB_DB_USER", "ecommerce"),
        "password": password,
    }


def _connect(db_config: dict) -> psycopg2.extensions.connection:
    """Connect to PostgreSQL and return connection handle."""
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True  # No transaction overhead for reads
        return conn
    except psycopg2.OperationalError as exc:
        print(f"ERROR: Cannot connect to PostgreSQL: {exc}", file=sys.stderr)
        sys.exit(1)


# ─── Medición ───────────────────────────────────────────────

def _measure_query_time(
    conn: psycopg2.extensions.connection,
    sql: str,
    runs: int,
) -> list[float]:
    """Execute a query `runs` times and return a list of wall-clock times (s)."""
    times: list[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.fetchall()  # Consume all results
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    return times


def _compute_percentiles(times: list[float]) -> dict[str, float]:
    """Compute p50, p95, p99 from a sorted list of times."""
    sorted_times = sorted(times)
    n = len(sorted_times)
    return {
        "p50": sorted_times[int(n * 0.50)],
        "p95": sorted_times[int(n * 0.95)],
        "p99": sorted_times[int(n * 0.99)],
        "mean": statistics.mean(sorted_times),
        "min": sorted_times[0],
        "max": sorted_times[-1],
    }


# ─── Reporte ────────────────────────────────────────────────

def _print_header():
    """Print the report header."""
    print("=" * 95)
    print(f"{'Query':<35} {'p50 (ms)':<10} {'p95 (ms)':<10} {'p99 (ms)':<10} "
          f"{'Status':<10}")
    print("=" * 95)


def _format_time(seconds: float) -> str:
    """Format seconds as milliseconds with 1 decimal."""
    return f"{seconds * 1000:.1f}"


def _print_row(name: str, stats: dict, threshold: float) -> bool:
    """Print a single query result row. Returns True if passing (< threshold)."""
    p95 = stats["p95"]
    passing = p95 < threshold
    status = "✅ PASS" if passing else "❌ FAIL"
    print(f"{name:<35} {_format_time(stats['p50']):<10} "
          f"{_format_time(p95):<10} {_format_time(stats['p99']):<10} "
          f"{status:<10}")
    return passing


def _print_summary(all_passing: bool, threshold: float):
    """Print summary line at the end."""
    print("=" * 95)
    if all_passing:
        print(f"✅ ALL QUERIES PASS (p95 < {threshold}s)")
    else:
        print(f"❌ SOME QUERIES FAILED (p95 >= {threshold}s)")
    print()


# ─── Main ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Measure p50/p95/p99 query latency for dashboard queries."
    )
    parser.add_argument(
        "--runs", type=int, default=10,
        help="Number of times to run each query (default: 10)",
    )
    parser.add_argument(
        "--threshold", type=float, default=2.0,
        help="p95 threshold in seconds (default: 2.0)",
    )
    args = parser.parse_args()

    db_config = _load_db_config()
    conn = _connect(db_config)

    _print_header()
    all_passing = True

    for query in DASHBOARD_QUERIES:
        times = _measure_query_time(conn, query["sql"], args.runs)
        stats = _compute_percentiles(times)
        passing = _print_row(query["name"], stats, args.threshold)
        if not passing:
            all_passing = False

    _print_summary(all_passing, args.threshold)
    conn.close()

    if not all_passing:
        sys.exit(1)


if __name__ == "__main__":
    main()
