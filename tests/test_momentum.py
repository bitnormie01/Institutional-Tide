"""Tests for the flow momentum scorer."""
from src.models import ETFFlowSnapshot, MomentumResult
from src.momentum import compute_momentum_score


def test_strong_inflow():
    flow = ETFFlowSnapshot(
        date="2025-01-03",
        net_inflow_usd=500_000_000,
        inflow_trend="accelerating",
        flow_streak_days=5,
    )
    result = compute_momentum_score(flow, [])
    assert isinstance(result, MomentumResult)
    assert result.score > 2


def test_strong_outflow():
    flow = ETFFlowSnapshot(
        date="2025-01-14",
        net_inflow_usd=-400_000_000,
        inflow_trend="accelerating",
        flow_streak_days=-6,
    )
    result = compute_momentum_score(flow, [])
    assert result.score < -2


def test_clamped_to_range():
    huge = ETFFlowSnapshot(
        date="2025-01-01",
        net_inflow_usd=999_999_999_999,
        inflow_trend="accelerating",
        flow_streak_days=100,
    )
    result = compute_momentum_score(huge, [])
    assert -5 <= result.score <= 5
