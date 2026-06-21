"""Tests for the fixture store loader."""
from src.fixtures.loader import FixtureStore
from src.models import ETFFlowSnapshot


def test_flows_count():
    store = FixtureStore()
    flows = store.get_flows()
    assert len(flows) >= 10
    assert all(isinstance(f, ETFFlowSnapshot) for f in flows)


def test_price_series():
    store = FixtureStore()
    prices = store.get_price_series()
    assert len(prices) >= 10
    assert all("date" in p and "price_usd" in p for p in prices)
