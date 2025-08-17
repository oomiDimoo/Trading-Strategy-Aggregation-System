import pytest
import pandas as pd
import numpy as np

from strategies.macd_strategy import MACDStrategy

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


def test_macd_strategy_init_defaults():
    """Test MACDStrategy initialization with default parameters."""
    strategy = MACDStrategy(name="MACD_default")
    assert strategy.name == "MACD_default"
    assert strategy.fast_period == 12
    assert strategy.slow_period == 26
    assert strategy.signal_period == 9


def test_macd_strategy_init_custom():
    """Test MACDStrategy initialization with custom parameters."""
    params = {"fast_period": 10, "slow_period": 30, "signal_period": 5}
    strategy = MACDStrategy(name="MACD_custom", parameters=params)
    assert strategy.name == "MACD_custom"
    assert strategy.fast_period == 10
    assert strategy.slow_period == 30
    assert strategy.signal_period == 5


def test_macd_strategy_process_data(market_data):
    """Test MACDStrategy signal generation."""
    strategy = MACDStrategy(name="MACD", parameters={"fast_period": 12, "slow_period": 26, "signal_period": 9})
    signals = strategy.process_data(market_data)
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns
    assert "macd_line" in signals.columns
    assert "signal_line" in signals.columns
    assert "histogram" in signals.columns
    assert not signals["signal"].empty

def test_macd_signal_correctness():
    """Test MACD signal correctness with a known dataset."""
    close_prices = [
        100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
        110, 109, 108, 107, 106, 105, 104, 103, 102, 101
    ]
    dates = pd.date_range(start="2023-01-01", periods=len(close_prices))
    data = pd.DataFrame({"close": close_prices}, index=dates)

    strategy = MACDStrategy(name="MACD_test", parameters={"fast_period": 5, "slow_period": 10, "signal_period": 4})
    signals = strategy.process_data(data)

    # Check for a crossover event
    # Find the first point where MACD is above the signal line
    buy_signal_day = signals[(signals['macd_line'] > signals['signal_line'])].index[0]
    # Find the first point where MACD is below the signal line after the buy signal
    sell_signal_day = signals[(signals.index > buy_signal_day) & (signals['macd_line'] < signals['signal_line'])].index[0]

    assert signals.loc[buy_signal_day]['signal'] == 1
    assert signals.loc[sell_signal_day]['signal'] == -1


def test_macd_strategy_process_empty_data():
    """Test MACDStrategy with empty data."""
    strategy = MACDStrategy(name="MACD")
    signals = strategy.process_data(pd.DataFrame())
    assert signals.empty
