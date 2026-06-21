"""Tests for the tide classifier."""
from src.classifier import classify_tide
from src.models import TideLevel


def test_strong_inflow():
    assert classify_tide(3.0) == TideLevel.STRONG_INFLOW


def test_mild_inflow():
    assert classify_tide(1.5) == TideLevel.MILD_INFLOW


def test_neutral():
    assert classify_tide(0.0) == TideLevel.NEUTRAL


def test_mild_outflow():
    assert classify_tide(-1.5) == TideLevel.MILD_OUTFLOW


def test_strong_outflow():
    assert classify_tide(-3.0) == TideLevel.STRONG_OUTFLOW
