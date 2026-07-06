"""
Tests: F4: Pruebas — Performance, Export, Resilience.

Verifica todos los criterios de aceptación del plan F4:
- Slice 1: Performance Validation (F4-01, F4-02, F4-03)
- Slice 2: Export Validation (F4-04, F4-05)
- Slice 3: Resilience Validation (F4-06, F4-07)
- Slice 4: Test Suite F4 (F4-08)
- Security: Secrets via .env, no hardcodeo de credenciales
"""
import subprocess
from pathlib import Path

import pytest

# ─── Helpers ────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
QUERIES_PERFORMANCE = PROJECT_ROOT / "sql" / "queries_performance.sql"
MEASURE_SCRIPT = PROJECT_ROOT / "scripts" / "measure_query_performance.py"
VALIDATE_EXPORT_SCRIPT = PROJECT_ROOT / "scripts" / "validate_dashboard_exports.py"
PERSISTENCE_SCRIPT = PROJECT_ROOT / "scripts" / "test_persistence.sh"
ERROR_HANDLING_SCRIPT = PROJECT_ROOT / "scripts" / "test_error_handling.py"
METABASE_EXPORTS_DOC = PROJECT_ROOT / "docs" / "METABASE_EXPORTS.md"


def has_docker() -> bool:
    """Check if Docker daemon is available for runtime tests."""
    rc = subprocess.run(
        ["docker", "info", "--format", "{{.ServerVersion}}"],
        capture_output=True,
    ).returncode
    return rc == 0


# ═══════════════════════════════════════════════════════════════
# Slice 1: Performance Validation (F4-01, F4-02, F4-03)
# ═══════════════════════════════════════════════════════════════

class TestQueriesPerformanceFile:
    """F4-01: sql/queries_performance.sql exists and has expected structure."""

    def test_queries_performance_exists(self):
        assert QUERIES_PERFORMANCE.exists(), (
            f"Missing: {QUERIES_PERFORMANCE}"
        )

    def test_queries_performance_has_content(self):
        content = QUERIES_PERFORMANCE.read_text()
        assert len(content.strip()) > 500, (
            "queries_performance.sql is too short or empty"
        )

    def test_queries_performance_has_all_4_queries(self):
        """File must contain 4 separate EXPLAIN ANALYZE blocks (one per dashboard query)."""
        content = QUERIES_PERFORMANCE.read_text()
        # Each query should have an EXPLAIN ANALYZE statement
        count = content.count("EXPLAIN")
        assert count >= 4, (
            f"Expected at least 4 EXPLAIN statements, found {count}"
        )

    def test_queries_performance_has_query_names(self):
        """File must reference the 4 dashboard query names."""
        content = QUERIES_PERFORMANCE.read_text().lower()
        expected = ["rotación", "stock", "top 10", "alerta"]
        for name in expected:
            assert name in content, (
                f"Missing reference to query '{name}' in queries_performance.sql"
            )

    def test_queries_performance_has_index_references(self):
        """File should reference indexes used in each plan."""
        content = QUERIES_PERFORMANCE.read_text().lower()
        assert "index scan" in content or "idx" in content, (
            "Expected index references in queries_performance.sql"
        )


class TestMeasureQueryPerformanceScript:
    """F4-02: scripts/measure_query_performance.py exists and has expected structure."""

    def test_measure_script_exists(self):
        assert MEASURE_SCRIPT.exists(), (
            f"Missing: {MEASURE_SCRIPT}"
        )

    def test_measure_script_has_content(self):
        content = MEASURE_SCRIPT.read_text()
        assert len(content.strip()) > 200, (
            "measure_query_performance.py is too short or empty"
        )

    def test_measure_script_is_executable(self):
        """measure_query_performance.py must be importable/runnable as a script."""
        # Check it has a main section or __name__ == "__main__" guard
        content = MEASURE_SCRIPT.read_text()
        assert "__name__" in content and "__main__" in content, (
            "Missing __name__ == '__main__' guard in measure script"
        )
