"""Tests for the backtest engine."""
from src.backtest import run_backtest
from src.models import (
    BacktestResult,
    ETFFlowSnapshot,
    StrategyCard,
    StrategyConfig,
    TideLevel,
    TideReaction,
)


class FakeStore:
    def get_flows(self):
        return [
            ETFFlowSnapshot("2025-01-01", 300_000_000, "accelerating", 3),
            ETFFlowSnapshot("2025-01-02", 400_000_000, "accelerating", 4),
            ETFFlowSnapshot("2025-01-03", -200_000_000, "decelerating", -1),
            ETFFlowSnapshot("2025-01-04", -300_000_000, "accelerating", -2),
            ETFFlowSnapshot("2025-01-05", 100_000_000, "stable", 1),
        ]

    def get_price_series(self):
        return [
            {"date": "2025-01-01", "price_usd": 40000.0},
            {"date": "2025-01-02", "price_usd": 41000.0},
            {"date": "2025-01-03", "price_usd": 40500.0},
            {"date": "2025-01-04", "price_usd": 39800.0},
            {"date": "2025-01-05", "price_usd": 40200.0},
        ]


def _card() -> StrategyCard:
    reaction = TideReaction(
        tide_level=TideLevel.STRONG_INFLOW,
        sample_size=5,
        median_7d_return=0.03,
        median_14d_return=0.06,
        hit_rate=0.7,
    )
    config = StrategyConfig()
    return StrategyCard(
        tide=TideLevel.STRONG_INFLOW,
        reaction=reaction,
        config=config,
        entry_rule="test",
        exit_rule="test",
        position_sizing="100%",
        invalidation="test",
    )


def test_returns_result():
    result = run_backtest(_card(), FakeStore())
    assert isinstance(result, BacktestResult)
    assert len(result.equity_curve) >= 2
