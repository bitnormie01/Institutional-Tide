"""Fixture store: loads JSON fixture files into typed models."""
from __future__ import annotations

import json
import pathlib
from typing import List

from src.models import ETFFlowSnapshot

_FIXTURE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "fixtures"


class FixtureStore:
    def __init__(self, fixture_dir: pathlib.Path | None = None) -> None:
        self._dir = fixture_dir or _FIXTURE_DIR

    def get_flows(self) -> List[ETFFlowSnapshot]:
        data = json.loads((self._dir / "etf_flows.json").read_text())
        return [
            ETFFlowSnapshot(
                date=row["date"],
                net_inflow_usd=row["net_inflow_usd"],
                inflow_trend=row["inflow_trend"],
                flow_streak_days=row["flow_streak_days"],
            )
            for row in data
        ]

    def get_price_series(self) -> List[dict]:
        return json.loads((self._dir / "quotes.json").read_text())

    def get_global_metrics(self) -> List[dict]:
        return json.loads((self._dir / "global.json").read_text())
