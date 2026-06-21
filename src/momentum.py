"""Flow momentum scorer for Institutional Tide."""
from __future__ import annotations

import math
from typing import List

from src.models import ETFFlowSnapshot, MomentumResult


def compute_momentum_score(
    flow: ETFFlowSnapshot,
    history: List[ETFFlowSnapshot],
) -> MomentumResult:
    sign = 1.0 if flow.net_inflow_usd >= 0 else -1.0
    base = sign * math.log1p(abs(flow.net_inflow_usd) / 1e8)

    if flow.inflow_trend == "accelerating":
        acceleration_bonus = 0.5 * sign
    else:
        acceleration_bonus = 0.0

    streak = flow.flow_streak_days
    streak_bonus = min(abs(streak), 5) / 5.0 * 0.5 * sign

    raw = base + acceleration_bonus + streak_bonus
    clamped = max(-5.0, min(5.0, raw))

    return MomentumResult(
        score=clamped,
        base_component=base,
        acceleration_bonus=acceleration_bonus,
        streak_bonus=streak_bonus,
    )
