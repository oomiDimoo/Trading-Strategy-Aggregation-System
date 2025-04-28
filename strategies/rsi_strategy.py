#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class RSIStrategy(Strategy):
    """
    Relative Strength Index (RSI) strategy.
    
    Generates buy signals when RSI falls below the oversold threshold and
    sell signals when RSI rises above the overbought threshold.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the RSI strategy.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        super().__init__(name, parameters)
        
        # Set default parameters if not provided
        if not self.parameters:
            self.parameters = {
                "period": 14,
                "overbought": 70,
                "oversold": 30
            }
        
        # Extract parameters
        self.period = self.parameters.get("period", 14)
        self.overbought = self.parameters.get("overbought", 70)
        self.oversold = self.parameters.get("oversold", 30)
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data and generate trading signals.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            DataFrame containing the generated signals
        """
        if data.empty:
            logger.warning("Empty data provided to RSI strategy")
            return pd.DataFrame()
        
        # Ensure we have the required columns
        if 'close' not in data.columns:
            logger.error("Data missing 'close' column required for RSI calculation")
            return pd.DataFrame()
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        rs = avg_gain / avg_loss.where(avg_loss != 0, 1e-10)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        
        # Create signals DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['rsi'] = rsi
        
        # Generate signal: 1 for oversold (buy), -1 for overbought (sell), 0 for neutral
        signals['signal'] = 0
        signals.loc[rsi < self.oversold, 'signal'] = 1
        signals.loc[rsi > self.overbought, 'signal'] = -1
        
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
        if len(signals) < self.period + 10:
            return
        
        # Calculate signal changes (to identify entry/exit points)
        signal_changes = signals['signal'].diff().fillna(0)
        
        # Count number of trades
        num_trades = (signal_changes != 0).sum()
        
        # Store metadata
        self.metadata = {
            "strategy_name": self.name,
            "period": self.period,
            "overbought": self.overbought,
            "oversold": self.oversold,
            "num_trades": num_trades,
            "weight": self.weight
        }
    
    def get_signal_type(self) -> str:
        """
        Get the type of signals this strategy generates.
        
        Returns:
            Signal type description
        """
        return "mean_reversion"
    
    def get_description(self) -> str:
        """
        Get a description of how this strategy works.
        
        Returns:
            String describing the strategy
        """
        return f"RSI strategy that generates buy signals when RSI falls below {self.oversold} (oversold) and sell signals when RSI rises above {self.overbought} (overbought)."