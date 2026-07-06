#!/usr/bin/env python3
"""
setup_metabase.py — Metabase REST API setup for Dashboard E-commerce Analytics.

Configures Metabase programmatically:
  1. Authenticate with Metabase (POST /api/session)
  2. Create PostgreSQL database connection (POST /api/database)
  3. Create 4 saved SQL "Questions" (POST /api/card)
  4. Create Dashboard with 4 cards (POST /api/dashboard + /api/dashboard/:id/cards)
  5. Create 2 Metabase Pulses for alerts (POST /api/pulse)

All operations are idempotent: re-running does not duplicate resources.

Source: https://www.metabase.com/docs/latest/api
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

# ─── Constants ────────────────────────────────────────────────
METABASE_URL = "http://localhost:3000"
POSTGRES_HOST = "postgres"
POSTGRES_PORT = 5432

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
COLLECTION_DIR = PROJECT_ROOT / "metabase" / "collections"
COLLECTION_JSON = COLLECTION_DIR / "dashboard_ecommerce.json"

# Question definitions: (name, sql, display_type)
QUESTIONS = [
    {
        "name": "Rotación por Categoría",
        "sql": (
            "SELECT categoria, mes, anio, ventas_totales, ingresos_totales, "
            "productos_vendidos "
            "FROM mv_rotacion_mensual "
            "WHERE anio = {{anio}} AND mes = {{mes}} "
            "ORDER BY ventas_totales DESC"
        ),
        "display": "bar",
        "description": "Ventas e ingresos por categoría de producto a lo largo del tiempo.",
    },
    {
        "name": "Stock Actual vs Mínimo",
        "sql": (
            "SELECT producto_id, nombre, categoria, proveedor, "
            "stock_actual, stock_minimo, estado "
            "FROM mv_stock_actual "
            "WHERE estado IN ('ALERTA', 'PRECAUCION') "
            "ORDER BY stock_actual ASC"
        ),
        "display": "table",
        "description": "Alertas de stock mínimo y estado de inventario por producto.",
    },
    {
        "name": "Top 10 Productos por Ventas",
        "sql": (
            "SELECT producto_id, nombre, categoria, "
            "unidades_vendidas, ingresos_totales, numero_ventas "
            "FROM mv_top_productos "
            "ORDER BY ingresos_totales DESC "
            "LIMIT 10"
        ),
        "display": "row",
        "description": "Los 10 productos con mayores ingresos del período.",
    },
    {
        "name": "Alertas de Stock Mínimo",
        "sql": (
            "SELECT p.id, p.nombre, p.stock_actual, p.stock_minimo, "
            "pr.nombre AS proveedor, pr.email AS contacto_proveedor "
            "FROM productos p "
            "JOIN proveedores pr ON p.proveedor_id = pr.id "
            "WHERE p.stock_actual <= p.stock_minimo * {{umbral_multiplier}} "
            "ORDER BY p.stock_actual ASC"
        ),
        "display": "table",
        "description": "Productos con stock por debajo del umbral configurable.",
    },
]

# Pulse definitions
PULSES = [
    {
        "name": "Alerta Stock Crítico",
        "schedule_hour": 9,
        "schedule_day": "mon,tue,wed,thu,fri",
        "card_index": 3,  # Alertas de Stock Mínimo
    },
    {
        "name": "Resumen Ventas Diarias",
        "schedule_hour": 18,
        "schedule_day": "mon,tue,wed,thu,fri",
        "card_index": 2,  # Top 10 Productos
    },
]

# ─── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("metabase-setup")


# ═══════════════════════════════════════════════════════════════
# Metabase API Client
# ═══════════════════════════════════════════════════════════════

class MetabaseSetupError(Exception):
    """Base exception for Metabase setup errors."""
    pass


class MetabaseAuthError(MetabaseSetupError):
    """Raised when authentication with Metabase fails."""
    pass


class MetabaseApiError(MetabaseSetupError):
    """Raised when a Metabase API call returns an unexpected status."""
    def __init__(self, endpoint: str, status: int, detail: str = ""):
        self.endpoint = endpoint
        self.status = status
        self.detail = detail
        super().__init__(f"API {endpoint}: HTTP {status} — {detail[:200]}")


class MetabaseSetup:
    """Client for configuring Metabase via its REST API.

    Encapsulates authentication, resource creation (databases, questions,
    dashboards, pulses), and collection export. All methods are idempotent.

    Source: https://www.metabase.com/docs/latest/api
    """

    def __init__(self, base_url: str = METABASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session_token: Optional[str] = None
        self._headers: dict[str, str] = {"Content-Type": "application/json"}

    # ── Authentication & Setup ──────────────────────────────
    # Source: GET /api/session/properties, POST /api/setup, POST /api/session

    def _check_setup_state(self) -> tuple[str, bool]:
        """Check if Metabase has been initialized (first-time setup).

        GET /api/session/properties.
        Returns (setup_token, has_user_setup).
        - If not set up: (token_str, False) where token_str is the setup token
        - If set up: (None, True)
        """
        response = requests.get(
            f"{self.base_url}/api/session/properties",
            timeout=10,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                "GET /api/session/properties",
                response.status_code,
                response.text,
            )
        props = response.json()
        token = props.get("setup-token")
        has_user = props.get("has-user-setup", False)
        return token, bool(has_user)

    def _perform_initial_setup(
        self, username: str, password: str
    ) -> str:
        """Complete Metabase first-time setup.

        POST /api/setup with setup token + admin user.
        Creates the admin user and returns the session token.
        """
        token, has_user = self._check_setup_state()
        if has_user:
            log.info("Metabase already set up — skipping initial setup")
            return self._authenticate(username, password)

        if not token:
            raise MetabaseSetupError(
                "No setup token available and no user configured. "
                "Check Metabase state."
            )

        payload = {
            "token": token,
            "user": {
                "first_name": "Admin",
                "last_name": "User",
                "email": username,
                "password": password,
            },
            "prefs": {
                "site_name": "E-commerce Analytics",
                "allow_tracking": False,
            },
            "database": None,
            "invite": None,
        }
        response = requests.post(
            f"{self.base_url}/api/setup",
            json=payload,
            timeout=15,
        )
        if response.status_code not in (200, 201):
            raise MetabaseSetupError(
                f"Initial setup failed (HTTP {response.status_code}): "
                f"{response.text[:300]}"
            )
        data = response.json()
        self.session_token = data.get("id", "")
        self._headers["X-Metabase-Session"] = self.session_token
        log.info("Metabase initial setup complete — admin user created")
        return self.session_token

    def _authenticate(self, username: str, password: str) -> str:
        """Authenticate with existing Metabase credentials.

        POST /api/session with {username, password}.
        Raises MetabaseAuthError if credentials are invalid.
        """
        response = requests.post(
            f"{self.base_url}/api/session",
            json={"username": username, "password": password},
            timeout=10,
        )
        if response.status_code != 200:
            raise MetabaseAuthError(
                f"Authentication failed (HTTP {response.status_code}): "
                f"{response.text[:200]}"
            )
        data = response.json()
        self.session_token = data["id"]
        self._headers["X-Metabase-Session"] = self.session_token
        log.info("Authenticated with Metabase as %s", username)
        return self.session_token

    def authenticate(self, username: str, password: str) -> str:
        """Authenticate with Metabase, handling initial setup if needed.

        First checks if Metabase has been set up.
        If not, performs initial setup via POST /api/setup.
        Otherwise, authenticates via POST /api/session.

        Returns session token string.
        """
        _, has_user = self._check_setup_state()
        if not has_user:
            return self._perform_initial_setup(username, password)
        return self._authenticate(username, password)

    # ── Database Connection ─────────────────────────────────
    # Source: GET /api/database, POST /api/database

    def _get_databases(self) -> list[dict[str, Any]]:
        """Return list of configured database connections."""
        response = requests.get(
            f"{self.base_url}/api/database",
            headers=self._headers,
            timeout=10,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                "GET /api/database", response.status_code, response.text
            )
        return response.json().get("data", [])

    def _db_name_exists(self, name: str) -> bool:
        """Check if a database with given name already exists (idempotency)."""
        dbs = self._get_databases()
        return any(db.get("name") == name for db in dbs)

    def create_database_connection(
        self,
        name: str = "E-commerce Analytics",
        host: str = POSTGRES_HOST,
        port: int = POSTGRES_PORT,
        dbname: str = "",
        user: str = "",
        password: str = "",
    ) -> dict[str, Any]:
        """Create a PostgreSQL database connection in Metabase.

        If a database with the same name already exists, skips creation
        and logs the existing connection (idempotent).

        POST /api/database with connection details.
        Returns the database resource dict.
        """
        if self._db_name_exists(name):
            log.info("Database '%s' already exists — skipping (idempotent)", name)
            dbs = self._get_databases()
            return next(db for db in dbs if db.get("name") == name)

        payload = {
            "engine": "postgres",
            "name": name,
            "details": {
                "host": host,
                "port": port,
                "dbname": dbname,
                "user": user,
                "password": password,
                "ssl": False,
                "tunnel_enabled": False,
            },
            "is_full_sync": True,
        }
        response = requests.post(
            f"{self.base_url}/api/database",
            headers=self._headers,
            json=payload,
            timeout=15,
        )
        if response.status_code not in (200, 201):
            raise MetabaseApiError(
                "POST /api/database", response.status_code, response.text
            )
        db = response.json()
        log.info("Database connection '%s' created (id=%s)", name, db.get("id"))
        return db

    # ── Questions (Saved SQL Queries) ───────────────────────
    # Source: GET /api/card, POST /api/card

    def _get_questions(self) -> list[dict[str, Any]]:
        """Return list of saved questions."""
        response = requests.get(
            f"{self.base_url}/api/card",
            headers=self._headers,
            timeout=10,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                "GET /api/card", response.status_code, response.text
            )
        data = response.json()
        # GET /api/card returns a list directly (not wrapped in {"data": [...]})
        if isinstance(data, list):
            return data
        return data.get("data", [])

    def _question_name_exists(self, name: str) -> bool:
        """Check if a question with given name already exists."""
        questions = self._get_questions()
        return any(q.get("name") == name for q in questions)

    def _get_first_database_id(self) -> int:
        """Return the ID of the first (and expected only) database connection."""
        dbs = self._get_databases()
        if not dbs:
            raise MetabaseSetupError(
                "No database connections configured. Run --db-only first."
            )
        return dbs[0]["id"]

    def create_question(
        self,
        name: str,
        sql: str,
        display: str = "table",
        description: str = "",
    ) -> dict[str, Any]:
        """Create a saved SQL question.

        If a question with the same name already exists, skips creation
        (idempotent).

        POST /api/card with dataset_query containing the native SQL.
        Returns the card resource dict.
        """
        if self._question_name_exists(name):
            log.info("Question '%s' already exists — skipping (idempotent)", name)
            questions = self._get_questions()
            return next(q for q in questions if q.get("name") == name)

        db_id = self._get_first_database_id()
        payload = {
            "name": name,
            "description": description,
            "display": display,
            "dataset_query": {
                "type": "native",
                "native": {
                    "query": sql,
                    "template_tags": {},
                },
                "database": db_id,
            },
            "visualization_settings": {},
            "collection_position": None,
        }
        response = requests.post(
            f"{self.base_url}/api/card",
            headers=self._headers,
            json=payload,
            timeout=15,
        )
        if response.status_code not in (200, 201):
            raise MetabaseApiError(
                "POST /api/card", response.status_code, response.text
            )
        card = response.json()
        log.info("Question '%s' created (id=%s)", name, card.get("id"))
        return card

    def create_all_questions(self) -> list[dict[str, Any]]:
        """Create all 4 dashboard questions defined in QUESTIONS constant.

        Returns list of created/existing card dicts.
        """
        cards = []
        for q_def in QUESTIONS:
            card = self.create_question(
                name=q_def["name"],
                sql=q_def["sql"],
                display=q_def["display"],
                description=q_def.get("description", ""),
            )
            cards.append(card)
        log.info("Total questions: %d", len(cards))
        return cards

    # ── Dashboard + Cards ───────────────────────────────────
    # Source: GET /api/dashboard, POST /api/dashboard,
    #         POST /api/dashboard/:id/cards

    def _get_dashboards(self) -> list[dict[str, Any]]:
        """Return list of dashboards."""
        response = requests.get(
            f"{self.base_url}/api/dashboard",
            headers=self._headers,
            timeout=10,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                "GET /api/dashboard", response.status_code, response.text
            )
        data = response.json()
        if isinstance(data, list):
            return data
        return data.get("data", [])

    def _dashboard_name_exists(self, name: str) -> bool:
        """Check if a dashboard with given name already exists."""
        dashboards = self._get_dashboards()
        return any(d.get("name") == name for d in dashboards)

    def create_dashboard(
        self,
        name: str = "E-commerce Analytics",
        description: str = "Dashboard analítico de e-commerce: rotación, stock, ventas y alertas.",
    ) -> dict[str, Any]:
        """Create a dashboard.

        If a dashboard with same name exists, returns existing one (idempotent).

        POST /api/dashboard.
        Returns the dashboard resource dict.
        """
        if self._dashboard_name_exists(name):
            log.info("Dashboard '%s' already exists — skipping (idempotent)", name)
            dashboards = self._get_dashboards()
            return next(d for d in dashboards if d.get("name") == name)

        payload = {
            "name": name,
            "description": description,
            "collection_position": None,
        }
        response = requests.post(
            f"{self.base_url}/api/dashboard",
            headers=self._headers,
            json=payload,
            timeout=15,
        )
        if response.status_code not in (200, 201):
            raise MetabaseApiError(
                "POST /api/dashboard", response.status_code, response.text
            )
        dashboard = response.json()
        log.info("Dashboard '%s' created (id=%s)", name, dashboard.get("id"))
        return dashboard

    def setup_dashboard_with_cards(self, cards: list[dict[str, Any]]) -> dict[str, Any]:
        """Create dashboard and add all cards in a 2x2 grid layout.

        First creates/reuses the dashboard via POST /api/dashboard.
        Then adds all cards via PUT /api/dashboard/{id} with temporary
        negative IDs (Metabase frontend pattern for new dashcards).

        Layout (12-column grid):
          [Card 0  ] [Card 1  ]  row 0
          [Card 2  ] [Card 3  ]  row 6

        Each card occupies 6 cols x 6 rows.
        """
        dashboard = self.create_dashboard()

        if not dashboard.get("id"):
            raise MetabaseSetupError("Dashboard creation returned no ID")

        dash_id = dashboard["id"]
        layout = [
            (0, 0, 6, 6),    # Card 0: top-left
            (0, 6, 6, 6),    # Card 1: top-right
            (6, 0, 6, 6),    # Card 2: bottom-left
            (6, 6, 6, 6),    # Card 3: bottom-right
        ]

        # Build dashcards array with temporary negative IDs
        dashcards = []
        for i, card_data in enumerate(cards[:4]):
            card_id = card_data.get("id")
            if not card_id:
                log.warning("Card at index %d has no ID — skipping", i)
                continue
            row, col, sx, sy = layout[i]
            dashcards.append({
                "id": -(i + 1),  # temporary negative ID for new dashcards
                "card_id": card_id,
                "row": row,
                "col": col,
                "size_x": sx,
                "size_y": sy,
                "series": [],
                "parameter_mappings": [],
                "visualization_settings": {},
            })

        if not dashcards:
            log.warning("No cards to add to dashboard")
            return dashboard

        # Use PUT /api/dashboard/{id} to save dashcards
        # Source: Metabase frontend uses this pattern with temp negative IDs
        payload = {
            "name": dashboard.get("name", "E-commerce Analytics"),
            "description": dashboard.get("description", ""),
            "dashcards": dashcards,
        }
        response = requests.put(
            f"{self.base_url}/api/dashboard/{dash_id}",
            headers=self._headers,
            json=payload,
            timeout=15,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                f"PUT /api/dashboard/{dash_id}",
                response.status_code,
                response.text,
            )
        updated = response.json()
        cards_added = len(updated.get("dashcards", []))
        log.info(
            "Dashboard %d updated with %d cards",
            dash_id, cards_added,
        )
        return updated

    # ── Pulses (Alerts) ─────────────────────────────────────
    # Source: POST /api/pulse

    def _get_pulses(self) -> list[dict[str, Any]]:
        """Return list of configured pulses."""
        response = requests.get(
            f"{self.base_url}/api/pulse",
            headers=self._headers,
            timeout=10,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                "GET /api/pulse", response.status_code, response.text
            )
        data = response.json()
        if isinstance(data, list):
            return data
        return data.get("data", [])

    def _pulse_name_exists(self, name: str) -> bool:
        """Check if a pulse with given name already exists."""
        pulses = self._get_pulses()
        return any(p.get("name") == name for p in pulses)

    def create_pulse(
        self,
        name: str,
        cards: list[dict[str, Any]],
        card_indices: list[int],
        schedule_hour: int = 9,
        schedule_day: str = "mon,tue,wed,thu,fri",
    ) -> dict[str, Any]:
        """Create a Metabase Pulse (alert/notification).

        If a pulse with the same name exists, skips (idempotent).

        POST /api/pulse.
        Cards are referenced by ID from the card list.
        Schedule: daily at specified hour on specified days.
        Channel: email to admin (config-only, no SMTP required).
        """
        if self._pulse_name_exists(name):
            log.info("Pulse '%s' already exists — skipping (idempotent)", name)
            pulses = self._get_pulses()
            return next(p for p in pulses if p.get("name") == name)

        pulse_cards = []
        for idx in card_indices:
            if idx < len(cards) and cards[idx].get("id"):
                pulse_cards.append({
                    "id": cards[idx]["id"],
                    "include_csv": False,
                    "include_xls": False,
                })

        if not pulse_cards:
            raise MetabaseSetupError(
                f"No valid cards to attach to pulse '{name}'"
            )

        payload = {
            "name": name,
            "cards": pulse_cards,
            "channels": [
                {
                    "channel_type": "email",
                    "details": {},
                    "schedule_type": "daily",
                    "schedule_hour": schedule_hour,
                    "schedule_day": schedule_day,
                    "schedule_frame": None,
                    "enabled": True,
                }
            ],
            "skip_if_empty": True,
            "collection_position": None,
        }
        response = requests.post(
            f"{self.base_url}/api/pulse",
            headers=self._headers,
            json=payload,
            timeout=15,
        )
        if response.status_code not in (200, 201):
            raise MetabaseApiError(
                "POST /api/pulse", response.status_code, response.text
            )
        pulse = response.json()
        log.info("Pulse '%s' created (id=%s)", name, pulse.get("id"))
        return pulse

    def create_all_pulses(self, cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Create both pulses defined in PULSES constant.

        Returns list of created/existing pulse dicts.
        """
        pulses = []
        for p_def in PULSES:
            pulse = self.create_pulse(
                name=p_def["name"],
                cards=cards,
                card_indices=[p_def["card_index"]],
                schedule_hour=p_def["schedule_hour"],
                schedule_day=p_def["schedule_day"],
            )
            pulses.append(pulse)
        log.info("Total pulses: %d", len(pulses))
        return pulses

    # ── Collection Export (Snapshot) ────────────────────────
    # Source: GET /api/collection/:id/items  + recursive

    def get_root_collection_id(self) -> int:
        """Return the ID of the root collection ('Our Analytics')."""
        response = requests.get(
            f"{self.base_url}/api/collection/root",
            headers=self._headers,
            timeout=10,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                "GET /api/collection/root", response.status_code, response.text
            )
        return response.json()["id"]

    def export_collection(self, output_path: Path) -> dict[str, Any]:
        """Export the root collection structure to a JSON file.

        Fetches the collection hierarchy and items recursively,
        saving the result to output_path.
        """
        root_id = self.get_root_collection_id()

        # Collect all items from root collection
        items_url = (
            f"{self.base_url}/api/collection/{root_id}/items"
        )
        response = requests.get(
            items_url,
            headers=self._headers,
            timeout=15,
        )
        if response.status_code != 200:
            raise MetabaseApiError(
                f"GET /api/collection/{root_id}/items",
                response.status_code,
                response.text,
            )

        data = response.json()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(
            "Collection exported to %s (%d items)",
            output_path, len(data.get("data", [])),
        )
        return data

    # ── Full Pipeline ────────────────────────────────────────

    def full_setup(self) -> dict[str, Any]:
        """Execute the complete setup pipeline.

        Returns dict with keys for each resource type.
        """
        result: dict[str, Any] = {
            "database": None,
            "questions": [],
            "dashboard": None,
            "pulses": [],
            "export": None,
        }

        # Step 1: Database connection
        dbname = os.getenv("POSTGRES_DB", "ecommerce-db")
        user = os.getenv("POSTGRES_USER", "ecommerce-fish")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        result["database"] = self.create_database_connection(
            dbname=dbname,
            user=user,
            password=password,
        )

        # Step 2: Create all questions
        result["questions"] = self.create_all_questions()

        # Step 3: Create dashboard with cards
        result["dashboard"] = self.setup_dashboard_with_cards(
            result["questions"]
        )

        # Step 4: Create pulses
        result["pulses"] = self.create_all_pulses(result["questions"])

        # Step 5: Export collection
        result["export"] = self.export_collection(COLLECTION_JSON)

        return result


# ═══════════════════════════════════════════════════════════════
# CLI Entry Point
# ═══════════════════════════════════════════════════════════════

def main():
    """Parse CLI arguments and execute setup steps.

    Flags:
      --db-only     Configure only the database connection
      --questions   Create saved SQL questions
      --dashboard   Create dashboard with cards
      --full        Execute all steps above
    """
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Setup Metabase dashboards programmatically via REST API.",
    )
    parser.add_argument(
        "--db-only",
        action="store_true",
        help="Configure only the PostgreSQL database connection in Metabase",
    )
    parser.add_argument(
        "--questions",
        action="store_true",
        help="Create saved SQL questions (queries) for dashboards",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Create dashboard with cards (requires --questions first)",
    )
    parser.add_argument(
        "--pulses",
        action="store_true",
        help="Create Metabase Pulse alerts (requires --dashboard first)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Execute complete setup: database + questions + dashboard + pulses",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Default to --full if no flags provided
    if not any([args.db_only, args.questions, args.dashboard, args.pulses, args.full]):
        args.full = True

    # Read credentials from environment
    mb_user = os.getenv("MB_USER", "admin@example.com")
    # Password must meet Metabase default requirements:
    # min 8 chars, uppercase, lowercase, digit, not too common
    mb_password = os.getenv("MB_PASSWORD", "Metabase1")
    pg_db = os.getenv("POSTGRES_DB", "ecommerce-db")
    pg_user = os.getenv("POSTGRES_USER", "ecommerce-fish")
    pg_password = os.getenv("POSTGRES_PASSWORD", "postgres")

    # Initialize client
    setup = MetabaseSetup()

    try:
        # Auth
        setup.authenticate(mb_user, mb_password)

        # Database connection
        if args.db_only or args.full:
            setup.create_database_connection(
                dbname=pg_db,
                user=pg_user,
                password=pg_password,
            )

        # Questions
        cards = []
        if args.questions or args.full:
            cards = setup.create_all_questions()

        # Dashboard
        if args.dashboard or args.full:
            if not cards and args.dashboard:
                # Need to fetch existing questions if we're only doing dashboard step
                existing = setup._get_questions()
                cards = [q for q in existing if q.get("name") in
                         [qd["name"] for qd in QUESTIONS]]
            if cards:
                setup.setup_dashboard_with_cards(cards)
            else:
                log.warning(
                    "No questions available to add to dashboard. "
                    "Run --questions first."
                )

        # Pulses
        if args.pulses or args.full:
            if not cards and args.pulses:
                existing = setup._get_questions()
                cards = [q for q in existing if q.get("name") in
                         [qd["name"] for qd in QUESTIONS]]
            if cards:
                setup.create_all_pulses(cards)
            else:
                log.warning(
                    "No questions available for pulses. "
                    "Run --questions first."
                )

        # Export collection (always at end if --full, or if any resource created)
        if args.full:
            setup.export_collection(COLLECTION_JSON)
            log.info("=" * 50)
            log.info("FULL SETUP COMPLETE")
            log.info("Dashboard: http://localhost:3000")
            log.info("=" * 50)

    except (
        MetabaseAuthError,
        MetabaseApiError,
        MetabaseSetupError,
        requests.exceptions.ConnectionError,
    ) as e:
        log.error("Setup failed: %s", e)
        sys.exit(1)
    except Exception as e:
        log.error("Unexpected error: %s", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
