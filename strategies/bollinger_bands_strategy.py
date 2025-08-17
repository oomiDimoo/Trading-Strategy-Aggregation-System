#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands strategy.
    
    Generates buy signals when price touches or crosses below the lower band
    and sell signals when price touches or crosses above the upper band.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the Bollinger Bands strategy.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        super().__init__(name, parameters)
        
        # Extract parameters
        self.period = self.parameters.get("period", 20)
        self.std_dev = self.parameters.get("std_dev", 2.0)
        self.price_source = self.parameters.get("price_source", "close")
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data and generate trading signals.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            DataFrame containing the generated signals
        """
        if data.empty:
            logger.warning("Empty data provided to Bollinger Bands strategy")
            return pd.DataFrame()
        
        # Ensure we have the required columns
        if self.price_source not in data.columns:
            logger.error(f"Data missing '{self.price_source}' column required for Bollinger Bands calculation")
            return pd.DataFrame()
        
        # Calculate Bollinger Bands
        price = data[self.price_source]
        
        # Calculate middle band (simple moving average)
        middle_band = price.rolling(window=self.period).mean()
        
        # Calculate standard deviation
        rolling_std = price.rolling(window=self.period).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (rolling_std * self.std_dev)
        lower_band = middle_band - (rolling_std * self.std_dev)
        
        # Create signals DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['middle_band'] = middle_band
        signals['upper_band'] = upper_band
        signals['lower_band'] = lower_band
        signals['price'] = price
        
        # Generate signal: 1 for price below lower band (buy), -1 for price above upper band (sell), 0 for neutral
        signals['signal'] = 0
        signals.loc[price < lower_band, 'signal'] = 1  # Buy signal
        signals.loc[price > upper_band, 'signal'] = -1  # Sell signal
        
        # Generate binary signal (1 for buy, 0 for sell/neutral)
        signals['binary_signal'] = np.where(signals['signal'] > 0, 1, 0)
        
        # Add strategy metadata
        signals['strategy'] = self.name
        signals['weight'] = self.weight
        
        # Store signals for later retrieval
        self.signals = signals
        
        # Calculate performance metrics
        self._calculate_performance_metrics(data, signals)
        
        return signals
    
    def _calculate_performance_metrics(self, data: pd.DataFrame, signals: pd.DataFrame) -> None:
        """
        Calculate performance metrics for the strategy.
        
        Args:
            data: Original market data
            signals: Generated signals
        """
        super()._calculate_performance_metrics(data, signals)
        # Skip if we don't have enough data
        if len(signals) < self.period + 1:
            return
        
        # Calculate metrics only on valid signals (after warmup period)
        valid_signals = signals.iloc[self.period:].copy()
        
        # Count number of buy and sell signals
        buy_signals = (valid_signals['signal'] == 1).sum()
        sell_signals = (valid_signals['signal'] == -1).sum()
        
        # Calculate percentage of time in market
        total_periods = len(valid_signals)
        in_market_periods = (valid_signals['binary_signal'] == 1).sum()
        market_participation = (in_market_periods / total_periods) * 100 if total_periods > 0 else 0
        
        # Store metrics in metadata
        self.metadata.update({
            "strategy_name": self.name,
            "parameters": self.parameters,
            "buy_signals": int(buy_signals),
            "sell_signals": int(sell_signals),
            "market_participation": float(market_participation)
        })
    
    def get_signal_type(self) -> str:
        """
        Get the type of signals this strategy generates.
        
        Returns:
            Signal type description
        """
        return "Bollinger Bands"
    
    def get_description(self) -> str:
        """
        Get a description of this strategy.
        
        Returns:
            Strategy description
        """
        return f"Bollinger Bands ({self.period}, {self.std_dev})"