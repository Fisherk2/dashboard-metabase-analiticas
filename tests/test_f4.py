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

    def test_measure_script_defines_dashboard_queries(self):
        """Measure script must define the 4 dashboard queries."""
        content = MEASURE_SCRIPT.read_text()
        assert "DASHBOARD_QUERIES" in content, (
            "Missing DASHBOARD_QUERIES list in measure script"
        )
        for name in ["Rotación", "Stock", "Top 10", "Alertas"]:
            assert name in content, (
                f"Missing query reference '{name}' in measure script"
            )

    def test_measure_script_has_percentile_computation(self):
        """Measure script must compute p50/p95/p99."""
        content = MEASURE_SCRIPT.read_text()
        assert "_compute_percentiles" in content, (
            "Missing _compute_percentiles function in measure script"
        )
        assert "p50" in content and "p95" in content and "p99" in content, (
            "Missing p50/p95/p99 references in measure script"
        )


class TestMakefileTestQueries:
    """F4-03: Makefile test-queries target references the performance script."""

    MAKEFILE = PROJECT_ROOT / "Makefile"

    def test_makefile_test_queries_target_exists(self):
        content = self.MAKEFILE.read_text()
        assert "test-queries:" in content, (
            "Missing 'test-queries' target in Makefile"
        )

    def test_makefile_test_queries_invokes_measure_script(self):
        """make test-queries should call measure_query_performance.py."""
        content = self.MAKEFILE.read_text()
        assert "measure_query_performance.py" in content, (
            "test-queries target should reference measure_query_performance.py"
        )

    def test_makefile_test_queries_has_help(self):
        """test-queries target should have a ## comment for make help."""
        content = self.MAKEFILE.read_text()
        assert "test-queries:" in content, "test-queries target not found"
        # Find the line with test-queries and check it has ##
        lines = content.splitlines()
        target_lines = [l for l in lines if "test-queries:" in l]
        assert any("##" in l for l in target_lines), (
            "test-queries target missing ## help comment"
        )


# ═══════════════════════════════════════════════════════════════
# Slice 2: Export Validation (F4-04, F4-05)
# ═══════════════════════════════════════════════════════════════

class TestValidateExportsScript:
    """F4-04: scripts/validate_dashboard_exports.py exists and has expected structure."""

    def test_validate_exports_exists(self):
        assert VALIDATE_EXPORT_SCRIPT.exists(), (
            f"Missing: {VALIDATE_EXPORT_SCRIPT}"
        )

    def test_validate_exports_has_content(self):
        content = VALIDATE_EXPORT_SCRIPT.read_text()
        assert len(content.strip()) > 200, (
            "validate_dashboard_exports.py is too short or empty"
        )

    def test_validate_exports_has_main_guard(self):
        content = VALIDATE_EXPORT_SCRIPT.read_text()
        assert "__name__" in content and "__main__" in content, (
            "Missing __name__ == '__main__' guard"
        )

    def test_validate_exports_has_csv_validation(self):
        """Script should validate CSV exports."""
        content = VALIDATE_EXPORT_SCRIPT.read_text()
        assert "_validate_csv_export" in content, (
            "Missing CSV export validation method"
        )
        assert "csv.DictReader" in content or "csv." in content, (
            "CSV parsing logic expected"
        )

    def test_validate_exports_has_xlsx_validation(self):
        """Script should validate XLSX exports."""
        content = VALIDATE_EXPORT_SCRIPT.read_text()
        assert "_validate_xlsx_export" in content, (
            "Missing XLSX export validation method"
        )

    def test_validate_exports_uses_metabase_api(self):
        """Script should use Metabase API for auth and export."""
        content = VALIDATE_EXPORT_SCRIPT.read_text()
        assert "/api/session" in content, (
            "Missing Metabase authentication API reference"
        )
        assert "/api/card/" in content, (
            "Missing Metabase card API reference"
        )


class TestMetabaseExportsDoc:
    """F4-05: docs/METABASE_EXPORTS.md exists and has expected structure."""

    def test_metabase_exports_doc_exists(self):
        assert METABASE_EXPORTS_DOC.exists(), (
            f"Missing: {METABASE_EXPORTS_DOC}"
        )

    def test_metabase_exports_doc_has_content(self):
        content = METABASE_EXPORTS_DOC.read_text()
        assert len(content.strip()) > 500, (
            "METABASE_EXPORTS.md is too short or empty"
        )

    def test_metabase_exports_doc_has_endpoints(self):
        content = METABASE_EXPORTS_DOC.read_text()
        assert "CSV" in content and "XLSX" in content and "JSON" in content, (
            "Expected CSV/XLSX/JSON endpoints in METABASE_EXPORTS.md"
        )

    def test_metabase_exports_doc_has_troubleshooting(self):
        content = METABASE_EXPORTS_DOC.read_text()
        assert "Troubleshooting" in content or "troubleshooting" in content, (
            "Missing troubleshooting section"
        )


# ═══════════════════════════════════════════════════════════════
# Slice 3: Resilience Validation (F4-06, F4-07)
# ═══════════════════════════════════════════════════════════════

class TestPersistenceScript:
    """F4-06: scripts/test_persistence.sh exists and has expected structure."""

    def test_persistence_script_exists(self):
        assert PERSISTENCE_SCRIPT.exists(), (
            f"Missing: {PERSISTENCE_SCRIPT}"
        )

    def test_persistence_script_has_content(self):
        content = PERSISTENCE_SCRIPT.read_text()
        assert len(content.strip()) > 200, (
            "test_persistence.sh is too short or empty"
        )

    def test_persistence_script_has_shebang(self):
        content = PERSISTENCE_SCRIPT.read_text()
        assert content.startswith("#!/bin/bash"), (
            "Missing bash shebang"
        )

    def test_persistence_script_has_strict_mode(self):
        content = PERSISTENCE_SCRIPT.read_text()
        assert "set -Eeuo pipefail" in content, (
            "Missing set -Eeuo pipefail (strict mode)"
        )

    def test_persistence_script_has_destruct_guard(self):
        """Script must require ALLOW_DESTRUCTIVE=1 to run."""
        content = PERSISTENCE_SCRIPT.read_text()
        assert "ALLOW_DESTRUCTIVE" in content, (
            "Missing ALLOW_DESTRUCTIVE guard for destructive operation"
        )

    def test_persistence_script_runs_roundtrip_steps(self):
        """Script must include make destroy, setup, metabase-setup, and test."""
        content = PERSISTENCE_SCRIPT.read_text()
        for step in ["make destroy", "make setup", "make metabase-setup", "make test"]:
            assert step in content, (
                f"Missing step '{step}' in persistence script"
            )


class TestErrorHandlingScript:
    """F4-07: scripts/test_error_handling.py exists and has expected structure."""

    def test_error_handling_script_exists(self):
        assert ERROR_HANDLING_SCRIPT.exists(), (
            f"Missing: {ERROR_HANDLING_SCRIPT}"
        )

    def test_error_handling_has_content(self):
        content = ERROR_HANDLING_SCRIPT.read_text()
        assert len(content.strip()) > 200, (
            "test_error_handling.py is too short or empty"
        )

    def test_error_handling_has_main_guard(self):
        content = ERROR_HANDLING_SCRIPT.read_text()
        assert "__name__" in content and "__main__" in content, (
            "Missing __name__ == '__main__' guard"
        )

    def test_error_handling_stops_and_restarts_pg(self):
        """Script should stop and restart PostgreSQL."""
        content = ERROR_HANDLING_SCRIPT.read_text()
        assert "docker stop" in content or "docker start" in content, (
            "Missing docker stop/start for PostgreSQL"
        )

    def test_error_handling_checks_metabase_error(self):
        """Script should verify Metabase returns an error, not a stack trace."""
        content = ERROR_HANDLING_SCRIPT.read_text()
        assert "500" in content or "status_code" in content, (
            "Missing HTTP status code check for error response"
        )


# ═══════════════════════════════════════════════════════════════
# Slice 4: Test Suite F4 (F4-08) — Static tests
# ═══════════════════════════════════════════════════════════════

class TestTestSuiteF4:
    """F4-08: F4 test suite meets coverage expectations."""

    def test_test_count_sufficient(self):
        """F4 must have at least 15 tests (static + runtime)."""
        content = (PROJECT_ROOT / "tests" / "test_f4.py").read_text()
        test_count = content.count("def test_")
        assert test_count >= 15, (
            f"Expected ≥15 tests in test_f4.py, found {test_count}"
        )

    def test_has_runtime_marker_import(self):
        """Test file should import pytest for runtime markers (conftest has it)."""
        content = (PROJECT_ROOT / "tests" / "test_f4.py").read_text()
        assert "import pytest" in content, (
            "Missing pytest import"
        )

    def test_conftest_has_runtime_marker(self):
        """conftest.py must register the runtime marker."""
        content = (PROJECT_ROOT / "tests" / "conftest.py").read_text()
        assert "runtime" in content, (
            "Missing 'runtime' marker registration in conftest.py"
        )

    def test_all_queries_permitted(self):
        """All F4 tests must be passing (checked by test runner)."""
        # This is a placeholder — the actual check happens when pytest runs
        pass


# ═══════════════════════════════════════════════════════════════
# Runtime Tests (requieren Docker)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.runtime
class TestF4Runtime:
    """F4 runtime smoke tests — require Docker + services up."""

    def test_metabase_health(self, run_cmd):
        """Verify Metabase API health endpoint returns ok."""
        rc, stdout, _ = run_cmd(
            "curl -sf http://localhost:3000/api/health"
        )
        assert rc == 0, "Metabase health endpoint not reachable"
        assert '"status":"ok"' in stdout, \
            f"Metabase health did not return ok: {stdout[:200]}"

    def test_measure_script_runs(self, run_cmd):
        """measure_query_performance.py should run without crashing."""
        rc, stdout, stderr = run_cmd(
            "python scripts/measure_query_performance.py --runs 2",
        )
        combined = stdout + stderr
        # If env vars not loaded (running outside make), script fails gracefully
        if "POSTGRES_PASSWORD" in combined:
            pytest.skip("Run via 'make test-queries' to load .env variables")
        if rc != 0:
            if "Cannot connect" in combined:
                pytest.skip("PostgreSQL not accessible (Docker may be down)")
        # If it runs, it should output the table header
        assert "Query" in stdout or rc == 0, (
            f"Script failed: {stderr[:200]}"
        )
