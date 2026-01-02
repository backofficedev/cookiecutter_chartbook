"""Pytest fixtures for cookiecutter template tests."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test output."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def template_dir():
    """Return the path to the cookiecutter template (repository root)."""
    return Path(__file__).parent.parent
