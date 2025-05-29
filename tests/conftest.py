"""Fixture loader for pynjspc snapshot responses."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def status_snapshot():
    """Load the JSON snapshot from tests/snapshots/status.json."""
    snapshot_path = Path(__file__).parent / 'snapshots' / 'status.json'
    with snapshot_path.open('r', encoding='utf-8') as file:
        return json.load(file)