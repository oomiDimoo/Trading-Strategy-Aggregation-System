import pytest
import pandas as pd
import numpy as np

from aggregator.signal_aggregator import SignalAggregator

@pytest.fixture
def sample_signals():
    """Fixture for a list of sample signal DataFrames."""
    dates = pd.date_range(start="2023-01-01", periods=5)
    signals1 = pd.DataFrame({
        "signal": [0.8, 0.6, 0.4, 0.2, 0.0],
        "binary_signal": [1, 1, 0, 0, 0],
        "weight": [1.0] * 5
    }, index=dates)
    signals2 = pd.DataFrame({
        "signal": [0.1, 0.3, 0.5, 0.7, 0.9],
        "binary_signal": [0, 0, 1, 1, 1],
        "weight": [0.5] * 5
    }, index=dates)
    return [signals1, signals2]

def test_signal_aggregator_init():
    """Test SignalAggregator initialization."""
    config = {"method": "weighted_average", "threshold": 0.6}
    aggregator = SignalAggregator(config)
    assert aggregator.method == "weighted_average"
    assert aggregator.threshold == 0.6

def test_weighted_average_aggregation(sample_signals):
    """Test weighted_average aggregation method."""
    aggregator = SignalAggregator(config={"method": "weighted_average"})
    aggregated = aggregator.aggregate(sample_signals)
    assert isinstance(aggregated, pd.DataFrame)
    assert "signal" in aggregated.columns
    # Manual calculation for the first element: (0.8 * 1.0 + 0.1 * 0.5) / (1.0 + 0.5) = 0.85 / 1.5 = 0.5666...
    assert np.isclose(aggregated["signal"].iloc[0], 0.56666666)

def test_majority_vote_aggregation(sample_signals):
    """Test majority_vote aggregation method."""
    aggregator = SignalAggregator(config={"method": "majority_vote", "threshold": 0.5})
    aggregated = aggregator.aggregate(sample_signals)
    assert isinstance(aggregated, pd.DataFrame)
    assert "binary_signal" in aggregated.columns
    # Manual calculation for the first element: (1 * 1.0 + 0 * 0.5) / (1.0 + 0.5) = 1.0 / 1.5 = 0.666... > 0.5 -> 1
    assert aggregated["binary_signal"].iloc[0] == 1
    # Manual calculation for the third element: (0 * 1.0 + 1 * 0.5) / (1.0 + 0.5) = 0.5 / 1.5 = 0.333... < 0.5 -> 0
    assert aggregated["binary_signal"].iloc[2] == 0


def test_consensus_aggregation(sample_signals):
    """Test consensus aggregation method."""
    aggregator = SignalAggregator(config={"method": "consensus"})
    # Modify signals to have a consensus
    sample_signals[0]["binary_signal"] = [1, 0, 1, 0, 1]
    sample_signals[1]["binary_signal"] = [1, 0, 0, 1, 1]
    aggregated = aggregator.aggregate(sample_signals)
    assert isinstance(aggregated, pd.DataFrame)
    assert "binary_signal" in aggregated.columns
    assert aggregated["binary_signal"].iloc[0] == 1.0 # Consensus buy
    assert aggregated["binary_signal"].iloc[1] == 0.0 # Consensus sell
    assert aggregated["binary_signal"].iloc[2] == 0.5 # No consensus
    assert aggregated["binary_signal"].iloc[3] == 0.5 # No consensus
    assert aggregated["binary_signal"].iloc[4] == 1.0 # Consensus buy
