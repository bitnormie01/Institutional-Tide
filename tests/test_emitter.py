"""Tests for the strategy emitter."""
import yaml

from src.emitter import emit_strategy, render_yaml, render_markdown
from src.models import StrategyCard, StrategyConfig, TideLevel, TideReaction


def _reaction() -> TideReaction:
    return TideReaction(
        tide_level=TideLevel.STRONG_INFLOW,
        sample_size=12,
        median_7d_return=0.035,
        median_14d_return=0.068,
        hit_rate=0.73,
    )


def test_strong_inflow_100pct():
    config = StrategyConfig()
    card = emit_strategy(TideLevel.STRONG_INFLOW, _reaction(), config)
    assert isinstance(card, StrategyCard)
    assert "100%" in card.position_sizing


def test_yaml_parseable():
    config = StrategyConfig()
    card = emit_strategy(TideLevel.STRONG_INFLOW, _reaction(), config)
    text = render_yaml(card)
    parsed = yaml.safe_load(text)
    assert parsed["tide_level"] == "STRONG_INFLOW"


def test_markdown_rendering():
    config = StrategyConfig()
    card = emit_strategy(TideLevel.MILD_INFLOW, _reaction(), config)
    md = render_markdown(card)
    assert "MILD_INFLOW" in md
