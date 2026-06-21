# Institutional Tide

Institutional Tide is a Track 2 Strategy Skill for converting institutional flow momentum into an explicit market-allocation card. It is fixture-backed: the CLI reads local ETF flow snapshots and price fixtures; scores the latest flow regime; classifies the market tide; emits a YAML/Markdown strategy card; and replays the allocation rule against fixture prices. The fixture store also includes global market context for review.

The checked-in fixture output classifies the latest snapshot as `STRONG_INFLOW`, with a 100% allocation rule, a 24-sample historical reaction set, 1.55% median 7-day return, -6.21% median 14-day return, and a 54.2% hit rate.

## Track 2 Fit

This project fits Track 2 because it produces a transparent strategy artifact from market evidence. The inputs are fixture files, the score components are printed by the CLI, the tide classification is threshold-based, and the strategy card exposes entry, exit, sizing, invalidation, and risk controls.

The strategy card includes:

- Tide level: `STRONG_INFLOW`, `MILD_INFLOW`, `NEUTRAL`, `MILD_OUTFLOW`, or `STRONG_OUTFLOW`.
- Historical reaction: sample size, median 7-day return, median 14-day return, and hit rate.
- Entry rule: target allocation when the current tide level is active.
- Exit rule: move to 0% on `STRONG_OUTFLOW` or when the drawdown stop is triggered.
- Position sizing: allocation from the tide-to-allocation map.
- Risk controls: -12% max drawdown stop and rebalance-on-level-change flag.
- Backtest metrics: total return, buy-and-hold return, alpha, Sharpe ratio, max drawdown, and equity-point count.

## Evidence Inputs

All evidence is local and reproducible:

- `fixtures/etf_flows.json` contains dated net ETF flow snapshots, flow trend labels, and streak lengths.
- `fixtures/quotes.json` contains dated `price_usd` rows used for reaction windows and backtesting.
- `fixtures/global.json` contains market-cap, BTC dominance, and 24h volume context loaded by the fixture store.

Momentum scoring is intentionally auditable:

- Flow magnitude contributes a signed log-scaled base component.
- Accelerating flows add a signed acceleration bonus.
- Flow streak length adds a signed streak bonus capped at 5 days.
- Final score is clamped to the range `-5` to `+5`.

Tide classification thresholds:

- `STRONG_INFLOW` when score is greater than `2`.
- `MILD_INFLOW` when score is greater than `1`.
- `NEUTRAL` when score is greater than `-1`.
- `MILD_OUTFLOW` when score is greater than `-2`.
- `STRONG_OUTFLOW` otherwise.

## Quick Start

From `08-institutional-tide`:

```bash
python -m pip install -e ".[dev]"
python -m src run --mode fixture --output-dir output
python -m pytest tests -v
```

The verified portable CLI path is `python -m src run --mode fixture`. The CLI test runs that command in a subprocess from the project root, so it does not depend on a shell alias or a console entry point.

Fixture mode requires no credentials and makes no network calls.

## Generated Outputs

The CLI prints the latest flow snapshot, momentum score and components, tide level, historical reaction, YAML strategy card, and backtest results. When `--output-dir` is supplied, it writes:

- `output/strategy.yaml`
- `output/strategy.md`

The checked-in fixture outputs contain:

- `tide_level: STRONG_INFLOW`
- `sample_size: 24`
- `median_7d_return: 0.015453`
- `median_14d_return: -0.062069`
- `hit_rate: 0.5417`
- `position_sizing: 100% of portfolio`
- `max_drawdown_stop: -0.12`
- `rebalance_on_level_change: true`

## Project Map

- `src/__main__.py` wires the CLI, fixture pipeline, printed report, output writing, and live-mode boundary.
- `src/fixtures/loader.py` loads ETF flow, price, and global market fixtures.
- `src/momentum.py` computes the flow momentum score and score components.
- `src/classifier.py` maps scores to tide levels.
- `src/emitter.py` builds the strategy card and renders YAML/Markdown.
- `src/backtest.py` replays the allocation map against fixture prices.
- `src/models.py` defines the typed dataclasses used across the pipeline.
- `fixtures/` stores the evidence inputs.
- `output/` stores reproducible sample strategy cards.
- `tests/` covers loaders, momentum scoring, classification, card rendering, portable CLI execution, backtest, and the full pipeline.

## Verification

Run the full test suite from `08-institutional-tide`:

```bash
python -m pytest tests -v
```

The tests assert fixture loading, score clamping, tide thresholds, YAML parseability, Markdown rendering, subprocess CLI execution through `python -m src`, backtest shape, and end-to-end pipeline behavior.

## Safety And Live Mode Boundary

- No live trading.
- No wallet execution.
- No orders, swaps, transfers, private keys, or transaction signing.
- No capital is required.
- Fixture mode is the supported review path and works without credentials.
- The CLI accepts `--mode live`, but it exits with a message that CMC API credentials would be required. No CMC client or live data path is implemented in this project.
