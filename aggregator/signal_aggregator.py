#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

class SignalAggregator:
    """
    Aggregates signals from multiple trading strategies into a unified signal.
    
    This class implements various methods for combining signals from different
    strategies, taking into account their weights and signal types.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the signal aggregator.
        
        Args:
            config: Configuration dictionary for the aggregator
        """
        self.config = config or {}
        self.method = self.config.get("method", "weighted_average")
        self.threshold = self.config.get("threshold", 0.5)
        self.metadata = {}
    
    def aggregate(self, signals_list: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Aggregate multiple signal DataFrames into a single DataFrame.
        
        Args:
            signals_list: List of DataFrames containing signals from different strategies
            
        Returns:
            DataFrame containing the aggregated signals
        """
        if not signals_list:
            logger.warning("No signals to aggregate")
            return pd.DataFrame()
        
        # Ensure all DataFrames have the same index
        if not all(signals.index.equals(signals_list[0].index) for signals in signals_list):
            logger.warning("Signal DataFrames have different indices, reindexing...")
            # Get the union of all indices
            all_indices = signals_list[0].index
            for signals in signals_list[1:]:
                all_indices = all_indices.union(signals.index)
            
            # Reindex all DataFrames
            signals_list = [signals.reindex(all_indices) for signals in signals_list]
        
        # Choose aggregation method based on configuration
        if self.method == "weighted_average":
            return self._weighted_average(signals_list)
        elif self.method == "majority_vote":
            return self._majority_vote(signals_list)
        elif self.method == "consensus":
            return self._consensus(signals_list)
        else:
            logger.warning(f"Unknown aggregation method: {self.method}, using weighted_average")
            return self._weighted_average(signals_list)
    
    def _weighted_average(self, signals_list: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Aggregate signals using weighted average.
        
        Args:
            signals_list: List of DataFrames containing signals
            
        Returns:
            DataFrame with aggregated signals
        """
        # Extract signal columns and weights
        signal_dfs = []
        weights = []
        
        for signals in signals_list:
            if "signal" not in signals.columns:
                logger.warning(f"DataFrame missing 'signal' column, skipping")
                continue
            
            signal_dfs.append(signals["signal"])
            weights.append(signals.get("weight", 1.0).iloc[0] if "weight" in signals.columns else 1.0)
        
        if not signal_dfs:
            logger.warning("No valid signal columns found")
            return pd.DataFrame()
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(weights) for _ in weights]
        
        # Combine signals using weighted average
        combined_signal = pd.DataFrame(index=signal_dfs[0].index)
        combined_signal["signal"] = sum(df * weight for df, weight in zip(signal_dfs, weights))
        
        # Add binary signal based on threshold
        combined_signal["binary_signal"] = (combined_signal["signal"] > self.threshold).astype(int)
        
        # Add metadata
        self.metadata = {
            "method": "weighted_average",
            "threshold": self.threshold,
            "num_strategies": len(signal_dfs),
            "weights": weights
        }
        
        return combined_signal
    
    def _majority_vote(self, signals_list: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Aggregate signals using majority vote.
        
        Args:
            signals_list: List of DataFrames containing signals
            
        Returns:
            DataFrame with aggregated signals
        """
        # Extract binary signal columns
        binary_signals = []
        weights = []
        
        for signals in signals_list:
            if "binary_signal" not in signals.columns:
                if "signal" in signals.columns:
                    # Convert continuous signal to binary using threshold
                    binary_signal = (signals["signal"] > 0.5).astype(int)
                else:
                    logger.warning(f"DataFrame missing signal columns, skipping")
                    continue
            else:
                binary_signal = signals["binary_signal"]
            
            binary_signals.append(binary_signal)
            weights.append(signals.get("weight", 1.0).iloc[0] if "weight" in signals.columns else 1.0)
        
        if not binary_signals:
            logger.warning("No valid binary signal columns found")
            return pd.DataFrame()
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(weights) for _ in weights]
        
        # Combine binary signals using weighted vote
        combined_signal = pd.DataFrame(index=binary_signals[0].index)
        combined_signal["signal"] = sum(bs * weight for bs, weight in zip(binary_signals, weights))
        
        # Add binary signal based on threshold (default 0.5 for majority)
        combined_signal["binary_signal"] = (combined_signal["signal"] > self.threshold).astype(int)
        
        # Add metadata
        self.metadata = {
            "method": "majority_vote",
            "threshold": self.threshold,
            "num_strategies": len(binary_signals),
            "weights": weights
        }
        
        return combined_signal
    
    def _consensus(self, signals_list: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Aggregate signals using consensus (all must agree).
        
        Args:
            signals_list: List of DataFrames containing signals
            
        Returns:
            DataFrame with aggregated signals
        """
        # Extract binary signal columns
        binary_signals = []
        
        for signals in signals_list:
            if "binary_signal" not in signals.columns:
                if "signal" in signals.columns:
                    # Convert continuous signal to binary using threshold
                    binary_signal = (signals["signal"] > 0.5).astype(int)
                else:
                    logger.warning(f"DataFrame missing signal columns, skipping")
                    continue
            else:
                binary_signal = signals["binary_signal"]
            
            binary_signals.append(binary_signal)
        
        if not binary_signals:
            logger.warning("No valid binary signal columns found")
            return pd.DataFrame()
        
        # Combine binary signals using consensus (all must agree)
        combined_signal = pd.DataFrame(index=binary_signals[0].index)
        
        # For buy signals (1), all strategies must agree
        buy_consensus = pd.Series(1, index=binary_signals[0].index)
        for bs in binary_signals:
            buy_consensus = buy_consensus & (bs == 1)
        
        # For sell signals (0), all strategies must agree
        sell_consensus = pd.Series(1, index=binary_signals[0].index)
        for bs in binary_signals:
            sell_consensus = sell_consensus & (bs == 0)
        
        # Combine: 1 for buy consensus, 0 for sell consensus, 0.5 for no consensus
        combined_signal["binary_signal"] = 0.5  # Default: no consensus
        combined_signal.loc[buy_consensus, "binary_signal"] = 1.0  # Buy consensus
        combined_signal.loc[sell_consensus, "binary_signal"] = 0.0  # Sell consensus
        
        # Add continuous signal (same as binary in this case)
        combined_signal["signal"] = combined_signal["binary_signal"]
        
        # Add metadata
        self.metadata = {
            "method": "consensus",
            "num_strategies": len(binary_signals)
        }
        
        return combined_signal
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the aggregation process.
        
        Returns:
            Dictionary of metadata
        """
        return self.metadata