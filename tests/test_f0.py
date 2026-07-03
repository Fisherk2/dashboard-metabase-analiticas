"""
Tests: F0: Preparación — Validación de estructura, configuración y seguridad.

Verifica todos los criterios de aceptación del plan F0:
- Slice 1: Foundation (directorios, docker-compose, .gitignore, .env)
- Slice 2: Documentation (README, AGENTS, ARCHITECTURE)
- Slice 3: Automation (Makefile, requirements.txt)
- Security: No secrets in repo
"""
import subprocess
from pathlib import Path

import pytest

# ─── Slice 1: Foundation ────────────────────────────────────
class TestDirectoryStructure:
    """F0-01a: Create directory structure per SPEC.md."""

    @pytest.mark.parametrize("directory", [
        "docker",
        "sql/views",
        "sql/indexes",
        "sql/partitions",
        "metabase/collections",
    ])
    def test_directory_exists(self, root: Path, directory: str):
        assert (root / directory).is_dir(), f"Missing directory: {directory}"

    @pytest.mark.parametrize("directory", [
        "docker",
        "sql/views",
        "sql/indexes",
        "sql/partitions",
        "metabase/collections",
    ])
    def test_directory_has_gitkeep(self, root: Path, directory: str):
        gitkeep = root / directory / ".gitkeep"
        assert gitkeep.exists(), f"Missing .gitkeep in: {directory}"


class TestDockerCompose:
    """F0-01b: docker-compose.yml moved to docker/, root stubs removed."""

    def test_compose_in_docker_dir(self, root: Path):
        assert (root / "docker" / "docker-compose.yml").exists()

    def test_compose_not_in_root(self, root: Path):
        assert not (root / "docker-compose.yml").exists()

    def test_dockerfile_removed(self, root: Path):
        assert not (root / "Dockerfile").exists()

    def test_compose_has_services(self, root: Path):
        content = (root / "docker" / "docker-compose.yml").read_text()
        assert "services:" in content
        assert "postgres" in content
        assert "metabase" in content


class TestScriptsCleanup:
    """F0-01c: Remove stub .sh files from scripts/."""

    def test_no_sh_files(self, root: Path):
        scripts_dir = root / "scripts"
        assert scripts_dir.is_dir(), "scripts/ directory must exist"
        sh_files = list(scripts_dir.glob("*.sh"))
        assert len(sh_files) == 0, f"Found .sh files: {[f.name for f in sh_files]}"


class TestGitignore:
    """F0-02a: Extend .gitignore with project-specific patterns."""

    @pytest.mark.parametrize("pattern,should_match", [
        (".env", True),
        ("data/test.sql", True),
        ("dump.sql.gz", True),
        ("metabase-data/file", True),
        (".env.example", False),
    ])
    def test_gitignore_patterns(self, root: Path, pattern: str, should_match: bool, run_cmd):
        rc, _, _ = run_cmd(f"git check-ignore -q {pattern}")
        is_ignored = rc == 0
        assert is_ignored == should_match, (
            f"git check-ignore {pattern}: expected {'ignored' if should_match else 'not ignored'}, "
            f"got {'ignored' if is_ignored else 'not ignored'}"
        )


class TestEnvExample:
    """F0-02b: Create .env.example template with documented variables."""

    def test_env_example_exists(self, root: Path):
        assert (root / ".env.example").exists()

    def test_env_example_has_variables(self, root: Path):
        content = (root / ".env.example").read_text()
        vars_count = content.count("=")
        assert vars_count >= 6, f"Expected >= 6 variables, found {vars_count}"

    def test_env_example_is_not_empty(self, root: Path):
        content = (root / ".env.example").read_text()
        assert len(content.strip()) > 0


# ─── Slice 2: Documentation ─────────────────────────────────
class TestReadme:
    """F0-03: Create README.md with badges, Quick Start, structure."""

    def test_readme_exists(self, root: Path):
        assert (root / "README.md").exists()

    def test_readme_has_content(self, root: Path):
        content = (root / "README.md").read_text()
        assert len(content.strip()) > 0

    def test_readme_has_minimum_lines(self, root: Path):
        lines = (root / "README.md").read_text().splitlines()
        assert len(lines) >= 50, f"README.md has {len(lines)} lines, expected >= 50"

    def test_readme_has_badges(self, root: Path):
        content = (root / "README.md").read_text()
        assert "PostgreSQL" in content or "postgres" in content.lower()
        assert "Docker" in content or "docker" in content.lower()

    def test_readme_has_quickstart(self, root: Path):
        content = (root / "README.md").read_text().lower()
        assert "make setup" in content or "quick start" in content


class TestAgents:
    """F0-04: Verify AGENTS.md exists and is under 60 lines."""

    def test_agents_exists(self, root: Path):
        assert (root / "AGENTS.md").exists()

    def test_agents_under_60_lines(self, root: Path):
        lines = (root / "AGENTS.md").read_text().splitlines()
        assert len(lines) < 60, f"AGENTS.md has {len(lines)} lines, expected < 60"


class TestArchitecture:
    """F0-04: Verify ARCHITECTURE.md has Mermaid and ADR index."""

    def test_architecture_exists(self, root: Path):
        assert (root / "docs" / "ARCHITECTURE.md").exists()

    def test_architecture_has_mermaid(self, root: Path):
        content = (root / "docs" / "ARCHITECTURE.md").read_text()
        assert "mermaid" in content.lower()

    def test_architecture_has_adr_index(self, root: Path):
        content = (root / "docs" / "ARCHITECTURE.md").read_text()
        assert "ADR" in content or "adr" in content


# ─── Slice 3: Automation ────────────────────────────────────
class TestMakefile:
    """F0-05: Implement complete Makefile with 25+ targets."""

    def test_makefile_exists(self, root: Path):
        assert (root / "Makefile").exists()

    def test_makefile_has_default_goal(self, root: Path):
        content = (root / "Makefile").read_text()
        assert ".DEFAULT_GOAL" in content

    def test_makefile_has_pragma_phony(self, root: Path):
        content = (root / "Makefile").read_text()
        assert ".PHONY" in content

    @pytest.mark.parametrize("target", [
        "help", "up", "down", "restart", "logs", "status", "validate",
        "destroy", "db-shell", "db-init", "db-reset", "db-check",
        "deps", "data-generate", "data-debug", "data-count",
        "mv-refresh", "indexes-check",
        "test-queries", "test-integrity", "test-full",
        "setup", "clean",
    ])
    def test_makefile_target_exists(self, root: Path, target: str):
        content = (root / "Makefile").read_text()
        assert f"{target}:" in content, f"Makefile missing target: {target}"

    def test_makefile_25_targets(self, root: Path):
        content = (root / "Makefile").read_text()
        targets = [line.split(":")[0].strip() for line in content.splitlines()
                   if ":" in line and not line.strip().startswith("#") and not line.strip().startswith(".")]
        assert len(targets) >= 25, f"Makefile has {len(targets)} targets, expected >= 25"


class TestRequirements:
    """F0-05b: Fill requirements.txt with Python dependencies."""

    def test_requirements_exists(self, root: Path):
        assert (root / "scripts" / "requirements.txt").exists()

    def test_requirements_has_faker(self, root: Path):
        content = (root / "scripts" / "requirements.txt").read_text()
        assert "faker" in content.lower()

    def test_requirements_has_psycopg2(self, root: Path):
        content = (root / "scripts" / "requirements.txt").read_text()
        assert "psycopg2" in content.lower()

    def test_requirements_has_dotenv(self, root: Path):
        content = (root / "scripts" / "requirements.txt").read_text()
        assert "dotenv" in content.lower()


# ─── Security ────────────────────────────────────────────────
class TestSecurity:
    """Security checks for F0."""

    def test_no_secrets_in_commit_messages(self, run_cmd):
        rc, stdout, _ = run_cmd("git log --all --oneline | head -30")
        forbidden = ["password", "secret", "api_key", "token"]
        for word in forbidden:
            assert word.lower() not in stdout.lower(), (
                f"Found '{word}' in commit messages"
            )

    def test_env_is_gitignored(self, run_cmd):
        rc, _, _ = run_cmd("git check-ignore -q .env")
        assert rc == 0, ".env should be gitignored"

    def test_env_example_is_not_gitignored(self, run_cmd):
        rc, _, _ = run_cmd("git check-ignore -q .env.example")
        assert rc != 0, ".env.example should NOT be gitignored"


# ─── Venv ────────────────────────────────────────────────────
class TestVenv:
    """Python virtual environment exists and has dependencies."""

    @staticmethod
    def _pip_list(root: Path) -> str:
        """Return pip list output for the venv."""
        result = subprocess.run(
            ["venv/bin/python", "-m", "pip", "list"],
            capture_output=True, text=True, cwd=root
        )
        return result.stdout

    def test_venv_exists(self, root: Path):
        assert (root / "venv").is_dir()

    def test_venv_has_python(self, root: Path):
        assert (root / "venv" / "bin" / "python").exists()

    def test_venv_has_pip(self, root: Path):
        assert (root / "venv" / "bin" / "pip").exists()

    def test_venv_has_faker(self, root: Path):
        assert "Faker" in self._pip_list(root), "Faker not found in venv"

    def test_venv_has_psycopg2(self, root: Path):
        assert "psycopg2" in self._pip_list(root), "psycopg2 not found in venv"
