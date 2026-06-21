"""Backtest engine for Institutional Tide."""
from __future__ import annotations

import math
from typing import List, Protocol

from src.classifier import classify_tide
from src.models import BacktestResult, StrategyCard, TideLevel
from src.momentum import compute_momentum_score


class PriceFlowStore(Protocol):
    def get_flows(self): ...
    def get_price_series(self) -> List[dict]: ...


def run_backtest(strategy: StrategyCard, fixture_store: PriceFlowStore) -> BacktestResult:
    flows = fixture_store.get_flows()
    prices = fixture_store.get_price_series()

    price_map = {p["date"]: p["price_usd"] for p in prices}
    flow_map = {f.date: f for f in flows}
    dates = sorted(set(price_map.keys()) & set(flow_map.keys()))

    if len(dates) < 2:
        return BacktestResult(
            total_return=0.0,
            buy_hold_return=0.0,
            alpha=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            equity_curve=[1.0],
        )

    alloc_map = strategy.config.allocation_map
    equity = 1.0
    bh_equity = 1.0
    equity_curve: List[float] = [1.0]
    peak = 1.0
    max_dd = 0.0
    daily_returns: List[float] = []
    stopped = False

    for i in range(1, len(dates)):
        prev_date = dates[i - 1]
        curr_date = dates[i]
        prev_price = price_map[prev_date]
        curr_price = price_map[curr_date]
        day_return = (curr_price - prev_price) / prev_price

        bh_equity *= 1.0 + day_return

        if stopped:
            equity_curve.append(equity)
            daily_returns.append(0.0)
            continue

        prev_flow = flow_map[prev_date]
        history = [flow_map[d] for d in dates[:i] if d in flow_map]
        momentum = compute_momentum_score(prev_flow, history)
        tide = classify_tide(momentum.score)
        alloc = alloc_map.get(tide, 0.5)

        equity *= 1.0 + day_return * alloc
        daily_returns.append(day_return * alloc)
        equity_curve.append(equity)

        if equity > peak:
            peak = equity
        dd = (equity - peak) / peak
        if dd < max_dd:
            max_dd = dd
        if dd <= strategy.config.max_drawdown_stop:
            stopped = True

    total_return = equity - 1.0
    buy_hold_return = bh_equity - 1.0
    alpha = total_return - buy_hold_return

    if len(daily_returns) > 1:
        mean_r = sum(daily_returns) / len(daily_returns)
        var_r = sum((r - mean_r) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
        std_r = math.sqrt(var_r) if var_r > 0 else 0.0
        sharpe = (mean_r / std_r * math.sqrt(252)) if std_r > 0 else 0.0
    else:
        sharpe = 0.0

    return BacktestResult(
        total_return=round(total_return, 6),
        buy_hold_return=round(buy_hold_return, 6),
        alpha=round(alpha, 6),
        sharpe_ratio=round(sharpe, 4),
        max_drawdown=round(max_dd, 6),
        equity_curve=equity_curve,
    )
