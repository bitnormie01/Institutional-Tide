"""End-to-end integration test for Institutional Tide."""
from src.backtest import run_backtest
from src.classifier import classify_tide
from src.emitter import emit_strategy, render_yaml, render_markdown
from src.fixtures.loader import FixtureStore
from src.models import BacktestResult, StrategyCard, StrategyConfig, TideLevel, TideReaction
from src.momentum import compute_momentum_score


def _compute_reaction(level, flows, price_map, dates):
    """Minimal historical reaction computation for integration test."""
    import statistics
    returns_7d = []
    total = 0
    hits = 0
    for i, flow in enumerate(flows):
        history = flows[:i]
        m = compute_momentum_score(flow, history)
        t = classify_tide(m.score)
        if t != level:
            continue
        idx = dates.index(flow.date) if flow.date in dates else -1
        if idx < 0:
            continue
        total += 1
        if idx + 7 < len(dates):
            r = (price_map[dates[idx + 7]] - price_map[dates[idx]]) / price_map[dates[idx]]
            returns_7d.append(r)
            if level in (TideLevel.STRONG_INFLOW, TideLevel.MILD_INFLOW) and r > 0:
                hits += 1
    median_7d = statistics.median(returns_7d) if returns_7d else 0.0
    hit_rate = hits / total if total > 0 else 0.0
    return TideReaction(
        tide_level=level,
        sample_size=total,
        median_7d_return=round(median_7d, 6),
        median_14d_return=0.0,
        hit_rate=round(hit_rate, 4),
    )


def test_full_pipeline():
    store = FixtureStore()
    flows = store.get_flows()
    prices = store.get_price_series()
    price_map = {p["date"]: p["price_usd"] for p in prices}
    dates = sorted(price_map.keys())

    assert len(flows) >= 10
    assert len(prices) >= 10

    latest = flows[-1]
    history = flows[:-1]

    momentum = compute_momentum_score(latest, history)
    assert -5 <= momentum.score <= 5

    tide = classify_tide(momentum.score)
    assert isinstance(tide, TideLevel)

    reaction = _compute_reaction(tide, flows, price_map, dates)
    config = StrategyConfig()
    card = emit_strategy(tide, reaction, config)
    assert isinstance(card, StrategyCard)

    yaml_out = render_yaml(card)
    assert "strategy" in yaml_out

    md_out = render_markdown(card)
    assert "Institutional Tide" in md_out

    bt = run_backtest(card, store)
    assert isinstance(bt, BacktestResult)
    assert len(bt.equity_curve) >= 2
