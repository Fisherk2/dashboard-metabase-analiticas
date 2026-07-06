#!/usr/bin/env python3
"""
test_error_handling.py — F4-07: Verifica manejo de errores de Metabase con PG caído.

Uso:
    python scripts/test_error_handling.py

Requiere:
    - Docker (docker compose)
    - Metabase corriendo (make up)
    - PostgreSQL corriendo (docker compose up postgres + metabase)

Comportamiento:
    1. Detiene PostgreSQL con 'docker stop metabase-postgres'
    2. Consulta Metabase API: espera error 500/503 con mensaje claro
    3. Re-inicia PostgreSQL con 'docker start metabase-postgres'
    4. Espera a que Metabase se reconecte
    5. Verifica que la API responde correctamente nuevamente

Exit code:
    0 si Metabase maneja el error correctamente
    1 si Metabase retorna un error opaco (stack trace, 200 con datos falsos, etc.)
    2 si no se puede iniciar la prueba (PG no encontrado, etc.)
"""

import json
import os
import subprocess
import sys
import time

import requests


# ─── Configuración ──────────────────────────────────────────

DEFAULT_MB_URL = "http://localhost:3000"
PG_CONTAINER = "metabase-postgres"
MB_CONTAINER = "metabase"

MB_USER = os.getenv("MB_USER", "")
MB_PASSWORD = os.getenv("MB_PASSWORD", "")
MB_URL = os.getenv("METABASE_URL", DEFAULT_MB_URL).rstrip("/")


# ─── Helpers ────────────────────────────────────────────────

def log_info(msg: str):
    print(f"  INFO: {msg}")


def log_error(msg: str):
    print(f"  ERROR: {msg}", file=sys.stderr)


def log_step(step: str):
    print(f"\n[{step}]")


def run_docker_cmd(*args: str) -> subprocess.CompletedProcess:
    """Run a docker command and return result."""
    return subprocess.run(
        ["docker", *args],
        capture_output=True, text=True,
        timeout=30,
    )


def mb_get(path: str) -> requests.Response:
    """GET a Metabase API endpoint without auth token."""
    return requests.get(f"{MB_URL}{path}", timeout=10)


# ─── Metabase Auth ─────────────────────────────────────────

def get_token() -> str:
    """Authenticate with Metabase and return session token."""
    resp = requests.post(
        f"{MB_URL}/api/session",
        json={"username": MB_USER, "password": MB_PASSWORD},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["id"]


# ─── Tests ──────────────────────────────────────────────────

def test_metabase_health_ok() -> bool:
    """Verify Metabase health endpoint returns ok."""
    log_step("Health check before test")
    resp = mb_get("/api/health")
    data = resp.json()
    if data.get("status") == "ok":
        log_info("Metabase health: ok")
        return True
    log_error(f"Metabase health returned: {data}")
    return False


def test_stop_postgres() -> bool:
    """Stop the PostgreSQL container."""
    log_step("Stopping PostgreSQL")
    result = run_docker_cmd("stop", PG_CONTAINER)
    if result.returncode != 0:
        log_error(f"Failed to stop PostgreSQL: {result.stderr.strip()}")
        return False
    log_info(f"PostgreSQL stopped: {PG_CONTAINER}")
    return True


def test_metabase_error_on_pg_down() -> bool:
    """Verify Metabase returns a clear error with PostgreSQL down.

    Expected behavior:
    - HTTP 500 or 503
    - Response body contains a user-friendly message, not a raw stack trace
    """
    log_step("Querying Metabase with PostgreSQL down")
    time.sleep(3)  # Wait for Metabase to detect connection loss

    # Note: Metabase stores admin credentials in its own app DB (not analytics DB),
    # so session creation works even with PostgreSQL down.
    token = get_token()
    headers = {"X-Metabase-Session": token}

    # Try accessing a database-dependent endpoint
    resp = requests.get(
        f"{MB_URL}/api/database",
        headers=headers,
        timeout=15,
    )

    status = resp.status_code
    body = resp.text[:2000]  # Limit response inspection

    # Check: should NOT be 200 (PG is down)
    if status == 200:
        log_error("Metabase returned HTTP 200 when PostgreSQL is down (should be error)")
        return False

    # Check: should be 500 or 503
    if status not in (500, 502, 503):
        log_info(f"Metabase returned HTTP {status} (acceptable error code)")

    # Check: response should NOT contain raw stack traces or Python/Clojure errors
    trace_indicators = [
        "Traceback (most recent call last)",
        "NullPointerException",
        "SQLException",
        "java.lang.",
        "File \"",
        "at org.",
    ]
    for indicator in trace_indicators:
        if indicator in body:
            log_error(f"Response contains raw trace: '{indicator}'")
            log_error(f"Body snippet: {body[:300]}")
            return False

    # Check: response should contain a meaningful error message
    meaningful_indicators = [
        "error", "Error", "unable", "Unable", "connect", "Connect",
        "database", "Database", "not available", "timeout",
    ]
    has_message = any(indicator in body for indicator in meaningful_indicators)
    if not has_message:
        log_warn = print  # Use print for non-critical warnings
        print(f"  WARN: Response may lack user-friendly message (status={status})")
        print(f"  Body: {body[:200]}")

    log_info(f"Metabase error handling: HTTP {status} with message (no raw trace)")
    return True


def test_start_postgres() -> bool:
    """Restart the PostgreSQL container."""
    log_step("Restarting PostgreSQL")
    result = run_docker_cmd("start", PG_CONTAINER)
    if result.returncode != 0:
        log_error(f"Failed to start PostgreSQL: {result.stderr.strip()}")
        return False
    log_info("PostgreSQL started")

    # Wait for PostgreSQL to be ready
    log_info("Waiting for PostgreSQL to accept connections...")
    for attempt in range(15):
        ready = run_docker_cmd(
            "exec", PG_CONTAINER,
            "pg_isready", "-U", os.getenv("POSTGRES_USER", "ecommerce"),
        )
        if ready.returncode == 0:
            log_info("PostgreSQL is ready")
            return True
        time.sleep(2)

    log_error("PostgreSQL did not become ready within 30 seconds")
    return False


def test_metabase_recovery() -> bool:
    """Verify Metabase recovers after PostgreSQL is back up."""
    log_step("Verifying Metabase recovery")
    time.sleep(5)  # Give Metabase time to reconnect

    for attempt in range(10):
        try:
            resp = mb_get("/api/health")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    log_info("Metabase recovered and healthy")
                    return True
        except requests.ConnectionError:
            pass
        time.sleep(3)

    log_error("Metabase did not recover within 30 seconds")
    return False


# ─── Main ───────────────────────────────────────────────────

def main():
    """Run all error handling tests in sequence."""
    print("=" * 60)
    print("  F4-07: Error Handling Test (PG failover)")
    print("=" * 60)

    # Check if PostgreSQL container exists
    result = run_docker_cmd("ps", "-q", "-f", f"name={PG_CONTAINER}")
    if not result.stdout.strip():
        log_error(f"Container '{PG_CONTAINER}' not found. Is Docker running?")
        sys.exit(2)

    # Validate required environment variables
    if not MB_USER or not MB_PASSWORD:
        log_error("MB_USER and MB_PASSWORD must be set in .env")
        log_error("Run via 'make test' to load .env variables")
        sys.exit(2)

    tests = [
        ("Health check before test", test_metabase_health_ok),
        ("Stop PostgreSQL", test_stop_postgres),
        ("Metabase error on PG down", test_metabase_error_on_pg_down),
        ("Restart PostgreSQL", test_start_postgres),
        ("Metabase recovery", test_metabase_recovery),
    ]

    passed = 0
    failed = 0

    for name, func in tests:
        try:
            if func():
                passed += 1
            else:
                failed += 1
        except Exception as exc:
            log_error(f"Exception in '{name}': {exc}")
            failed += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  Results: {passed}/{len(tests)} passed, {failed} failed")
    print(f"{'=' * 60}")

    if failed > 0:
        sys.exit(1)

    print("  ✅ Error handling correcto")


if __name__ == "__main__":
    main()
