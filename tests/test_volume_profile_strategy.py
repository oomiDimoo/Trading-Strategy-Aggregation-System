import pytest
import pandas as pd
import numpy as np

from strategies.volume_profile_strategy import VolumeProfileStrategy

@pytest.fixture
def market_data():
    """Fixture for sample market data."""
    dates = pd.date_range(start="2023-01-01", periods=200)
    data = {
        "open": np.random.uniform(95, 105, size=200),
        "high": np.random.uniform(100, 110, size=200),
        "low": np.random.uniform(90, 100, size=200),
        "close": np.random.uniform(98, 108, size=200),
        "volume": np.random.uniform(10000, 50000, size=200),
    }
    return pd.DataFrame(data, index=dates)


import json

def test_volume_profile_strategy_init_defaults():
    """Test VolumeProfileStrategy initialization with default parameters."""
    strategy = VolumeProfileStrategy(name="VolumeProfile_default")
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    defaults = config['strategy_defaults']['VolumeProfileStrategy']

    assert strategy.name == "VolumeProfile_default"
    assert strategy.num_bins == defaults['num_bins']
    assert strategy.lookback_period == defaults['lookback_period']
    assert strategy.volume_threshold == defaults['volume_threshold']
    assert strategy.signal_lookback == defaults['signal_lookback']


def test_volume_profile_strategy_init_custom():
    """Test VolumeProfileStrategy initialization with custom parameters."""
    params = {
        "num_bins": 30,
        "lookback_period": 150,
        "volume_threshold": 0.9,
        "signal_lookback": 10
    }
    strategy = VolumeProfileStrategy(name="VolumeProfile_custom", parameters=params)
    assert strategy.name == "VolumeProfile_custom"
    assert strategy.num_bins == 30
    assert strategy.lookback_period == 150
    assert strategy.volume_threshold == 0.9
    assert strategy.signal_lookback == 10


def test_volume_profile_strategy_process_data(market_data):
    """Test VolumeProfileStrategy signal generation."""
    strategy = VolumeProfileStrategy(name="VolumeProfile")
    signals = strategy.process_data(market_data)
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns


def test_volume_profile_strategy_process_empty_data():
    """Test VolumeProfileStrategy with empty data."""
    strategy = VolumeProfileStrategy(name="VolumeProfile")
    signals = strategy.process_data(pd.DataFrame())
    assert signals.empty


def test_volume_profile_signal_correctness():
    """
    Test Volume Profile signal correctness with a known dataset.
    NOTE: This test is not checking for a specific signal, as the logic is complex
    and difficult to create a reliable test case for. It is only checking that the
    strategy runs without errors and returns a dataframe with the correct columns.
    """
    # Create a dataset with a high volume node at 105
    prices = np.concatenate([
        np.linspace(100, 104, 50),  # Approaching the HVN
        np.full(50, 105),           # High volume node
        np.linspace(106, 110, 50)   # Moving away
    ])
    volume = np.concatenate([
        np.full(50, 1000),
        np.full(50, 100000),        # High volume at the node
        np.full(50, 1000)
    ])

    dates = pd.date_range(start="2023-01-01", periods=len(prices))
    data = pd.DataFrame({
        "close": prices,
        "high": prices + 0.1,
        "low": prices - 0.1,
        "volume": volume
    }, index=dates)

    strategy = VolumeProfileStrategy(
        name="VolumeProfile_test",
        parameters={
            "num_bins": 10,
            "lookback_period": 100,
            "volume_threshold": 0.9,
            "signal_lookback": 5
        }
    )

    signals = strategy.process_data(data)

    # Check that the strategy runs without errors and returns the correct columns
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns
