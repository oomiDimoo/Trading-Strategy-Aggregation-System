#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class FibonacciRetracementStrategy(Strategy):
    """
    Fibonacci Retracement strategy.
    
    Generates buy signals when price retraces to key Fibonacci levels during an uptrend,
    and sell signals when price retraces to key Fibonacci levels during a downtrend.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the Fibonacci Retracement strategy.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        super().__init__(name, parameters)
        
        # Extract parameters
        self.trend_period = self.parameters.get("trend_period", 50)
        self.swing_lookback = self.parameters.get("swing_lookback", 20)
        self.retracement_levels = self.parameters.get("retracement_levels", [0.236, 0.382, 0.5, 0.618, 0.786])
        self.level_tolerance = self.parameters.get("level_tolerance", 0.01)
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data and generate trading signals.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            DataFrame containing the generated signals
        """
        if data.empty:
            logger.warning("Empty data provided to Fibonacci Retracement strategy")
            return pd.DataFrame()
        
        # Ensure we have the required columns
        if 'high' not in data.columns or 'low' not in data.columns or 'close' not in data.columns:
            logger.error("Data missing required columns for Fibonacci Retracement calculation")
            return pd.DataFrame()
        
        # Create signals DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        signals['binary_signal'] = 0
        
        # Calculate trend direction using simple moving average
        data['trend_ma'] = data['close'].rolling(window=self.trend_period).mean()
        
        # We need at least trend_period + swing_lookback data points
        min_required = self.trend_period + self.swing_lookback
        if len(data) < min_required:
            logger.warning(f"Not enough data points for Fibonacci Retracement calculation. Need at least {min_required}")
            return signals
        
        # Process each window of data starting from the minimum required data points
        for i in range(min_required, len(data)):
            # Determine trend direction
            current_ma = data['trend_ma'].iloc[i]
            prev_ma = data['trend_ma'].iloc[i - self.swing_lookback]
            trend_direction = 1 if current_ma > prev_ma else -1
            
            # Find swing high/low points in the lookback period
            window = data.iloc[i - self.swing_lookback:i]
            
            if trend_direction > 0:  # Uptrend - look for swing low to swing high
                swing_low = window['low'].min()
                swing_low_idx = window['low'].idxmin()
                
                # Find the highest high after the swing low
                high_after_low = data.loc[swing_low_idx:data.index[i], 'high'].max()
                
                # Calculate Fibonacci retracement levels
                price_range = high_after_low - swing_low
                fib_levels = [high_after_low - level * price_range for level in self.retracement_levels]
                
                # Current price
                current_price = data['close'].iloc[i]
                
                # Check if price is near any retracement level
                for level, price_level in zip(self.retracement_levels, fib_levels):
                    # Calculate percentage distance from the level
                    level_distance = abs(current_price - price_level) / price_level
                    
                    # If price is within tolerance of a Fibonacci level
                    if level_distance <= self.level_tolerance:
                        # Generate buy signal in uptrend when price retraces to a Fibonacci level
                        signals.loc[data.index[i], 'signal'] = 1
                        signals.loc[data.index[i], 'binary_signal'] = 1
                        break
            
            else:  # Downtrend - look for swing high to swing low
                swing_high = window['high'].max()
                swing_high_idx = window['high'].idxmax()
                
                # Find the lowest low after the swing high
                low_after_high = data.loc[swing_high_idx:data.index[i], 'low'].min()
                
                # Calculate Fibonacci retracement levels
                price_range = swing_high - low_after_high
                fib_levels = [low_after_high + level * price_range for level in self.retracement_levels]
                
                # Current price
                current_price = data['close'].iloc[i]
                
                # Check if price is near any retracement level
                for level, price_level in zip(self.retracement_levels, fib_levels):
                    # Calculate percentage distance from the level
                    level_distance = abs(current_price - price_level) / price_level
                    
                    # If price is within tolerance of a Fibonacci level
                    if level_distance <= self.level_tolerance:
                        # Generate sell signal in downtrend when price retraces to a Fibonacci level
                        signals.loc[data.index[i], 'signal'] = -1
                        signals.loc[data.index[i], 'binary_signal'] = 0
                        break
        
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
        if len(signals) < self.trend_period + self.swing_lookback + 10:
            return
        
        # Calculate basic metrics
        signal_changes = signals['signal'].diff().fillna(0)
        num_trades = (signal_changes != 0).sum()
        
        # Calculate win rate (simplified)
        # A win is when a buy signal is followed by a price increase, or a sell signal is followed by a price decrease
        wins = 0
        for i in range(len(signals) - 1):
            if signals['signal'].iloc[i] == 1 and data['close'].iloc[i+1] > data['close'].iloc[i]:
                wins += 1
            elif signals['signal'].iloc[i] == -1 and data['close'].iloc[i+1] < data['close'].iloc[i]:
                wins += 1
        
        win_rate = wins / num_trades if num_trades > 0 else 0
        
        # Store metrics in metadata
        self.metadata.update({
            "num_trades": num_trades,
            "win_rate": win_rate,
            "strategy_type": "Fibonacci Retracement",
            "parameters": self.parameters
        })

    def get_signal_type(self) -> str:
        """
        Get the type of signals this strategy generates.

        Returns:
            Signal type description
        """
        return "Fibonacci Retracement"

    def get_description(self) -> str:
        """
        Get a description of this strategy.

        Returns:
            Strategy description
        """
        return f"Fibonacci Retracement ({self.trend_period}, {self.swing_lookback})"