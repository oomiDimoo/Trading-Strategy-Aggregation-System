import pytest
import pandas as pd
import numpy as np

from strategies.moving_average_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy

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


def test_moving_average_crossover_init():
    """Test MovingAverageCrossover strategy initialization."""
    params = {"fast_period": 10, "slow_period": 30}
    strategy = MovingAverageCrossover(name="MACrossover", parameters=params)
    assert strategy.name == "MACrossover"
    assert strategy.fast_period == 10
    assert strategy.slow_period == 30


def test_moving_average_crossover_process_data(market_data):
    """Test MovingAverageCrossover signal generation."""
    strategy = MovingAverageCrossover(name="MACrossover", parameters={"fast_period": 10, "slow_period": 30})
    signals = strategy.process_data(market_data)
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns
    assert not signals["signal"].empty


def test_rsi_strategy_init():
    """Test RSIStrategy initialization."""
    params = {"period": 14, "overbought": 70, "oversold": 30}
    strategy = RSIStrategy(name="RSI", parameters=params)
    assert strategy.name == "RSI"
    assert strategy.period == 14
    assert strategy.overbought == 70
    assert strategy.oversold == 30


def test_rsi_strategy_process_data(market_data):
    """Test RSIStrategy signal generation."""
    strategy = RSIStrategy(name="RSI", parameters={"period": 14})
    signals = strategy.process_data(market_data)
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns
    assert "rsi" in signals.columns
    assert not signals["signal"].empty
