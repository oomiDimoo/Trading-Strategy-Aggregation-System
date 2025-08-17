import pytest
import pandas as pd
import numpy as np

from strategies.ichimoku_cloud_strategy import IchimokuCloudStrategy

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

def test_ichimoku_cloud_strategy_init_defaults():
    """Test IchimokuCloudStrategy initialization with default parameters."""
    strategy = IchimokuCloudStrategy(name="IchimokuCloud_default")
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    defaults = config['strategy_defaults']['IchimokuCloudStrategy']

    assert strategy.name == "IchimokuCloud_default"
    assert strategy.tenkan_period == defaults['tenkan_period']
    assert strategy.kijun_period == defaults['kijun_period']
    assert strategy.senkou_b_period == defaults['senkou_b_period']
    assert strategy.displacement == defaults['displacement']


def test_ichimoku_cloud_strategy_init_custom():
    """Test IchimokuCloudStrategy initialization with custom parameters."""
    params = {
        "tenkan_period": 10,
        "kijun_period": 30,
        "senkou_b_period": 60,
        "displacement": 30
    }
    strategy = IchimokuCloudStrategy(name="IchimokuCloud_custom", parameters=params)
    assert strategy.name == "IchimokuCloud_custom"
    assert strategy.tenkan_period == 10
    assert strategy.kijun_period == 30
    assert strategy.senkou_b_period == 60
    assert strategy.displacement == 30


def test_ichimoku_cloud_strategy_process_data(market_data):
    """Test IchimokuCloudStrategy signal generation."""
    strategy = IchimokuCloudStrategy(name="IchimokuCloud")
    signals = strategy.process_data(market_data)
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns
    assert "tenkan_sen" in signals.columns
    assert "kijun_sen" in signals.columns
    assert "senkou_span_a" in signals.columns
    assert "senkou_span_b" in signals.columns
    assert "chikou_span" in signals.columns


def test_ichimoku_cloud_strategy_process_empty_data():
    """Test IchimokuCloudStrategy with empty data."""
    strategy = IchimokuCloudStrategy(name="IchimokuCloud")
    signals = strategy.process_data(pd.DataFrame())
    assert signals.empty


def test_ichimoku_signal_correctness():
    """Test Ichimoku Cloud signal correctness with a known dataset."""
    # Create a dataset with a clear bullish crossover
    close_prices = np.linspace(100, 150, 60)
    high_prices = close_prices * 1.01
    low_prices = close_prices * 0.99
    dates = pd.date_range(start="2023-01-01", periods=len(close_prices))
    data = pd.DataFrame({"close": close_prices, "high": high_prices, "low": low_prices}, index=dates)

    strategy = IchimokuCloudStrategy(
        name="Ichimoku_test",
        parameters={
            "tenkan_period": 9,
            "kijun_period": 26,
            "senkou_b_period": 52,
            "displacement": 26
        }
    )

    signals = strategy.process_data(data)

    # Find the first point where Tenkan-sen crosses above Kijun-sen
    buy_signal_day = signals[(signals['tenkan_sen'] > signals['kijun_sen']) & (signals['tenkan_sen'].shift(1) <= signals['kijun_sen'].shift(1))].index

    if not buy_signal_day.empty:
        assert signals.loc[buy_signal_day[0]]['signal'] == 1
