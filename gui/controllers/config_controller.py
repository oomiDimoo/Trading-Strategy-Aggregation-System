#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration Controller for the Trading Strategy Aggregation System GUI

This module handles loading, saving, and managing the application configuration.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)

class ConfigController:
    """Controller for managing application configuration"""
    
    def __init__(self):
        """Initialize the configuration controller"""
        self.config = {}
        self.config_path = "config/config.json"
    
    def create_default_config(self) -> Dict[str, Any]:
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
        self.config = config
        return config
    
    def load_config(self, config_path: str) -> bool:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                self.config_path = config_path
                logger.info(f"Configuration loaded from {config_path}")
                return True
            else:
                logger.warning(f"Configuration file not found: {config_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def save_config(self, config_path: str) -> bool:
        """Save configuration to a JSON file"""
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.config_path = config_path
            logger.info(f"Configuration saved to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self.config
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the current configuration"""
        self.config = config
    
    def get_data_source_config(self) -> Dict[str, Any]:
        """Get the data source configuration"""
        return self.config.get("data_source", {})
    
    def set_data_source_config(self, data_source_config: Dict[str, Any]) -> None:
        """Set the data source configuration"""
        self.config["data_source"] = data_source_config
    
    def get_strategies_config(self) -> List[Dict[str, Any]]:
        """Get the strategies configuration"""
        return self.config.get("strategies", [])
    
    def set_strategies_config(self, strategies_config: List[Dict[str, Any]]) -> None:
        """Set the strategies configuration"""
        self.config["strategies"] = strategies_config
    
    def get_aggregator_config(self) -> Dict[str, Any]:
        """Get the aggregator configuration"""
        return self.config.get("aggregator", {})
    
    def set_aggregator_config(self, aggregator_config: Dict[str, Any]) -> None:
        """Set the aggregator configuration"""
        self.config["aggregator"] = aggregator_config
    
    def get_report_config(self) -> Dict[str, Any]:
        """Get the report configuration"""
        return self.config.get("report", {})
    
    def set_report_config(self, report_config: Dict[str, Any]) -> None:
        """Set the report configuration"""
        self.config["report"] = report_config