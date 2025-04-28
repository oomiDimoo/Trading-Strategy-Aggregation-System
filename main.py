#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trading Strategy Aggregation System

This is the main entry point for the application that aggregates signals
from multiple trading strategies and generates a unified report.
"""

import os
import json
import logging
from datetime import datetime, timedelta
import argparse

# Import core modules
from strategies.strategy_interface import Strategy
from strategies.strategy_factory import StrategyFactory
from aggregator.signal_aggregator import SignalAggregator
from reports.report_generator import ReportGenerator
from data.data_loader import DataLoader

# Import strategy implementations
from strategies.moving_average_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path="config/config.json"):
    """Load configuration from JSON file"""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Configuration file not found: {config_path}, using default configuration")
            return create_default_config()
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return create_default_config()


def create_default_config():
    """Create a default configuration"""
    config = {
        "data_source": {
            "type": "sample",  # Use sample data by default
            "symbol": "AAPL",
            "timeframe": "1d",
            "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        },
        "strategies": [
            {
                "name": "MovingAverageCrossover",
                "parameters": {
                    "fast_period": 20,
                    "slow_period": 50
                },
                "weight": 1.0
            },
            {
                "name": "RSIStrategy",
                "parameters": {
                    "period": 14,
                    "overbought": 70,
                    "oversold": 30
                },
                "weight": 0.8
            },
            {
                "name": "MACDStrategy",
                "parameters": {
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9
                },
                "weight": 0.9
            }
        ],
        "aggregator": {
            "method": "weighted_average",
            "threshold": 0.5
        },
        "report": {
            "format": "html",
            "include_plots": True,
            "output_dir": "reports/output"
        }
    }
    return config


def create_directories():
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


def save_config(config, config_path="config/config.json"):
    """Save configuration to a JSON file"""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")


def main():
    """Main application entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Trading Strategy Aggregation System")
    parser.add_argument("--config", type=str, default="config/config.json", help="Path to configuration file")
    parser.add_argument("--save-config", action="store_true", help="Save default configuration if none exists")
    args = parser.parse_args()
    
    # Create necessary directories
    create_directories()
    
    # Load configuration
    config = load_config(args.config)
    if args.save_config and not os.path.exists(args.config):
        save_config(config, args.config)
    
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    logger.info("Starting Trading Strategy Aggregation System")
    
    try:
        # Load market data
        logger.info("Loading market data...")
        data_loader = DataLoader(config.get("data_source", {}))
        market_data = data_loader.load_data()
        logger.info(f"Loaded {len(market_data)} data points")
        
        # Initialize strategy factory and register strategies
        strategy_factory = StrategyFactory()
        strategy_factory.register_strategy("MovingAverageCrossover", MovingAverageCrossover)
        strategy_factory.register_strategy("RSIStrategy", RSIStrategy)
        strategy_factory.register_strategy("MACDStrategy", MACDStrategy)
        
        # Initialize strategies
        strategies = []
        strategy_configs = config.get("strategies", [])
        
        if not strategy_configs:
            logger.warning("No strategies configured, using default strategies")
            strategy_configs = create_default_config()["strategies"]
        
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
            logger.error("No strategies were initialized. Exiting.")
            return
        
        # Process data through each strategy to get signals
        strategy_signals = []
        strategy_metadata = []
        
        for strategy in strategies:
            signals = strategy.process_data(market_data)
            strategy_signals.append(signals)
            strategy_metadata.append(strategy.get_metadata())
            logger.info(f"Processed data through strategy: {strategy.get_name()}")
        
        # Aggregate signals
        aggregator = SignalAggregator(config.get("aggregator", {}))
        aggregated_signal = aggregator.aggregate(strategy_signals)
        logger.info(f"Aggregated signals using method: {aggregator.method}")
        
        # Generate report
        report_generator = ReportGenerator(config.get("report", {}))
        report_path = report_generator.generate_report(
            market_data=market_data, 
            strategy_signals=strategy_signals, 
            aggregated_signal=aggregated_signal,
            strategy_metadata=strategy_metadata
        )
        
        if report_path:
            logger.info(f"Report generated successfully: {report_path}")
            print(f"\nReport generated successfully: {os.path.abspath(report_path)}")
        else:
            logger.error("Failed to generate report")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()