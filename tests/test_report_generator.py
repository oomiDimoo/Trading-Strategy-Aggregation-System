import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock

from reports.report_generator import ReportGenerator

@pytest.fixture
def sample_market_data():
    """Fixture for sample market data."""
    dates = pd.date_range(start="2023-01-01", periods=10)
    return pd.DataFrame({
        "close": [100 + i for i in range(10)]
    }, index=dates)

@pytest.fixture
def sample_strategy_signals():
    """Fixture for sample strategy signals."""
    dates = pd.date_range(start="2023-01-01", periods=10)
    signals1 = pd.DataFrame({
        "signal": [0.8, 0.6, 0.4, 0.2, 0.0, 0.1, 0.3, 0.5, 0.7, 0.9],
        "binary_signal": [1, 1, 0, 0, 0, 0, 0, 1, 1, 1],
        "strategy": ["MACD"] * 10,
        "weight": [1.0] * 10,
        "signal_type": ["trend_following"] * 10
    }, index=dates)
    return [signals1]

@pytest.fixture
def sample_aggregated_signal():
    """Fixture for sample aggregated signal."""
    dates = pd.date_range(start="2023-01-01", periods=10)
    return pd.DataFrame({
        "signal": [0.4, 0.3, 0.2, 0.1, 0.0, 0.05, 0.15, 0.25, 0.35, 0.45],
        "binary_signal": [0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
    }, index=dates)

@pytest.fixture
def sample_strategy_metadata():
    """Fixture for sample strategy metadata."""
    return [{"strategy_name": "MACD", "weight": 1.0, "num_trades": 5}]

def test_report_generator_init(tmpdir):
    """Test ReportGenerator initialization."""
    config = {"output_dir": str(tmpdir)}
    generator = ReportGenerator(config)
    assert generator.output_dir == str(tmpdir)
    assert os.path.exists(str(tmpdir))

@patch("matplotlib.pyplot.savefig")
def test_generate_html_report(mock_savefig, tmpdir, sample_market_data, sample_strategy_signals, sample_aggregated_signal, sample_strategy_metadata):
    """Test HTML report generation."""
    config = {"output_dir": str(tmpdir), "format": "html", "include_plots": True}
    generator = ReportGenerator(config)
    report_path = generator.generate_report(
        market_data=sample_market_data,
        strategy_signals=sample_strategy_signals,
        aggregated_signal=sample_aggregated_signal,
        strategy_metadata=sample_strategy_metadata
    )
    assert os.path.exists(report_path)
    assert report_path.endswith(".html")
    with open(report_path, "r") as f:
        content = f.read()
    assert "<h1>Trading Strategy Report</h1>" in content
    assert "<h2>Strategy Summary</h2>" in content
    assert mock_savefig.called

@patch("matplotlib.pyplot.savefig")
def test_generate_csv_report(mock_savefig, tmpdir, sample_market_data, sample_strategy_signals, sample_aggregated_signal, sample_strategy_metadata):
    """Test CSV report generation."""
    config = {"output_dir": str(tmpdir), "format": "csv", "include_plots": False}
    generator = ReportGenerator(config)
    report_path = generator.generate_report(
        market_data=sample_market_data,
        strategy_signals=sample_strategy_signals,
        aggregated_signal=sample_aggregated_signal,
        strategy_metadata=sample_strategy_metadata
    )
    assert os.path.exists(report_path)
    assert report_path.endswith(".csv")
    df = pd.read_csv(report_path)
    assert "aggregated_signal" in df.columns
    assert "MACD_signal" in df.columns
    assert not mock_savefig.called
