#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class MACDStrategy(Strategy):
    """
    Moving Average Convergence Divergence (MACD) strategy.
    
    Generates buy signals when the MACD line crosses above the signal line,
    and sell signals when the MACD line crosses below the signal line.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the MACD strategy.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        super().__init__(name, parameters)
        
        # Set default parameters if not provided
        if not self.parameters:
            self.parameters = {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9
            }
        
        # Extract parameters
        self.fast_period = self.parameters.get("fast_period", 12)
        self.slow_period = self.parameters.get("slow_period", 26)
        self.signal_period = self.parameters.get("signal_period", 9)
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data and generate trading signals.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            DataFrame containing the generated signals
        """
        if data.empty:
            logger.warning("Empty data provided to MACD strategy")
            return pd.DataFrame()
        
        # Ensure we have the required columns
        if 'close' not in data.columns:
            logger.error("Data missing 'close' column required for MACD calculation")
            return pd.DataFrame()
        
        # Calculate MACD components
        exp1 = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = data['close'].ewm(span=self.slow_period, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        # Create signals DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['macd_line'] = macd_line
        signals['signal_line'] = signal_line
        signals['histogram'] = histogram
        
        # Generate signal: 1 when MACD line crosses above signal line, -1 when crosses below
        signals['signal'] = 0
        signals['signal'] = np.where(macd_line > signal_line, 1, -1)
        
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
        # Skip if we don't have enough data
        if len(signals) < max(self.fast_period, self.slow_period, self.signal_period) + 10:
            return
        
        # Calculate signal changes (to identify entry/exit points)
        signal_changes = signals['signal'].diff().fillna(0)
        
        # Count number of trades
        num_trades = (signal_changes != 0).sum() // 2  # Divide by 2 because each trade has entry and exit
        
        # Store metadata
        self.metadata = {
            "strategy_name": self.name,
            "fast_period": self.fast_period,
            "slow_period": self.slow_period,
            "signal_period": self.signal_period,
            "num_trades": num_trades,
            "weight": self.weight
        }
    
    def get_signal_type(self) -> str:
        """
        Get the type of signals this strategy generates.
        
        Returns:
            Signal type description
        """
        return "trend_following"
    
    def get_description(self) -> str:
        """
        Get a description of how this strategy works.
        
        Returns:
            String describing the strategy
        """
        return f"MACD strategy that generates buy signals when the MACD line crosses above the signal line (fast period: {self.fast_period}, slow period: {self.slow_period}, signal period: {self.signal_period}), and sell signals when it crosses below."