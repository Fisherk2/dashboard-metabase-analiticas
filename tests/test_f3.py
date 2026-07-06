"""
Tests: F3: Interfaces — Setup Metabase vía API REST.

Verifica todos los criterios de aceptación del plan F3:
- Slice 1: Setup Reproductible vía Metabase API
- Slice 2: 3 Paneles Core (Rotación, Stock, Top 10)
- Slice 3: Panel Alertas + Metabase Pulses
- Slice 4: Test Suite F3
- Security: Secrets via .env, idempotencia, no hardcodeo
"""
import ast
import json
from pathlib import Path

import pytest

# ─── Helpers ────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
SETUP_SCRIPT = PROJECT_ROOT / "scripts" / "setup_metabase.py"
COLLECTION_JSON = PROJECT_ROOT / "metabase" / "collections" / "dashboard_ecommerce.json"
METABASE_DOCS = PROJECT_ROOT / "docs" / "METABASE_SETUP.md"
QUERIES_DASHBOARD = PROJECT_ROOT / "sql" / "queries_dashboard.sql"


# ═══════════════════════════════════════════════════════════════
# Slice 1: Setup Reproductible vía Metabase API (F3-01 a F3-04)
# ═══════════════════════════════════════════════════════════════

class TestSetupMetabaseScript:
    """F3-01: scripts/setup_metabase.py existe y define clases/métodos esperados."""

    def test_setup_script_exists(self):
        assert SETUP_SCRIPT.exists(), f"Missing: {SETUP_SCRIPT}"

    def test_setup_script_has_content(self):
        content = SETUP_SCRIPT.read_text()
        assert len(content.strip()) > 0, "setup_metabase.py is empty"

    def test_setup_has_metabase_setup_class(self):
        """El script define la clase MetabaseSetup."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        has_class = any(
            isinstance(node, ast.ClassDef) and node.name == "MetabaseSetup"
            for node in ast.walk(tree)
        )
        assert has_class, "Missing 'MetabaseSetup' class in setup_metabase.py"

    def test_setup_has_authenticate_method(self):
        """MetabaseSetup define el método authenticate()."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MetabaseSetup":
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                assert "authenticate" in methods, (
                    f"Missing 'authenticate' method. Found: {methods}"
                )

    def test_setup_has_create_database_connection_method(self):
        """MetabaseSetup define el método create_database_connection()."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MetabaseSetup":
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                assert "create_database_connection" in methods, (
                    f"Missing 'create_database_connection' method. Found: {methods}"
                )

    def test_setup_has_main_function(self):
        """El script define una función main() en el módulo."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        has_main = any(
            isinstance(node, ast.FunctionDef) and node.name == "main"
            for node in ast.walk(tree)
        )
        assert has_main, "Missing 'main()' function in setup_metabase.py"

    def test_setup_has_argument_parser(self):
        """El script usa argparse."""
        source = SETUP_SCRIPT.read_text()
        assert "argparse" in source, "setup_metabase.py should use argparse"
        assert "ArgumentParser" in source, "setup_metabase.py should use ArgumentParser"

    def test_setup_has_dotenv(self):
        """El script carga variables de entorno con python-dotenv."""
        source = SETUP_SCRIPT.read_text()
        assert "load_dotenv" in source, "setup_metabase.py should use load_dotenv"

    def test_setup_uses_requests_library(self):
        """El script usa la librería requests para llamadas HTTP."""
        source = SETUP_SCRIPT.read_text()
        assert "import requests" in source, "setup_metabase.py should import requests"

    @pytest.mark.parametrize("arg", ["--db-only", "--questions", "--dashboard", "--full"])
    def test_setup_has_expected_argparse_arg(self, arg: str):
        """El argparse soporta los flags esperados del plan F3."""
        source = SETUP_SCRIPT.read_text()
        assert arg in source, f"Missing argparse argument: {arg}"

    def test_setup_has_create_question_method(self):
        """MetabaseSetup define create_question()."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MetabaseSetup":
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                assert "create_question" in methods, (
                    f"Missing 'create_question' method. Found: {methods}"
                )

    def test_setup_has_create_dashboard_method(self):
        """MetabaseSetup define create_dashboard() y add_card_to_dashboard()."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MetabaseSetup":
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                assert "create_dashboard" in methods, (
                    f"Missing 'create_dashboard' method. Found: {methods}"
                )

    def test_setup_has_add_card_to_dashboard_method(self):
        """MetabaseSetup define add_card_to_dashboard()."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MetabaseSetup":
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                assert "add_card_to_dashboard" in methods, (
                    f"Missing 'add_card_to_dashboard' method. Found: {methods}"
                )

    def test_setup_has_create_pulse_method(self):
        """MetabaseSetup define create_pulse()."""
        source = SETUP_SCRIPT.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MetabaseSetup":
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                assert "create_pulse" in methods, (
                    f"Missing 'create_pulse' method. Found: {methods}"
                )


class TestCollectionExport:
    """F3-03/F3-11: metabase/collections/dashboard_ecommerce.json existe y es válido."""

    def test_collection_json_exists(self):
        assert COLLECTION_JSON.exists(), f"Missing: {COLLECTION_JSON}"

    def test_collection_json_is_valid(self):
        content = COLLECTION_JSON.read_text()
        parsed = json.loads(content)
        assert isinstance(parsed, (dict, list)), "JSON should be an object or array"


class TestMetabaseDocs:
    """F3-12: docs/METABASE_SETUP.md existe."""

    def test_metabase_docs_exists(self):
        assert METABASE_DOCS.exists(), f"Missing: {METABASE_DOCS}"

    def test_metabase_docs_has_content(self):
        content = METABASE_DOCS.read_text()
        assert len(content.strip()) > 0, "METABASE_SETUP.md is empty"


class TestQueriesDashboard:
    """F3-08: sql/queries_dashboard.sql existe con EXPLAIN ANALYZE."""

    def test_queries_dashboard_exists(self):
        assert QUERIES_DASHBOARD.exists(), f"Missing: {QUERIES_DASHBOARD}"

    def test_queries_dashboard_has_explain_analyze(self):
        content = QUERIES_DASHBOARD.read_text()
        assert "EXPLAIN ANALYZE" in content, "Dashboard queries file should contain EXPLAIN ANALYZE"

    def test_queries_dashboard_uses_materialized_views(self):
        """Las queries deben usar mv_*, no tablas base."""
        content = QUERIES_DASHBOARD.read_text()
        mv_count = content.count("mv_")
        assert mv_count >= 4, (
            f"Expected >=4 references to materialized views, found {mv_count}"
        )

    def test_queries_dashboard_has_execution_times(self):
        """El archivo documenta tiempos de ejecución."""
        content = QUERIES_DASHBOARD.read_text()
        has_ms = "ms" in content
        has_seconds = "seconds" in content.lower() or "sec" in content.lower()
        assert has_ms or has_seconds, "Missing execution time documentation"


# ═══════════════════════════════════════════════════════════════
# Runtime Tests (requieren Docker + Metabase funcionando)
# ═══════════════════════════════════════════════════════════════

class TestMetabaseApiRuntime:
    """F3-01 runtime: Metabase API está operativa."""

    @pytest.mark.runtime
    @pytest.mark.timeout(30)
    def test_metabase_api_health(self, run_cmd):
        """El endpoint /api/health respon OK."""
        rc, stdout, _ = run_cmd(
            "curl -sf http://localhost:3000/api/health 2>&1"
        )
        assert rc == 0, "Metabase /api/health failed"
        assert "\"ok\"" in stdout or "ok" in stdout.lower(), (
            f"/api/health should return ok: {stdout[:200]}"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(60)
    def test_setup_db_connection_works(self, run_cmd):
        """El script setup_metabase.py con --db-only configura la conexión sin errores."""
        rc, stdout, stderr = run_cmd(
            "python scripts/setup_metabase.py --db-only",
            timeout=60
        )
        output = stdout + stderr
        assert rc == 0, (
            f"setup_metabase.py --db-only failed:\n{output[:500]}"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(60)
    def test_setup_idempotent(self, run_cmd):
        """Ejecutar setup_metabase.py --db-only dos veces no duplica conexión."""
        # First run
        rc1, _, stderr1 = run_cmd(
            "python scripts/setup_metabase.py --db-only",
            timeout=60
        )
        # Second run
        rc2, stdout2, stderr2 = run_cmd(
            "python scripts/setup_metabase.py --db-only",
            timeout=60
        )
        output2 = stdout2 + stderr2
        assert rc1 == 0 and rc2 == 0, (
            f"Idempotent run failed:\n{output2[:500]}"
        )
        # Should not show error about duplicate
        assert "already exists" in output2.lower() or "skipping" in output2.lower() or "idempotent" in output2.lower(), (
            f"Idempotency message expected:\n{output2[:500]}"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(60)
    def test_setup_questions_works(self, run_cmd):
        """El script crea 4 questions sin errores."""
        rc, stdout, stderr = run_cmd(
            "python scripts/setup_metabase.py --questions",
            timeout=60
        )
        output = stdout + stderr
        assert rc == 0, (
            f"setup_metabase.py --questions failed:\n{output[:500]}"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(60)
    def test_setup_dashboard_works(self, run_cmd):
        """El script crea dashboard + cards sin errores."""
        rc, stdout, stderr = run_cmd(
            "python scripts/setup_metabase.py --dashboard",
            timeout=60
        )
        output = stdout + stderr
        assert rc == 0, (
            f"setup_metabase.py --dashboard failed:\n{output[:500]}"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(60)
    def test_setup_full_works(self, run_cmd):
        """El script con --full ejecuta todos los pasos sin errores."""
        rc, stdout, stderr = run_cmd(
            "python scripts/setup_metabase.py --full",
            timeout=120
        )
        output = stdout + stderr
        assert rc == 0, (
            f"setup_metabase.py --full failed:\n{output[:500]}"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(30)
    def test_collection_json_generated(self):
        """Después del setup, el JSON de colección debe existir y ser válido."""
        assert COLLECTION_JSON.exists(), (
            "collection JSON not found after setup"
        )
        content = COLLECTION_JSON.read_text()
        parsed = json.loads(content)
        assert isinstance(parsed, (dict, list))

    @pytest.mark.runtime
    @pytest.mark.timeout(30)
    def test_collection_json_has_cards(self, run_cmd):
        """La colección exportada contiene entries de cards (questions)."""
        content = COLLECTION_JSON.read_text()
        data = json.loads(content)
        # The export structure varies by Metabase version; check for card-like keys
        json_str = json.dumps(data).lower()
        assert any(kw in json_str for kw in ["card", "question"]), (
            "Collection JSON should contain card/question entries"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(30)
    def test_collection_json_has_dashboard(self, run_cmd):
        """La colección exportada contiene entries de dashboard."""
        content = COLLECTION_JSON.read_text()
        data = json.loads(content)
        json_str = json.dumps(data).lower()
        assert "dashboard" in json_str, (
            "Collection JSON should contain dashboard entries"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(30)
    def test_create_indexes_script_exists(self, run_cmd):
        """El script refresh_materialized_views.sql existe para refrescar MVs."""
        rc, _, _ = run_cmd("test -f scripts/refresh_materialized_views.sql")
        assert rc == 0, "scripts/refresh_materialized_views.sql not found"

    @pytest.mark.runtime
    @pytest.mark.timeout(30)
    def test_mv_refresh_works(self, run_cmd):
        """make mv-refresh funciona sin errores."""
        rc, stdout, stderr = run_cmd(
            "make mv-refresh",
            timeout=30
        )
        output = stdout + stderr
        assert rc == 0, f"make mv-refresh failed:\n{output[:300]}"
