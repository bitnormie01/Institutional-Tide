"""Tests for the CLI entry point."""
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_fixture_mode():
    result = subprocess.run(
        [sys.executable, "-m", "src", "run", "--mode", "fixture"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert "INSTITUTIONAL TIDE" in result.stdout
    assert "Momentum Score" in result.stdout
    assert "BACKTEST RESULTS" in result.stdout
