"""Tide classifier for Institutional Tide."""
from __future__ import annotations

from src.models import TideLevel


def classify_tide(score: float) -> TideLevel:
    if score > 2:
        return TideLevel.STRONG_INFLOW
    if score > 1:
        return TideLevel.MILD_INFLOW
    if score > -1:
        return TideLevel.NEUTRAL
    if score > -2:
        return TideLevel.MILD_OUTFLOW
    return TideLevel.STRONG_OUTFLOW
