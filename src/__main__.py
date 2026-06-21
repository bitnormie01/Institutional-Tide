"""CLI entry point for Institutional Tide."""
from __future__ import annotations

import argparse
import statistics
import sys
from typing import List

from src.backtest import run_backtest
from src.classifier import classify_tide
from src.emitter import emit_strategy, render_markdown, render_yaml
from src.fixtures.loader import FixtureStore
from src.models import (
    ETFFlowSnapshot,
    StrategyConfig,
    TideLevel,
    TideReaction,
)
from src.momentum import compute_momentum_score


def _compute_tide_reaction(
    level: TideLevel,
    flows: List[ETFFlowSnapshot],
    price_map: dict[str, float],
    dates: List[str],
) -> TideReaction:
    """Compute historical reaction for a given tide level from fixture data."""
    returns_7d: List[float] = []
    returns_14d: List[float] = []
    hits = 0
    total = 0

    for i, flow in enumerate(flows):
        history = flows[:i]
        m = compute_momentum_score(flow, history)
        tide = classify_tide(m.score)
        if tide != level:
            continue

        idx = dates.index(flow.date) if flow.date in dates else -1
        if idx < 0:
            continue

        if idx + 7 < len(dates):
            p0 = price_map[dates[idx]]
            p7 = price_map[dates[idx + 7]]
            r7 = (p7 - p0) / p0
            returns_7d.append(r7)
        if idx + 14 < len(dates):
            p0 = price_map[dates[idx]]
            p14 = price_map[dates[idx + 14]]
            r14 = (p14 - p0) / p0
            returns_14d.append(r14)

        total += 1
        if level in (TideLevel.STRONG_INFLOW, TideLevel.MILD_INFLOW):
            if idx + 7 < len(dates) and price_map[dates[idx + 7]] > price_map[dates[idx]]:
                hits += 1
        elif level in (TideLevel.STRONG_OUTFLOW, TideLevel.MILD_OUTFLOW):
            if idx + 7 < len(dates) and price_map[dates[idx + 7]] < price_map[dates[idx]]:
                hits += 1

    median_7d = statistics.median(returns_7d) if returns_7d else 0.0
    median_14d = statistics.median(returns_14d) if returns_14d else 0.0
    hit_rate = hits / total if total > 0 else 0.0

    return TideReaction(
        tide_level=level,
        sample_size=total,
        median_7d_return=round(median_7d, 6),
        median_14d_return=round(median_14d, 6),
        hit_rate=round(hit_rate, 4),
    )


def run(mode: str = "fixture", output_dir: str | None = None) -> None:
    if mode == "fixture":
        store = FixtureStore()
    else:
        print("Live mode requires CMC API credentials (not implemented for demo).")
        sys.exit(1)

    flows = store.get_flows()
    prices = store.get_price_series()
    price_map = {p["date"]: p["price_usd"] for p in prices}
    dates = sorted(price_map.keys())

    latest = flows[-1]
    history = flows[:-1]

    momentum = compute_momentum_score(latest, history)
    tide = classify_tide(momentum.score)

    print("=" * 60)
    print("  INSTITUTIONAL TIDE - Flow Momentum Strategy")
    print("=" * 60)
    print()
    print(f"  Date:            {latest.date}")
    print(f"  Net ETF Flow:    ${latest.net_inflow_usd:,.0f}")
    print(f"  Flow Trend:      {latest.inflow_trend}")
    print(f"  Streak:          {latest.flow_streak_days} days")
    print()
    print(f"  Momentum Score:  {momentum.score:+.2f}  (range -5 to +5)")
    print(f"    base:          {momentum.base_component:+.4f}")
    print(f"    acceleration:  {momentum.acceleration_bonus:+.4f}")
    print(f"    streak:        {momentum.streak_bonus:+.4f}")
    print()
    print(f"  Tide Level:      {tide.value}")
    print()

    reaction = _compute_tide_reaction(tide, flows, price_map, dates)
    config = StrategyConfig()
    card = emit_strategy(tide, reaction, config)

    print("-" * 60)
    print("  HISTORICAL REACTION")
    print("-" * 60)
    print(f"  Sample size:     {reaction.sample_size}")
    print(f"  Median 7d ret:   {reaction.median_7d_return:+.2%}")
    print(f"  Median 14d ret:  {reaction.median_14d_return:+.2%}")
    print(f"  Hit rate:        {reaction.hit_rate:.1%}")
    print()

    print("-" * 60)
    print("  STRATEGY CARD (YAML)")
    print("-" * 60)
    print(render_yaml(card))

    bt = run_backtest(card, store)

    print("-" * 60)
    print("  BACKTEST RESULTS")
    print("-" * 60)
    print(f"  Total return:    {bt.total_return:+.2%}")
    print(f"  Buy & hold:      {bt.buy_hold_return:+.2%}")
    print(f"  Alpha:           {bt.alpha:+.2%}")
    print(f"  Sharpe ratio:    {bt.sharpe_ratio:.4f}")
    print(f"  Max drawdown:    {bt.max_drawdown:+.2%}")
    print(f"  Equity pts:      {len(bt.equity_curve)}")
    print()
    print("=" * 60)
    print("  Demo complete - no credentials, no live trading.")
    print("=" * 60)

    if output_dir:
        import pathlib
        out = pathlib.Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "strategy.yaml").write_text(render_yaml(card))
        (out / "strategy.md").write_text(render_markdown(card))
        print(f"\n  Output written to {output_dir}/")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="institutional_tide",
        description="Institutional Tide - CMC institutional-flow strategy skill",
    )
    sub = parser.add_subparsers(dest="command")
    run_p = sub.add_parser("run", help="Run the full pipeline")
    run_p.add_argument("--mode", choices=["fixture", "live"], default="fixture")
    run_p.add_argument("--output-dir", default=None)

    args = parser.parse_args()
    if args.command == "run":
        run(mode=args.mode, output_dir=args.output_dir)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
