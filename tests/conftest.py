"""Pytest configuration for Dashboard Metabase project."""
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def root() -> Path:
    """Absolute path to project root."""
    return PROJECT_ROOT


@pytest.fixture
def run_cmd():
    """Execute a shell command and return (returncode, stdout, stderr)."""
    def _run(cmd: str, **kwargs) -> tuple:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=PROJECT_ROOT, **kwargs
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    return _run


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "runtime: marks tests that require Docker daemon (skipped if not available)")
    config.addinivalue_line("markers", "timeout: mark test with timeout in seconds (provided by pytest-timeout)")
