"""Pytest configuration for Dashboard Metabase project."""
import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "runtime: marks tests that require Docker daemon (skipped if not available)")
