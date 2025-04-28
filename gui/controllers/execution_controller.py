#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Execution Controller for the Trading Strategy Aggregation System GUI

This module handles the execution of the trading strategy analysis and
processing of the results.
"""

import os
import logging
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

# Import core functionality
from strategies.strategy_factory import StrategyFactory
from strategies.moving_average_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from aggregator.signal_aggregator import SignalAggregator
from reports.report_generator import ReportGenerator
from data.data_loader import DataLoader

logger = logging.getLogger(__name__)

class ExecutionController:
    """Controller for executing trading strategy analysis"""
    
    def __init__(self, config_controller):
        """Initialize the execution controller"""
        self.config_controller = config_controller
        self.market_data = None
        self.strategy_signals = []
        self.strategy_metadata = []
        self.aggregated_signal = None
        self.report_path = None
    
    def run_analysis(self) -> Tuple[bool, str]:
        """Run the trading strategy analysis"""
        try:
            # Get configuration
            config = self.config_controller.get_config()
            
            # Create necessary directories
            self._create_directories()
            
            # Load market data
            logger.info("Loading market data...")
            data_loader = DataLoader(config.get("data_source", {}))
            self.market_data = data_loader.load_data()
            logger.info(f"Loaded {len(self.market_data)} data points")
            
            if self.market_data.empty:
                return False, "Failed to load market data"
            
            # Initialize strategy factory and register strategies
            strategy_factory = StrategyFactory()
            strategy_factory.register_strategy("MovingAverageCrossover", MovingAverageCrossover)
            strategy_factory.register_strategy("RSIStrategy", RSIStrategy)
            strategy_factory.register_strategy("MACDStrategy", MACDStrategy)
            
            # Initialize strategies
            strategies = []
            strategy_configs = config.get("strategies", [])
            
            if not strategy_configs:
                logger.warning("No strategies configured")
                return False, "No strategies configured"
            
            for strategy_config in strategy_configs:
                strategy_name = strategy_config.get("name")
                strategy_params = strategy_config.get("parameters", {})
                strategy_weight = strategy_config.get("weight", 1.0)
                
                strategy = strategy_factory.create_strategy(strategy_name, strategy_params)
                if strategy:
                    strategy.set_weight(strategy_weight)
                    strategies.append(strategy)
                    logger.info(f"Initialized strategy: {strategy_name} with weight {strategy_weight}")
                else:
                    logger.warning(f"Failed to initialize strategy: {strategy_name}")
            
            if not strategies:
                logger.error("No strategies were initialized")
                return False, "No strategies were initialized"
            
            # Process data through each strategy to get signals
            self.strategy_signals = []
            self.strategy_metadata = []
            
            for strategy in strategies:
                signals = strategy.process_data(self.market_data)
                self.strategy_signals.append(signals)
                self.strategy_metadata.append(strategy.get_metadata())
                logger.info(f"Processed data through strategy: {strategy.get_name()}")
            
            # Aggregate signals
            aggregator = SignalAggregator(config.get("aggregator", {}))
            self.aggregated_signal = aggregator.aggregate(self.strategy_signals)
            logger.info(f"Aggregated signals using method: {aggregator.method}")
            
            # Generate report
            report_generator = ReportGenerator(config.get("report", {}))
            self.report_path = report_generator.generate_report(
                market_data=self.market_data, 
                strategy_signals=self.strategy_signals, 
                aggregated_signal=self.aggregated_signal,
                strategy_metadata=self.strategy_metadata
            )
            
            if self.report_path:
                logger.info(f"Report generated successfully: {self.report_path}")
                return True, f"Report generated successfully: {os.path.abspath(self.report_path)}"
            else:
                logger.error("Failed to generate report")
                return False, "Failed to generate report"
            
        except Exception as e:
            logger.error(f"An error occurred during analysis: {e}", exc_info=True)
            return False, f"An error occurred: {str(e)}"
    
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        directories = [
            "data",
            "strategies",
            "aggregator",
            "reports",
            "config",
            "logs",
            "reports/output",
            "reports/output/plots"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_market_data(self) -> pd.DataFrame:
        """Get the market data"""
        return self.market_data
    
    def get_strategy_signals(self) -> List[pd.DataFrame]:
        """Get the strategy signals"""
        return self.strategy_signals
    
    def get_strategy_metadata(self) -> List[Dict[str, Any]]:
        """Get the strategy metadata"""
        return self.strategy_metadata
    
    def get_aggregated_signal(self) -> pd.DataFrame:
        """Get the aggregated signal"""
        return self.aggregated_signal
    
    def get_report_path(self) -> str:
        """Get the path to the generated report"""
        return self.report_path
    
    def get_results(self) -> Dict[str, Any]:
        """Get all analysis results in a dictionary format
        
        Returns:
            Dict containing market_data, signals, and aggregated_signal
        """
        results = {}
        
        if self.market_data is not None and not self.market_data.empty:
            results['market_data'] = self.market_data
        
        if self.strategy_signals and len(self.strategy_signals) > 0:
            # Combine all strategy signals into one DataFrame
            all_signals = pd.DataFrame(index=self.market_data.index if self.market_data is not None else None)
            
            for i, signals_df in enumerate(self.strategy_signals):
                if not signals_df.empty and 'signal' in signals_df.columns:
                    strategy_name = f"Strategy_{i+1}"
                    if self.strategy_metadata and i < len(self.strategy_metadata):
                        strategy_name = self.strategy_metadata[i].get('name', strategy_name)
                    all_signals[strategy_name] = signals_df['signal']
            
            results['signals'] = all_signals
        
        if self.aggregated_signal is not None and not self.aggregated_signal.empty:
            results['aggregated_signal'] = self.aggregated_signal
            
        return results