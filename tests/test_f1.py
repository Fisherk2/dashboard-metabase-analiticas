"""
Tests: F1: Infraestructura — Docker Compose, PostgreSQL y Metabase.

Verifica todos los criterios de aceptación del plan F1:
- Slice 1: Compose Config Foundation (env, ports, volumes, healthcheck, network)
- Slice 2: Services Up & Healthy (Docker runtime)
- Slice 3: Integration & Resilience (persistence, port isolation)
- Security: Port isolation, secrets management
"""
import os
import subprocess
from pathlib import Path

import pytest

# ─── Constants ───────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
COMPOSE_FILE = PROJECT_ROOT / "docker" / "docker-compose.yml"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
DOCKERIGNORE = PROJECT_ROOT / ".dockerignore"
OVERRIDE_FILE = PROJECT_ROOT / "docker" / "docker-compose.override.yml"


# ─── Fixtures ────────────────────────────────────────────────
@pytest.fixture
def root() -> Path:
    """Absolute path to project root."""
    return PROJECT_ROOT


@pytest.fixture
def run_cmd():
    """Execute a shell command and return (returncode, stdout, stderr)."""
    def _run(cmd: str, **kwargs) -> tuple:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT, **kwargs
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    return _run


def dedent_yaml(text: str) -> str:
    """Remove common leading whitespace from YAML for assertion readability."""
    return "\n".join(line.lstrip() for line in text.splitlines())


# ─── Static helpers ──────────────────────────────────────────
def compose_content() -> str:
    """Return the raw text of docker-compose.yml."""
    return COMPOSE_FILE.read_text()


# ═══════════════════════════════════════════════════════════════
# Slice 1: Compose Config Foundation
# ═══════════════════════════════════════════════════════════════
class TestComposeFileExists:
    """F1-01: docker-compose.yml exists in docker/ directory."""

    def test_compose_file_exists(self):
        assert COMPOSE_FILE.exists(), "docker/docker-compose.yml not found"

    def test_compose_has_postgres(self):
        content = compose_content()
        assert "postgres:" in content, "Missing postgres service"

    def test_compose_has_metabase(self):
        content = compose_content()
        assert "metabase:" in content, "Missing metabase service"


class TestComposePostgres:
    """F1-01: PostgreSQL service configuration."""

    def test_image(self):
        content = compose_content()
        assert "postgres:15" in content, "Expected postgres:15 image"

    def test_container_name(self):
        content = compose_content()
        assert "metabase-postgres" in content, "Expected container_name metabase-postgres"

    def test_no_exposed_ports(self, run_cmd):
        """PostgreSQL must NOT expose port 5432 to host (security)."""
        rc, stdout, _ = run_cmd("docker compose -f docker/docker-compose.yml config")
        assert rc == 0, "docker compose config failed"

        lines = stdout.splitlines()
        # Find the postgres SERVICE block (not depends_on: postgres: inside metabase)
        # Config output: services: \n  metabase: ... \n  postgres: \n ...
        pg_start = None
        for i, line in enumerate(lines):
            # Service postgres is at 2-space indent; depends_on postgres at deeper indent
            if line.strip() == "postgres:" and not line.startswith("    "):
                pg_start = i
                break
        assert pg_start is not None, "postgres service not found in config"

        # Scan lines after postgres: until next top-level non-space key
        pg_block = []
        for line in lines[pg_start + 1:]:
            if line and not line.startswith(" ") and ":" in line:
                break  # next top-level key (networks:, volumes:)
            pg_block.append(line)

        block_text = "\n".join(pg_block)
        assert "ports:" not in block_text, "PostgreSQL has exposed ports in config!"

    def test_healthcheck_exists(self):
        content = compose_content()
        assert "healthcheck:" in content, "Missing healthcheck in postgres"

    def test_healthcheck_command(self):
        content = compose_content()
        assert "pg_isready" in content, "Healthcheck must use pg_isready"

    def test_volumes_named(self):
        """Use named volume pg_data, not bind mount."""
        content = compose_content()
        assert "pg_data:" in content or "pg_data/" in content, "Missing pg_data volume reference"

    def test_restart_policy(self):
        content = compose_content()
        assert "unless-stopped" in content, "Missing restart: unless-stopped"


class TestComposeMetabase:
    """F1-01: Metabase service configuration."""

    def test_image(self):
        content = compose_content()
        assert "metabase/metabase" in content, "Expected metabase/metabase image"

    def test_container_name(self):
        content = compose_content()
        assert "metabase-app" in content, "Expected container_name metabase-app"

    def test_ports_3000(self, run_cmd):
        """Metabase must expose port 3000 to host (verified via compose config)."""
        rc, stdout, _ = run_cmd("docker compose -f docker/docker-compose.yml config")
        assert rc == 0, "docker compose config failed"
        # In normalized config, target: 3000 indicates port mapping
        assert "target: 3000" in stdout, "Missing port target 3000 in Metabase config"

    def test_depends_on_postgres(self):
        content = compose_content()
        idx = content.find("metabase:")
        metabase_section = content[idx:]
        assert "postgres" in metabase_section, "Missing depends_on postgres"

    def test_depends_on_condition_healthy(self):
        content = compose_content()
        idx = content.find("metabase:")
        metabase_section = content[idx:]
        assert "service_healthy" in metabase_section, "Missing service_healthy condition"

    def test_volumes_named(self):
        """Use named volume mb_data, not bind mount."""
        content = compose_content()
        assert "mb_data:" in content or "mb_data/" in content, "Missing mb_data volume reference"

    def test_environment_has_mb_vars(self):
        content = compose_content()
        idx = content.find("metabase:")
        metabase_section = content[idx:]
        assert "MB_DB_TYPE" in metabase_section, "Missing MB_DB_TYPE env var"
        assert "MB_DB_HOST" in metabase_section, "Missing MB_DB_HOST env var"
        assert "MB_DB_PASS" in metabase_section, "Missing MB_DB_PASS env var"
        assert "MB_DB_USER" in metabase_section, "Missing MB_DB_USER env var"
        assert "MB_DB_DBNAME" in metabase_section, "Missing MB_DB_DBNAME env var"
        assert "MB_DB_PORT" in metabase_section, "Missing MB_DB_PORT env var"


class TestComposeTopLevel:
    """F1-01: Compose file top-level structure."""

    def test_volumes_section_exists(self):
        content = compose_content()
        assert "volumes:" in content, "Missing top-level volumes section"

    def test_volumes_declared(self):
        content = compose_content()
        assert "pg_data:" in content, "Missing pg_data in top-level volumes"
        assert "mb_data:" in content, "Missing mb_data in top-level volumes"

    def test_networks_section_exists(self):
        content = compose_content()
        assert "networks:" in content, "Missing top-level networks section"

    def test_network_name(self):
        content = compose_content()
        assert "ecommerce_net" in content, "Missing ecommerce_net network"

    def test_make_validate_passes(self, run_cmd):
        """make validate must exit 0."""
        rc, stdout, stderr = run_cmd("make validate")
        assert rc == 0, f"make validate failed:\nstdout: {stdout}\nstderr: {stderr}"


# ═══════════════════════════════════════════════════════════════
# Slice 1: .env.example
# ═══════════════════════════════════════════════════════════════
class TestEnvExampleExtended:
    """F1-02: .env.example has all required variables."""

    REQUIRED_VARS = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_PORT",
        "METABASE_PORT",
        "METABASE_SECRET_KEY",
        "MB_DB_TYPE",
        "MB_DB_DBNAME",
        "MB_DB_PORT",
        "MB_DB_USER",
        "MB_DB_PASS",
        "MB_DB_HOST",
        "COMPOSE_PROJECT_NAME",
        "DATA_ROWS_SALES",
        "DATA_ROWS_PRODUCTS",
    ]

    def test_env_example_exists(self):
        assert ENV_EXAMPLE.exists(), ".env.example not found"

    @pytest.mark.parametrize("var_name", REQUIRED_VARS)
    def test_required_var_present(self, var_name: str):
        """Every required variable must be defined in .env.example."""
        content = ENV_EXAMPLE.read_text()
        assert f"{var_name}=" in content, f"Missing required variable: {var_name}"

    def test_total_vars_at_least_14(self):
        content = ENV_EXAMPLE.read_text()
        count = content.count("=")
        assert count >= 14, f"Expected >= 14 variables, found {count}"

    def test_mb_db_type_is_postgres(self):
        content = ENV_EXAMPLE.read_text()
        # Must define MB_DB_TYPE with value postgres
        for line in content.splitlines():
            if line.startswith("MB_DB_TYPE"):
                assert "=postgres" in line or "=postgresql" in line, \
                    "MB_DB_TYPE should default to postgres"


# ═══════════════════════════════════════════════════════════════
# Slice 1: .dockerignore
# ═══════════════════════════════════════════════════════════════
class TestDockerignore:
    """F1-03: .dockerignore exists with required patterns."""

    REQUIRED_PATTERNS = [
        "venv/",
        "tests/",
        "__pycache__/",
        ".env",
        ".git/",
        ".pytest_cache/",
    ]

    def test_dockerignore_exists(self):
        assert DOCKERIGNORE.exists(), ".dockerignore not found"

    def test_dockerignore_not_empty(self):
        content = DOCKERIGNORE.read_text()
        assert len(content.strip()) > 0, ".dockerignore is empty"

    @pytest.mark.parametrize("pattern", REQUIRED_PATTERNS)
    def test_required_pattern_present(self, pattern: str):
        content = DOCKERIGNORE.read_text()
        assert pattern in content, f"Missing .dockerignore pattern: {pattern}"


# ═══════════════════════════════════════════════════════════════
# Slice 1: docker-compose.override.yml
# ═══════════════════════════════════════════════════════════════
class TestOverrideCompose:
    """F1-04: docker-compose.override.yml template exists."""

    def test_override_exists(self):
        assert OVERRIDE_FILE.exists(), "docker-compose.override.yml not found"

    def test_override_is_valid_yaml(self, run_cmd):
        """Override must merge cleanly with main compose."""
        rc, stdout, stderr = run_cmd(
            f"docker compose -f {COMPOSE_FILE} -f {OVERRIDE_FILE} config"
        )
        assert rc == 0, f"Override merge failed:\nstdout: {stdout}\nstderr: {stderr}"

    def test_override_has_services(self):
        content = OVERRIDE_FILE.read_text()
        assert "services:" in content, "override missing services key"


# ═══════════════════════════════════════════════════════════════
# Slice 1: Make targets for F1
# ═══════════════════════════════════════════════════════════════
class TestMakefileF1Targets:
    """Makefile must have all F1 targets."""

    @pytest.mark.parametrize("target", [
        "up", "down", "restart", "logs", "status",
        "validate", "destroy", "db-check",
    ])
    def test_target_exists(self, root: Path, target: str):
        makefile = root / "Makefile"
        content = makefile.read_text()
        assert f"{target}:" in content, f"Missing Makefile target: {target}"


# ═══════════════════════════════════════════════════════════════
# Security: Secrets and isolation
# ═══════════════════════════════════════════════════════════════
class TestSecurityF1:
    """Security checks specific to F1 infrastructure."""

    def test_env_not_committed(self, run_cmd):
        rc, _, _ = run_cmd("git check-ignore -q .env")
        assert rc == 0, ".env must be gitignored"

    def test_no_hardcoded_creds_in_compose(self):
        """No hardcoded passwords in docker-compose.yml."""
        content = compose_content()
        forbidden = ["POSTGRES_PASSWORD: ", "POSTGRES_USER: admin",
                     "MB_DB_USER: ", "MB_DB_PASS: "]
        # The env vars should reference ${VAR} not literal values
        # Lines like "POSTGRES_PASSWORD: change-me" would be hardcoded
        for line in content.splitlines():
            for pattern in ["POSTGRES_PASSWORD:", "MB_DB_PASS:"]:
                if pattern in line and "${" not in line:
                    # Allow default values with YAML inline ${VAR:-default}
                    # But flag naked assignments
                    if "=" not in line and ":" not in line.replace(" ", "").replace("-", ""):
                        continue
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if stripped.startswith(pattern) and "${" not in stripped:
                        pytest.fail(f"Hardcoded credential found: {stripped}")


# ═══════════════════════════════════════════════════════════════
# Slice 2: Services Up & Healthy (Runtime)
# ═══════════════════════════════════════════════════════════════
class TestRuntimeServices:
    """F1-05 to F1-07: Services must be up and healthy.
    These tests run only with Docker available (mark: runtime)."""

    @staticmethod
    def _has_docker(run_cmd) -> bool:
        """Check if Docker daemon is available."""
        rc, _, _ = run_cmd("docker info --format '{{.ServerVersion}}'")
        return rc == 0

    @pytest.mark.runtime
    def test_services_are_running(self, run_cmd):
        """F1-05: Both containers must be Up."""
        if not self._has_docker(run_cmd):
            pytest.skip("Docker not available")

        rc, stdout, stderr = run_cmd(
            "docker ps --filter name=metabase --format '{{.Status}}'",
        )
        assert rc == 0, f"docker ps failed: {stderr}"
        states = stdout.splitlines()
        assert len(states) == 2, f"Expected 2 containers, found {len(states)}"
        for state in states:
            assert "Up" in state, f"Container not running: {state}"

    @pytest.mark.runtime
    def test_postgres_accepts_connections(self, run_cmd):
        """F1-06: pg_isready returns accepting connections."""
        if not self._has_docker(run_cmd):
            pytest.skip("Docker not available")

        rc, stdout, stderr = run_cmd(
            "docker exec -i metabase-postgres pg_isready -U ecommerce-fish"
        )
        assert rc == 0, f"pg_isready failed: {stderr}"
        assert "accepting connections" in stdout.lower(), \
            f"pg_isready unexpected output: {stdout}"

    @pytest.mark.runtime
    def test_metabase_logs_no_fatal(self, run_cmd):
        """F1-07: Metabase logs must not contain FATAL or Connection refused."""
        if not self._has_docker(run_cmd):
            pytest.skip("Docker not available")

        rc, stdout, stderr = run_cmd(
            "docker compose -f docker/docker-compose.yml logs metabase --tail 100 2>&1"
        )
        assert rc == 0, f"docker logs failed: {stderr}"
        assert "FATAL" not in stdout, f"Metabase log contains FATAL:\n{stdout}"
        assert "Connection refused" not in stdout, \
            f"Metabase log contains Connection refused:\n{stdout}"


# ═══════════════════════════════════════════════════════════════
# Slice 3: Integration & Resilience (Runtime)
# ═══════════════════════════════════════════════════════════════
class TestRuntimeIntegration:
    """F1-08 to F1-11: Integration tests require running services."""

    @staticmethod
    def _has_docker(run_cmd) -> bool:
        rc, _, _ = run_cmd("docker info --format '{{.ServerVersion}}'")
        return rc == 0

    @pytest.mark.runtime
    def test_metabase_api_health(self, run_cmd):
        """F1-08: Metabase API health endpoint returns OK."""
        if not self._has_docker(run_cmd):
            pytest.skip("Docker not available")

        rc, stdout, stderr = run_cmd(
            "curl -sf http://localhost:3000/api/health 2>&1"
        )
        assert rc == 0, f"Metabase health check failed: {stderr}"
        assert "ok" in stdout.lower(), f"Unexpected health response: {stdout}"

    @pytest.mark.runtime
    def test_port_5432_not_exposed(self, run_cmd):
        """F1-11: PostgreSQL port 5432 must NOT be exposed to host."""
        if not self._has_docker(run_cmd):
            pytest.skip("Docker not available")

        rc, stdout, stderr = run_cmd(
            "docker port metabase-postgres 2>&1"
        )
        # docker port for a container without published ports returns empty + exit 0
        assert rc == 0, f"docker port failed: {stderr}"
        assert stdout.strip() == "", \
            f"PostgreSQL port should not be exposed, found: {stdout}"

    @pytest.mark.runtime
    def test_nc_port_5432_refused(self, run_cmd):
        """F1-11: nc should report connection refused to localhost:5432."""
        if not self._has_docker(run_cmd):
            pytest.skip("Docker not available")

        rc, stdout, stderr = run_cmd("nc -zv localhost 5432 -w 2 2>&1")
        # nc returns non-zero when connection refused
        assert rc != 0, f"Port 5432 should be refused, but nc succeeded: {stdout}"
        refused_indicators = ["refused", "failed", "Connection refused", "timed out"]
        has_refused = any(ind in stdout.lower() for ind in refused_indicators)
        assert has_refused, f"Expected 'connection refused' but got: {stdout}"
