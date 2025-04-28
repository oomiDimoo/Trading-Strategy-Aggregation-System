#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class IchimokuCloudStrategy(Strategy):
    """
    Ichimoku Cloud (Ichimoku Kinko Hyo) strategy.
    
    Generates signals based on multiple components of the Ichimoku Cloud system:
    - Tenkan-sen (Conversion Line): Short-term trend indicator
    - Kijun-sen (Base Line): Medium-term trend indicator
    - Senkou Span A (Leading Span A): First component of the cloud
    - Senkou Span B (Leading Span B): Second component of the cloud
    - Chikou Span (Lagging Span): Closing price shifted backwards
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the Ichimoku Cloud strategy.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        super().__init__(name, parameters)
        
        # Set default parameters if not provided
        if not self.parameters:
            self.parameters = {
                "tenkan_period": 9,
                "kijun_period": 26,
                "senkou_b_period": 52,
                "displacement": 26
            }
        
        # Extract parameters
        self.tenkan_period = self.parameters.get("tenkan_period", 9)
        self.kijun_period = self.parameters.get("kijun_period", 26)
        self.senkou_b_period = self.parameters.get("senkou_b_period", 52)
        self.displacement = self.parameters.get("displacement", 26)
    
    def _calculate_ichimoku_components(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate all Ichimoku Cloud components.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            Dictionary containing all Ichimoku components
        """
        # Extract high and low prices
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Calculate Tenkan-sen (Conversion Line): (highest high + lowest low)/2 for the past 9 periods
        tenkan_sen = (high.rolling(window=self.tenkan_period).max() + 
                      low.rolling(window=self.tenkan_period).min()) / 2
        
        # Calculate Kijun-sen (Base Line): (highest high + lowest low)/2 for the past 26 periods
        kijun_sen = (high.rolling(window=self.kijun_period).max() + 
                     low.rolling(window=self.kijun_period).min()) / 2
        
        # Calculate Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen)/2 shifted forward 26 periods
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(self.displacement)
        
        # Calculate Senkou Span B (Leading Span B): (highest high + lowest low)/2 for the past 52 periods, shifted forward 26 periods
        senkou_span_b = ((high.rolling(window=self.senkou_b_period).max() + 
                          low.rolling(window=self.senkou_b_period).min()) / 2).shift(self.displacement)
        
        # Calculate Chikou Span (Lagging Span): Current closing price shifted backwards 26 periods
        chikou_span = close.shift(-self.displacement)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data and generate trading signals.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            DataFrame containing the generated signals
        """
        if data.empty:
            logger.warning("Empty data provided to Ichimoku Cloud strategy")
            return pd.DataFrame()
        
        # Ensure we have the required columns
        required_columns = ['high', 'low', 'close']
        for col in required_columns:
            if col not in data.columns:
                logger.error(f"Data missing '{col}' column required for Ichimoku Cloud calculation")
                return pd.DataFrame()
        
        # Calculate Ichimoku components
        ichimoku = self._calculate_ichimoku_components(data)
        
        # Create signals DataFrame
        signals = pd.DataFrame(index=data.index)
        
        # Add Ichimoku components to signals DataFrame
        for key, value in ichimoku.items():
            signals[key] = value
        
        # Add price data
        signals['close'] = data['close']
        
        # Generate signals based on Ichimoku rules
        signals['signal'] = 0
        
        # Buy signal conditions (multiple conditions for stronger signal):
        # 1. Price crosses above the cloud (close > senkou_span_a and close > senkou_span_b)
        # 2. Tenkan-sen crosses above Kijun-sen (bullish TK cross)
        buy_condition_1 = (data['close'] > signals['senkou_span_a']) & (data['close'] > signals['senkou_span_b'])
        buy_condition_2 = (signals['tenkan_sen'] > signals['kijun_sen']) & (signals['tenkan_sen'].shift(1) <= signals['kijun_sen'].shift(1))
        
        # Sell signal conditions:
        # 1. Price crosses below the cloud (close < senkou_span_a and close < senkou_span_b)
        # 2. Tenkan-sen crosses below Kijun-sen (bearish TK cross)
        sell_condition_1 = (data['close'] < signals['senkou_span_a']) & (data['close'] < signals['senkou_span_b'])
        sell_condition_2 = (signals['tenkan_sen'] < signals['kijun_sen']) & (signals['tenkan_sen'].shift(1) >= signals['kijun_sen'].shift(1))
        
        # Apply signals
        signals.loc[buy_condition_1 | buy_condition_2, 'signal'] = 1
        signals.loc[sell_condition_1 | sell_condition_2, 'signal'] = -1
        
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
        min_periods = max(self.tenkan_period, self.kijun_period, self.senkou_b_period) + self.displacement
        if len(signals) < min_periods + 1:
            return
        
        # Calculate metrics only on valid signals (after warmup period)
        valid_signals = signals.iloc[min_periods:].copy()
        
        # Count number of buy and sell signals
        buy_signals = (valid_signals['signal'] == 1).sum()
        sell_signals = (valid_signals['signal'] == -1).sum()
        
        # Calculate percentage of time in market
        total_periods = len(valid_signals)
        in_market_periods = (valid_signals['binary_signal'] == 1).sum()
        market_participation = (in_market_periods / total_periods) * 100 if total_periods > 0 else 0
        
        # Store metrics in metadata
        self.metadata = {
            "strategy_name": self.name,
            "parameters": self.parameters,
            "buy_signals": int(buy_signals),
            "sell_signals": int(sell_signals),
            "market_participation": float(market_participation)
        }
    
    def get_signal_type(self) -> str:
        """
        Get the type of signals this strategy generates.
        
        Returns:
            Signal type description
        """
        return "Ichimoku Cloud"
    
    def get_description(self) -> str:
        """
        Get a description of this strategy.
        
        Returns:
            Strategy description
        """
        return f"Ichimoku Cloud (Tenkan: {self.tenkan_period}, Kijun: {self.kijun_period}, Senkou B: {self.senkou_b_period})"