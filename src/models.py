"""Data models for Institutional Tide."""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List


class TideLevel(enum.Enum):
    STRONG_INFLOW = "STRONG_INFLOW"
    MILD_INFLOW = "MILD_INFLOW"
    NEUTRAL = "NEUTRAL"
    MILD_OUTFLOW = "MILD_OUTFLOW"
    STRONG_OUTFLOW = "STRONG_OUTFLOW"


@dataclass(frozen=True)
class ETFFlowSnapshot:
    date: str
    net_inflow_usd: float
    inflow_trend: str  # "accelerating" | "decelerating" | "stable"
    flow_streak_days: int


@dataclass(frozen=True)
class MomentumResult:
    score: float
    base_component: float
    acceleration_bonus: float
    streak_bonus: float


@dataclass(frozen=True)
class TideReaction:
    tide_level: TideLevel
    sample_size: int
    median_7d_return: float
    median_14d_return: float
    hit_rate: float


@dataclass(frozen=True)
class StrategyConfig:
    allocation_map: Dict[TideLevel, float] = field(default_factory=lambda: {
        TideLevel.STRONG_INFLOW: 1.0,
        TideLevel.MILD_INFLOW: 0.75,
        TideLevel.NEUTRAL: 0.50,
        TideLevel.MILD_OUTFLOW: 0.25,
        TideLevel.STRONG_OUTFLOW: 0.0,
    })
    max_drawdown_stop: float = -0.12
    rebalance_on_level_change: bool = True


@dataclass(frozen=True)
class StrategyCard:
    tide: TideLevel
    reaction: TideReaction
    config: StrategyConfig
    entry_rule: str
    exit_rule: str
    position_sizing: str
    invalidation: str


@dataclass(frozen=True)
class BacktestResult:
    total_return: float
    buy_hold_return: float
    alpha: float
    sharpe_ratio: float
    max_drawdown: float
    equity_curve: List[float]
