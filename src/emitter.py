"""Strategy emitter for Institutional Tide."""
from __future__ import annotations

import yaml

from src.models import StrategyCard, StrategyConfig, TideLevel, TideReaction


def emit_strategy(
    tide: TideLevel,
    reaction: TideReaction,
    config: StrategyConfig,
) -> StrategyCard:
    alloc = config.allocation_map.get(tide, 0.5)
    return StrategyCard(
        tide=tide,
        reaction=reaction,
        config=config,
        entry_rule=f"Enter {alloc*100:.0f}% position when tide == {tide.value}",
        exit_rule="Exit to 0% on STRONG_OUTFLOW or max-drawdown stop triggered",
        position_sizing=f"{alloc*100:.0f}% of portfolio",
        invalidation=f"Drawdown exceeds {config.max_drawdown_stop*100:.0f}%",
    )


def render_yaml(card: StrategyCard) -> str:
    data = {
        "strategy": "Institutional Tide",
        "tide_level": card.tide.value,
        "reaction": {
            "sample_size": card.reaction.sample_size,
            "median_7d_return": card.reaction.median_7d_return,
            "median_14d_return": card.reaction.median_14d_return,
            "hit_rate": card.reaction.hit_rate,
        },
        "entry_rule": card.entry_rule,
        "exit_rule": card.exit_rule,
        "position_sizing": card.position_sizing,
        "invalidation": card.invalidation,
        "max_drawdown_stop": card.config.max_drawdown_stop,
        "rebalance_on_level_change": card.config.rebalance_on_level_change,
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def render_markdown(card: StrategyCard) -> str:
    lines = [
        "# Institutional Tide Strategy Card",
        "",
        f"**Tide Level:** {card.tide.value}",
        f"**Entry Rule:** {card.entry_rule}",
        f"**Exit Rule:** {card.exit_rule}",
        f"**Position Sizing:** {card.position_sizing}",
        f"**Invalidation:** {card.invalidation}",
        "",
        "## Historical Reaction",
        "",
        f"- Sample size: {card.reaction.sample_size}",
        f"- Median 7d return: {card.reaction.median_7d_return:.2%}",
        f"- Median 14d return: {card.reaction.median_14d_return:.2%}",
        f"- Hit rate: {card.reaction.hit_rate:.1%}",
        "",
        "## Risk",
        "",
        f"- Max drawdown stop: {card.config.max_drawdown_stop:.0%}",
        f"- Rebalance on level change: {card.config.rebalance_on_level_change}",
    ]
    return "\n".join(lines) + "\n"
