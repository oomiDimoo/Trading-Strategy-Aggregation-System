import pytest
from data.data_loader import DataLoader

def test_load_data_unknown_source():
    """Test that DataLoader raises ValueError for an unknown data source."""
    config = {"type": "unknown"}
    loader = DataLoader(config)
    with pytest.raises(ValueError, match="Unknown data source type: unknown"):
        loader.load_data()

def test_load_from_csv_not_found():
    """Test that loading a non-existent CSV raises FileNotFoundError."""
    config = {"type": "csv", "path": "non_existent_file.csv"}
    loader = DataLoader(config)
    with pytest.raises(FileNotFoundError):
        loader.load_data()

def test_load_from_csv_missing_columns(mocker):
    """Test that a CSV with missing columns raises ValueError."""
    csv_data = "date,open,high,low\n2023-01-01,100,105,99\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=csv_data))
    mocker.patch("os.path.exists", return_value=True)
    config = {"type": "csv", "path": "dummy.csv"}
    loader = DataLoader(config)
    with pytest.raises(ValueError, match="CSV file missing required columns"):
        loader.load_data()

def test_load_from_yfinance_importerror(mocker):
    """Test that a yfinance import error is handled."""
    mocker.patch.dict("sys.modules", {"yfinance": None})
    config = {"type": "yfinance", "symbol": "AAPL"}
    loader = DataLoader(config)
    with pytest.raises(ImportError, match="yfinance package not installed"):
        loader.load_data()

def test_load_from_alpha_vantage_importerror(mocker):
    """Test that an alpha_vantage import error is handled."""
    mocker.patch.dict("sys.modules", {"alpha_vantage.timeseries": None})
    config = {"type": "alpha_vantage", "symbol": "IBM", "api_key": "TESTKEY"}
    loader = DataLoader(config)
    with pytest.raises(ImportError, match="alpha_vantage package not installed"):
        loader.load_data()

def test_load_from_alpha_vantage_no_api_key():
    """Test that missing Alpha Vantage API key raises ValueError."""
    config = {"type": "alpha_vantage", "symbol": "IBM"}
    loader = DataLoader(config)
    with pytest.raises(ValueError, match="Alpha Vantage API key not provided"):
        loader.load_data()
