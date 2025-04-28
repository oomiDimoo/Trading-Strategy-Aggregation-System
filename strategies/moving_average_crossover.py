#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class MovingAverageCrossover(Strategy):
    """
    Moving Average Crossover strategy.
    
    Generates buy signals when the fast moving average crosses above the slow moving average,
    and sell signals when the fast moving average crosses below the slow moving average.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the Moving Average Crossover strategy.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        super().__init__(name, parameters)
        
        # Set default parameters if not provided
        if not self.parameters:
            self.parameters = {
                "fast_period": 20,
                "slow_period": 50,
                "signal_threshold": 0.0
            }
        
        # Extract parameters
        self.fast_period = self.parameters.get("fast_period", 20)
        self.slow_period = self.parameters.get("slow_period", 50)
        self.signal_threshold = self.parameters.get("signal_threshold", 0.0)
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data and generate trading signals.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            DataFrame containing the generated signals
        """
        if data.empty:
            logger.warning("Empty data provided to MovingAverageCrossover strategy")
            return pd.DataFrame()
        
        # Ensure we have the required columns
        if 'close' not in data.columns:
            logger.error("Data missing 'close' column required for MA calculation")
            return pd.DataFrame()
        
        # Calculate moving averages
        fast_ma = data['close'].rolling(window=self.fast_period).mean()
        slow_ma = data['close'].rolling(window=self.slow_period).mean()
        
        # Create signals DataFrame
        signals = pd.DataFrame(index=data.index)
        
        # Calculate the difference between fast and slow MAs
        signals['ma_diff'] = fast_ma - slow_ma
        
        # Generate signal: 1 when fast MA > slow MA, -1 when fast MA < slow MA
        signals['signal'] = np.where(signals['ma_diff'] > self.signal_threshold, 1, -1)
        
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
        if len(signals) < max(self.fast_period, self.slow_period) + 10:
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
            "signal_threshold": self.signal_threshold,
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
        return f"Moving Average Crossover strategy that generates buy signals when the {self.fast_period}-period MA crosses above the {self.slow_period}-period MA, and sell signals when it crosses below."