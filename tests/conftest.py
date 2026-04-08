"""Shared fixtures for tests."""
import json
from pathlib import Path

import pytest

from stock_analytics.briefing.schema import RawData

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_nvda_raw() -> RawData:
    """Deterministic NVDA RawData for indicator/scoring tests."""
    payload = json.loads((FIXTURES_DIR / "sample_nvda.json").read_text())
    return RawData.model_validate(payload)
