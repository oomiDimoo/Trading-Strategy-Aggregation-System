#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Loads market data from various sources for use in trading strategies.
    
    This class handles importing data from CSV files, APIs, or other sources,
    and preprocessing it into a standardized format for strategy processing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the data loader.
        
        Args:
            config: Configuration dictionary for the data loader
        """
        self.config = config or {}
        self.source_type = self.config.get("type", "csv")
        self.source_path = self.config.get("path", "data/sample_data.csv")
        self.start_date = self.config.get("start_date", None)
        self.end_date = self.config.get("end_date", None)
        self.symbol = self.config.get("symbol", "AAPL")
        self.timeframe = self.config.get("timeframe", "1d")
        self.metadata = {}
    
    def load_data(self) -> pd.DataFrame:
        """
        Load market data based on configuration.
        
        Returns:
            DataFrame containing market data (OHLCV)
        """
        if self.source_type == "csv":
            return self._load_from_csv()
        elif self.source_type == "yfinance":
            return self._load_from_yfinance()
        elif self.source_type == "alpha_vantage":
            return self._load_from_alpha_vantage()
        elif self.source_type == "sample":
            return self._generate_sample_data()
        else:
            raise ValueError(f"Unknown data source type: {self.source_type}")
    
    def _load_from_csv(self) -> pd.DataFrame:
        """
        Load market data from a CSV file.
        
        Returns:
            DataFrame containing market data
        """
        # Check if file exists
        if not os.path.exists(self.source_path):
            raise FileNotFoundError(f"CSV file not found: {self.source_path}")

        # Load data from CSV
        df = pd.read_csv(self.source_path)

        # Ensure required columns exist
        required_columns = ["date", "open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"CSV file missing required columns: {missing_columns}")

        # Convert date column to datetime
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        # Filter by date range if specified
        if self.start_date:
            start_date = pd.to_datetime(self.start_date)
            df = df[df.index >= start_date]

        if self.end_date:
            end_date = pd.to_datetime(self.end_date)
            df = df[df.index <= end_date]

        # Ensure column names are standardized
        df.columns = [col.lower() for col in df.columns]

        # Set metadata
        self.metadata = {
            "source": "csv",
            "path": self.source_path,
            "rows": len(df),
            "start_date": df.index.min().strftime("%Y-%m-%d") if not df.empty else None,
            "end_date": df.index.max().strftime("%Y-%m-%d") if not df.empty else None
        }

        return df
    
    def _load_from_yfinance(self) -> pd.DataFrame:
        """
        Load market data from Yahoo Finance API.
        
        Returns:
            DataFrame containing market data
        """
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("yfinance package not installed. Please install it with: pip install yfinance")

        # Set default date range if not specified
        end_date = pd.to_datetime(self.end_date) if self.end_date else datetime.now()
        start_date = pd.to_datetime(self.start_date) if self.start_date else end_date - timedelta(days=365)

        # Download data
        df = yf.download(
            self.symbol,
            start=start_date,
            end=end_date,
            interval=self.timeframe,
            progress=False
        )

        if df.empty:
            raise ValueError(f"No data found for symbol {self.symbol} from yfinance.")

        # Rename columns to lowercase
        df.columns = [col.lower() for col in df.columns]

        # Set metadata
        self.metadata = {
            "source": "yfinance",
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "rows": len(df),
            "start_date": df.index.min().strftime("%Y-%m-%d") if not df.empty else None,
            "end_date": df.index.max().strftime("%Y-%m-%d") if not df.empty else None
        }

        return df
    
    def _load_from_alpha_vantage(self) -> pd.DataFrame:
        """
        Load market data from Alpha Vantage API.
        
        Returns:
            DataFrame containing market data
        """
        try:
            from alpha_vantage.timeseries import TimeSeries
        except ImportError:
            raise ImportError("alpha_vantage package not installed. Please install it with: pip install alpha_vantage")

        # Get API key from config
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("Alpha Vantage API key not provided in the configuration.")

        # Initialize Alpha Vantage API
        ts = TimeSeries(key=api_key, output_format='pandas')

        # Get data based on timeframe
        try:
            if self.timeframe == "1d":
                data, meta_data = ts.get_daily(symbol=self.symbol, outputsize='full')
            elif self.timeframe == "1h":
                data, meta_data = ts.get_intraday(symbol=self.symbol, interval='60min', outputsize='full')
            else:
                logger.warning(f"Unsupported timeframe for Alpha Vantage: {self.timeframe}, using daily")
                data, meta_data = ts.get_daily(symbol=self.symbol, outputsize='full')
        except ValueError as e:
            # Catch potential errors from the API, e.g., invalid symbol
            raise ValueError(f"Error fetching data from Alpha Vantage for symbol {self.symbol}: {e}")

        if data.empty:
            raise ValueError(f"No data found for symbol {self.symbol} from Alpha Vantage.")

        # Rename columns
        data.columns = [col.split('. ')[1].lower() for col in data.columns]

        # Filter by date range if specified
        if self.start_date:
            start_date = pd.to_datetime(self.start_date)
            data = data[data.index >= start_date]

        if self.end_date:
            end_date = pd.to_datetime(self.end_date)
            data = data[data.index <= end_date]

        # Set metadata
        self.metadata = {
            "source": "alpha_vantage",
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "rows": len(data),
            "start_date": data.index.min().strftime("%Y-%m-%d") if not data.empty else None,
            "end_date": data.index.max().strftime("%Y-%m-%d") if not data.empty else None
        }

        return data
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """
        Generate sample market data for testing.
        
        Returns:
            DataFrame containing sample market data
        """
        logger.info("Generating sample market data")
        
        # Set date range
        end_date = pd.to_datetime(self.end_date) if self.end_date else datetime.now()
        start_date = pd.to_datetime(self.start_date) if self.start_date else end_date - timedelta(days=365)
        
        # Generate date range
        if self.timeframe == "1d":
            date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
        elif self.timeframe == "1h":
            date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        else:
            date_range = pd.date_range(start=start_date, end=end_date, freq='B')
        
        # Generate random price data
        np.random.seed(42)  # For reproducibility
        n = len(date_range)
        
        # Start with a base price
        base_price = 100.0
        
        # Generate daily returns with a slight upward bias
        daily_returns = np.random.normal(0.0005, 0.015, n)
        
        # Calculate price series
        prices = base_price * (1 + np.cumsum(daily_returns))
        
        # Generate OHLC data
        data = pd.DataFrame(index=date_range)
        data['close'] = prices
        data['open'] = prices * (1 + np.random.normal(0, 0.005, n))
        data['high'] = np.maximum(data['open'], data['close']) * (1 + np.abs(np.random.normal(0, 0.005, n)))
        data['low'] = np.minimum(data['open'], data['close']) * (1 - np.abs(np.random.normal(0, 0.005, n)))
        data['volume'] = np.random.lognormal(10, 1, n).astype(int)
        
        # Set metadata
        self.metadata = {
            "source": "sample",
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "rows": len(data),
            "start_date": data.index.min().strftime("%Y-%m-%d"),
            "end_date": data.index.max().strftime("%Y-%m-%d")
        }
        
        return data
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the loaded data.
        
        Returns:
            Dictionary of metadata
        """
        return self.metadata