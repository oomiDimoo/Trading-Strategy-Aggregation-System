#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class VolumeProfileStrategy(Strategy):
    """
    Volume Profile strategy.
    
    Generates signals based on volume distribution across price levels.
    Buy signals occur at high volume nodes when price is approaching from below,
    and sell signals occur at high volume nodes when price is approaching from above.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the Volume Profile strategy.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        super().__init__(name, parameters)
        
        # Set default parameters if not provided
        if not self.parameters:
            self.parameters = {
                "num_bins": 20,
                "lookback_period": 100,
                "volume_threshold": 0.8,
                "signal_lookback": 5
            }
        
        # Extract parameters
        self.num_bins = self.parameters.get("num_bins", 20)
        self.lookback_period = self.parameters.get("lookback_period", 100)
        self.volume_threshold = self.parameters.get("volume_threshold", 0.8)
        self.signal_lookback = self.parameters.get("signal_lookback", 5)
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data and generate trading signals.
        
        Args:
            data: DataFrame containing market data (OHLCV)
            
        Returns:
            DataFrame containing the generated signals
        """
        if data.empty:
            logger.warning("Empty data provided to Volume Profile strategy")
            return pd.DataFrame()
        
        # Ensure we have the required columns
        required_columns = ['high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Data missing required columns for Volume Profile calculation")
            return pd.DataFrame()
        
        # Create signals DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        signals['binary_signal'] = 0
        
        # Process each window of data
        for i in range(self.lookback_period, len(data)):
            # Get the current window
            window = data.iloc[i-self.lookback_period:i]
            
            # Calculate price range for the window
            price_min = window['low'].min()
            price_max = window['high'].max()
            price_range = price_max - price_min
            
            # Skip if price range is too small
            if price_range < 0.001:
                continue
            
            # Create price bins
            bins = np.linspace(price_min, price_max, self.num_bins + 1)
            
            # Calculate volume profile
            volume_profile = np.zeros(self.num_bins)
            
            # Distribute volume across price levels
            for _, row in window.iterrows():
                # Determine which bins this candle spans
                low_bin = max(0, np.digitize(row['low'], bins) - 1)
                high_bin = min(self.num_bins - 1, np.digitize(row['high'], bins) - 1)
                
                # Distribute volume proportionally across the bins
                if high_bin == low_bin:
                    volume_profile[low_bin] += row['volume']
                else:
                    price_span = row['high'] - row['low']
                    for bin_idx in range(low_bin, high_bin + 1):
                        bin_low = bins[bin_idx]
                        bin_high = bins[bin_idx + 1]
                        overlap = min(bin_high, row['high']) - max(bin_low, row['low'])
                        bin_volume = row['volume'] * (overlap / price_span)
                        volume_profile[bin_idx] += bin_volume
            
            # Normalize volume profile
            total_volume = np.sum(volume_profile)
            if total_volume > 0:
                volume_profile = volume_profile / total_volume
            
            # Find high volume nodes (HVNs)
            hvn_threshold = np.percentile(volume_profile, self.volume_threshold * 100)
            hvn_bins = np.where(volume_profile >= hvn_threshold)[0]
            
            # Convert bin indices to price levels
            hvn_prices = [(bins[idx] + bins[idx + 1]) / 2 for idx in hvn_bins]
            
            # Current price and recent price movement
            current_price = data.iloc[i]['close']
            price_direction = 1 if current_price > data.iloc[i-self.signal_lookback]['close'] else -1
            
            # Generate signals based on proximity to HVNs
            for hvn_price in hvn_prices:
                price_distance = abs(current_price - hvn_price)
                price_percent = price_distance / current_price
                
                # If price is close to a HVN (within 0.5%)
                if price_percent < 0.005:
                    # Buy signal if approaching HVN from below
                    if price_direction > 0 and current_price < hvn_price:
                        signals.loc[data.index[i], 'signal'] = 1
                        signals.loc[data.index[i], 'binary_signal'] = 1
                    # Sell signal if approaching HVN from above
                    elif price_direction < 0 and current_price > hvn_price:
                        signals.loc[data.index[i], 'signal'] = -1
                        signals.loc[data.index[i], 'binary_signal'] = 0
        
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
        if len(signals) < self.lookback_period + 10:
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
        self.metadata = {
            "num_trades": num_trades,
            "win_rate": win_rate,
            "strategy_type": "Volume Profile",
            "parameters": self.parameters
        }