import pytest
import pandas as pd
import numpy as np

from strategies.bollinger_bands_strategy import BollingerBandsStrategy

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

def test_bollinger_bands_strategy_init_defaults():
    """Test BollingerBandsStrategy initialization with default parameters."""
    strategy = BollingerBandsStrategy(name="BollingerBands_default")
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    defaults = config['strategy_defaults']['BollingerBandsStrategy']

    assert strategy.name == "BollingerBands_default"
    assert strategy.period == defaults['period']
    assert strategy.std_dev == defaults['std_dev']
    assert strategy.price_source == defaults['price_source']


def test_bollinger_bands_strategy_init_custom():
    """Test BollingerBandsStrategy initialization with custom parameters."""
    params = {"period": 10, "std_dev": 1.5, "price_source": "high"}
    strategy = BollingerBandsStrategy(name="BollingerBands_custom", parameters=params)
    assert strategy.name == "BollingerBands_custom"
    assert strategy.period == 10
    assert strategy.std_dev == 1.5
    assert strategy.price_source == "high"


def test_bollinger_bands_strategy_process_data(market_data):
    """Test BollingerBandsStrategy signal generation."""
    strategy = BollingerBandsStrategy(name="BollingerBands", parameters={"period": 20, "std_dev": 2.0})
    signals = strategy.process_data(market_data)
    assert isinstance(signals, pd.DataFrame)
    assert "signal" in signals.columns
    assert "middle_band" in signals.columns
    assert "upper_band" in signals.columns
    assert "lower_band" in signals.columns
    assert not signals["signal"].empty

    # Check for advanced performance metrics
    metadata = strategy.get_metadata()
    assert "sharpe_ratio" in metadata
    assert "sortino_ratio" in metadata
    assert "max_drawdown" in metadata
    assert "profit_factor" in metadata

def test_bollinger_bands_signal_correctness():
    """Test BollingerBands signal correctness with a known dataset."""
    close_prices = [
        100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
        110, 115, 108, 107, 106, 105, 104, 103, 102, 101, 90
    ]
    dates = pd.date_range(start="2023-01-01", periods=len(close_prices))
    data = pd.DataFrame({"close": close_prices}, index=dates)

    strategy = BollingerBandsStrategy(name="BollingerBands_test", parameters={"period": 10, "std_dev": 2.0})
    signals = strategy.process_data(data)

    # Find the first point where price is above the upper band
    sell_signal_day = signals[signals['price'] > signals['upper_band']].index[0]

    # Find the first point where price is below the lower band
    buy_signal_day = signals[signals['price'] < signals['lower_band']].index[0]

    assert signals.loc[sell_signal_day]['signal'] == -1
    assert signals.loc[buy_signal_day]['signal'] == 1


def test_bollinger_bands_strategy_process_empty_data():
    """Test BollingerBandsStrategy with empty data."""
    strategy = BollingerBandsStrategy(name="BollingerBands")
    signals = strategy.process_data(pd.DataFrame())
    assert signals.empty
