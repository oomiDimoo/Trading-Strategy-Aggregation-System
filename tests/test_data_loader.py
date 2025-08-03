import pytest
import pandas as pd
from data.data_loader import DataLoader

@pytest.fixture
def sample_config():
    """Fixture for a sample DataLoader configuration."""
    return {
        "type": "sample",
        "symbol": "TEST",
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "timeframe": "1d"
    }

def test_data_loader_init(sample_config):
    """Test DataLoader initialization."""
    loader = DataLoader(sample_config)
    assert loader.source_type == "sample"
    assert loader.symbol == "TEST"

def test_load_sample_data(sample_config):
    """Test loading sample data."""
    loader = DataLoader(sample_config)
    data = loader.load_data()
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert "close" in data.columns
    assert "volume" in data.columns

def test_load_from_csv(mocker):
    """Test loading data from a CSV file."""
    # Create a mock CSV file
    csv_data = "date,open,high,low,close,volume\n2023-01-01,100,105,99,102,1000\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=csv_data))
    mocker.patch("os.path.exists", return_value=True)

    config = {
        "type": "csv",
        "path": "dummy/path.csv"
    }
    loader = DataLoader(config)
    data = loader.load_data()

    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert data.shape[0] == 1
    assert data.iloc[0]["close"] == 102
