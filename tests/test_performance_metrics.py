import pytest
import pandas as pd
import numpy as np

from reports.performance_metrics import (
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_profit_factor,
)

@pytest.fixture
def returns_data():
    """Fixture for sample returns data."""
    returns = np.random.normal(0.001, 0.02, 252)
    return pd.Series(returns)

def test_calculate_sharpe_ratio(returns_data):
    """Test Sharpe ratio calculation."""
    sharpe_ratio = calculate_sharpe_ratio(returns_data)
    assert isinstance(sharpe_ratio, float)

def test_calculate_sortino_ratio(returns_data):
    """Test Sortino ratio calculation."""
    sortino_ratio = calculate_sortino_ratio(returns_data)
    assert isinstance(sortino_ratio, float)

def test_calculate_max_drawdown(returns_data):
    """Test max drawdown calculation."""
    max_drawdown = calculate_max_drawdown(returns_data)
    assert isinstance(max_drawdown, float)
    assert max_drawdown <= 0

def test_calculate_profit_factor(returns_data):
    """Test profit factor calculation."""
    profit_factor = calculate_profit_factor(returns_data)
    assert isinstance(profit_factor, float)
    assert profit_factor >= 0
