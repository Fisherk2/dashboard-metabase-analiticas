#!/usr/bin/env python3
"""
validate_dashboard_exports.py — F4-04: Valida exportación CSV/XLSX de los paneles.

Uso:
    python scripts/validate_dashboard_exports.py

Requiere:
    - Metabase accesible via METABASE_URL, MB_USER, MB_PASSWORD en .env
    - make metabase-setup ejecutado previamente (dashboard + cards exist)

Exit code:
    0 si todas las exportaciones son válidas
    1 si alguna falla

Formato de salida:
    Tabla con: card_name, csv_rows, status
"""

import csv
import io
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


# ─── Configuración ──────────────────────────────────────────

_DEFAULT_MB_URL = "http://localhost:3000"


def _load_config() -> dict:
    """Load Metabase connection config from environment variables."""
    return {
        "url": os.getenv("METABASE_URL", _DEFAULT_MB_URL).rstrip("/"),
        "user": os.getenv("MB_USER", ""),
        "password": os.getenv("MB_PASSWORD", ""),
    }


# ─── Autenticación Metabase ─────────────────────────────────

def _auth(config: dict) -> str:
    """Authenticate with Metabase API and return session token."""
    if not config["user"] or not config["password"]:
        raise ValueError(
            "MB_USER and MB_PASSWORD must be set in .env"
        )
    resp = requests.post(
        f"{config['url']}/api/session",
        json={"username": config["user"], "password": config["password"]},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["id"]


# ─── Obtener cards ──────────────────────────────────────────

def _get_cards(config: dict, token: str) -> list[dict[str, Any]]:
    """Fetch all saved questions (cards) from Metabase."""
    headers = {"X-Metabase-Session": token}
    resp = requests.get(f"{config['url']}/api/card", headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ─── Validar exportaciones ──────────────────────────────────

def _fetch_export(
    config: dict,
    token: str,
    card_id: int,
    fmt: str,
) -> tuple:  # (response, None) or (None, (row_count, error_msg))
    """Fetch an export from Metabase API.

    Returns a (response, None) tuple on success, or
    (None, (0, error_message)) on failure.
    """
    headers = {"X-Metabase-Session": token}
    url = f"{config['url']}/api/card/{card_id}/query/{fmt}"
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            return (None, (0, f"HTTP {resp.status_code}"))
        return (resp, None)
    except requests.Timeout:
        return (None, (0, "TIMEOUT"))
    except Exception as exc:
        return (None, (0, f"ERROR: {exc}"))


def _validate_csv_export(
    config: dict,
    token: str,
    card_id: int,
    card_name: str,
) -> tuple[int, str]:
    """Download CSV export of a card and validate it.

    Returns:
        (row_count, status_message)
    """
    resp, error = _fetch_export(config, token, card_id, "csv")
    if error:
        return error

    # Try parsing as CSV
    text = resp.text
    # Strip any BOM
    if text.startswith("\ufeff"):
        text = text[1:]

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    row_count = len(rows)

    if row_count == 0:
        return (0, "EMPTY (0 rows)")

    # Validate we can read at least one column
    if not reader.fieldnames or len(reader.fieldnames) == 0:
        return (0, "NO COLUMNS")

    return (row_count, f"OK ({row_count} rows, {len(reader.fieldnames)} cols)")


def _validate_xlsx_export(
    config: dict,
    token: str,
    card_id: int,
    card_name: str,
) -> tuple[int, str]:
    """Download XLSX export and validate it's non-empty.

    Returns:
        (byte_size, status_message)
    """
    resp, error = _fetch_export(config, token, card_id, "xlsx")
    if error:
        return error

    content = resp.content
    size_kb = len(content) / 1024

    if len(content) < 100:
        return (0, f"TOO SMALL ({size_kb:.1f} KB)")

    # Validate it looks like an XLSX (PK zip header)
    is_xlsx = content[:2] == b"PK"
    if not is_xlsx:
        return (0, f"BAD FORMAT (no PK header, {size_kb:.1f} KB)")

    return (int(len(content)), f"OK ({size_kb:.1f} KB)")


# ─── Reporte ────────────────────────────────────────────────

def _print_header():
    """Print report header."""
    print("=" * 100)
    print(f"{'Card Name':<40} {'CSV Rows':<12} {'XLSX Size':<12} {'Status':<15}")
    print("=" * 100)


def _print_row(name: str, csv_result: tuple, xlsx_result: tuple) -> bool:
    """Print a single card result. Returns True if both exports OK."""
    csv_rows, csv_status = csv_result
    xlsx_size, xlsx_status = xlsx_result

    # Determine overall status
    csv_ok = csv_rows > 0 and csv_status.startswith("OK")
    xlsx_ok = xlsx_size > 0 and xlsx_status.startswith("OK")
    all_ok = csv_ok and xlsx_ok

    csv_display = str(csv_rows) if csv_ok else csv_status
    xlsx_display = xlsx_status if not xlsx_ok else f"{xlsx_size / 1024:.1f} KB"
    status = "✅ PASS" if all_ok else "❌ FAIL"

    print(f"{name:<40} {csv_display:<12} {xlsx_display:<12} {status:<15}")
    return all_ok


def _print_summary(all_passing: bool, total: int, passed: int):
    """Print summary line."""
    print("=" * 100)
    print(f"Exports: {passed}/{total} passed")
    if all_passing:
        print("✅ ALL EXPORTS VALID")
    else:
        print("❌ SOME EXPORTS FAILED")
    print()


# ─── Main ───────────────────────────────────────────────────

def main():
    config = _load_config()
    token = _auth(config)

    # Get all cards
    cards = _get_cards(config, token)

    # Filter to only "question" type cards (not models, metrics, etc.)
    questions = [c for c in cards if c.get("dataset") is not True]

    if not questions:
        print("ERROR: No questions (saved queries) found in Metabase.", file=sys.stderr)
        sys.exit(1)

    _print_header()
    all_passing = True
    passed = 0
    total = len(questions)

    for card in questions:
        card_id = card["id"]
        card_name = card.get("name", f"Card #{card_id}")

        csv_result = _validate_csv_export(config, token, card_id, card_name)
        xlsx_result = _validate_xlsx_export(config, token, card_id, card_name)
        ok = _print_row(card_name, csv_result, xlsx_result)
        if ok:
            passed += 1
        else:
            all_passing = False

    _print_summary(all_passing, total, passed)

    if not all_passing:
        sys.exit(1)


if __name__ == "__main__":
    main()
