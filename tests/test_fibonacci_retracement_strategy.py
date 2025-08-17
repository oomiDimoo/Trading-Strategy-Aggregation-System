import pytest
import pandas as pd
import numpy as np

from strategies.fibonacci_retracement_strategy import FibonacciRetracementStrategy

@pytest.fixture
def market_data():
    """Fixture for sample market data."""
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = {
        "open": np.random.uniform(95, 105, size=100),
        "high": np.random.uniform(100, 110, size=100),
        "low": np.random.uniform(90, 100, size=100),
        "close": np.random.uniform(98, 108, size=100),
        "volume": np.random.uniform(10000, 50000, size=100),
    }
    return pd.DataFrame(data, index=dates)


import json

def test_fibonacci_retracement_strategy_init_defaults():
    """Test FibonacciRetracementStrategy initialization with default parameters."""
    strategy = FibonacciRetracementStrategy(name="FibonacciRetracement_default")
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    defaults = config['strategy_defaults']['FibonacciRetracementStrategy']

    assert strategy.name == "FibonacciRetracement_default"
    assert strategy.trend_period == defaults['trend_period']
    assert strategy.swing_lookback == defaults['swing_lookback']
    assert strategy.retracement_levels == defaults['retracement_levels']
    assert strategy.level_tolerance == defaults['level_tolerance']


def test_fibonacci_retracement_strategy_init_custom():
    """Test FibonacciRetracementStrategy initialization with custom parameters."""
    params = {
        "trend_period": 30,
        "swing_lookback": 15,
        "retracement_levels": [0.382, 0.5, 0.618],
        "level_tolerance": 0.02
    }
    strategy = FibonacciRetracementStrategy(name="FibonacciRetracement_custom", parameters=params)
    assert strategy.name == "FibonacciRetracement_custom"
    assert strategy.trend_period == 30
    assert strategy.swing_lookback == 15
    assert strategy.retracement_levels == [0.382, 0.5, 0.618]
    assert strategy.level_tolerance == 0.02


def test_fibonacci_retracement_strategy_process_data(market_data):
    """Test FibonacciRetracementStrategy signal generation."""
    strategy = FibonacciRetracementStrategy(name="FibonacciRetracement")
    # Ensure there's enough data for the default parameters
    market_data_long = market_data.copy().iloc[0:80]
    signals = strategy.process_data(market_data_long)
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns


def test_fibonacci_retracement_strategy_process_empty_data():
    """Test FibonacciRetracementStrategy with empty data."""
    strategy = FibonacciRetracementStrategy(name="FibonacciRetracement")
    signals = strategy.process_data(pd.DataFrame())
    assert signals.empty


def test_fibonacci_signal_correctness():
    """Test Fibonacci Retracement signal correctness with a known dataset."""
    # Create a dataset with a clear uptrend and retracement
    close_prices = [100, 102, 104, 106, 108, 110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 90, 92, 94, 96, 98, 100]
    high_prices = [101, 103, 105, 107, 109, 111, 109, 107, 105, 103, 101, 99, 97, 95, 93, 91, 93, 95, 97, 99, 101]
    low_prices = [99, 101, 103, 105, 107, 109, 107, 105, 103, 101, 99, 97, 95, 93, 91, 89, 91, 93, 95, 97, 99]
    dates = pd.date_range(start="2023-01-01", periods=len(close_prices))
    data = pd.DataFrame({"close": close_prices, "high": high_prices, "low": low_prices}, index=dates)

    strategy = FibonacciRetracementStrategy(
        name="Fibonacci_test",
        parameters={
            "trend_period": 10,
            "swing_lookback": 5,
            "retracement_levels": [0.5],
            "level_tolerance": 0.02
        }
    )

    # We need to extend the data to have enough points for the trend and lookback
    extended_data = pd.concat([data] * 5, ignore_index=True)
    extended_data.index = pd.date_range(start="2023-01-01", periods=len(extended_data))

    signals = strategy.process_data(extended_data)

    # Check for a buy signal at a retracement level
    assert 1 in signals['signal'].values
