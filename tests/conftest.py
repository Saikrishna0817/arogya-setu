"""Pytest fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_prescription_text():
    """Sample prescription text."""
    return """
    Dr. Ramesh Kumar
    Patient: Priya Sharma
    Date: 15/03/2024
    
    Dx: Hypertension
    
    1. Amlodipine 5mg OD x 30 days
    2. Metoprolol 50mg BD x 30 days
    
    Follow up after 1 month
    """