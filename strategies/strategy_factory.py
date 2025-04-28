#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import logging
from typing import Dict, Any, Optional, Type

from strategies.strategy_interface import Strategy
from strategies.strategy_template import IndicatorBasedTemplate, PatternRecognitionTemplate, VolumeBasedTemplate

logger = logging.getLogger(__name__)

class StrategyFactory:
    """
    Factory class for creating strategy instances.
    
    This factory is responsible for dynamically loading and instantiating
    strategy classes based on their name and parameters.
    """
    
    def __init__(self):
        """
        Initialize the strategy factory.
        """
        self.registered_strategies = {}
    
    def register_strategy(self, strategy_name: str, strategy_class: Type[Strategy]) -> None:
        """
        Register a strategy class with the factory.
        
        Args:
            strategy_name: The name of the strategy
            strategy_class: The strategy class (must inherit from Strategy)
        """
        if not issubclass(strategy_class, Strategy):
            raise TypeError(f"Strategy class must inherit from Strategy interface")
        
        self.registered_strategies[strategy_name] = strategy_class
        logger.info(f"Registered strategy: {strategy_name}")
    
    def create_strategy(self, strategy_name: str, parameters: Dict[str, Any] = None) -> Optional[Strategy]:
        """
        Create a new instance of the specified strategy.
        
        Args:
            strategy_name: The name of the strategy to create
            parameters: Dictionary of strategy-specific parameters
            
        Returns:
            A new strategy instance or None if creation failed
        """
        # Check if strategy is already registered
        if strategy_name in self.registered_strategies:
            try:
                strategy_class = self.registered_strategies[strategy_name]
                return strategy_class(strategy_name, parameters)
            except Exception as e:
                logger.error(f"Error creating strategy {strategy_name}: {e}")
                return None
        
        # Try to dynamically import the strategy
        try:
            # Convert strategy name to module path (e.g., "MovingAverageCrossover" -> "moving_average_crossover")
            module_name = strategy_name.lower()
            
            # Import the module
            module_path = f"strategies.{module_name}"
            module = importlib.import_module(module_path)
            
            # Get the strategy class (assume it's named the same as the strategy_name)
            strategy_class = getattr(module, strategy_name)
            
            # Register the strategy for future use
            self.register_strategy(strategy_name, strategy_class)
            
            # Create and return the strategy instance
            return strategy_class(strategy_name, parameters)
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not find strategy {strategy_name}: {e}")
        except Exception as e:
            logger.error(f"Error creating strategy {strategy_name}: {e}")
        
        return None
        
    def load_all_strategies(self) -> None:
        """
        Load all available strategy classes.
        """
        # Import strategy modules
        from strategies.moving_average_crossover import MovingAverageCrossover
        from strategies.macd_strategy import MACDStrategy
        from strategies.rsi_strategy import RSIStrategy
        from strategies.bollinger_bands_strategy import BollingerBandsStrategy
        from strategies.ichimoku_cloud_strategy import IchimokuCloudStrategy
        from strategies.volume_profile_strategy import VolumeProfileStrategy
        from strategies.fibonacci_retracement_strategy import FibonacciRetracementStrategy
        
        # Register strategies
        self.register_strategy("Moving Average Crossover", MovingAverageCrossover)
        self.register_strategy("MACD", MACDStrategy)
        self.register_strategy("RSI", RSIStrategy)
        self.register_strategy("Bollinger Bands", BollingerBandsStrategy)
        self.register_strategy("Ichimoku Cloud", IchimokuCloudStrategy)
        self.register_strategy("Volume Profile", VolumeProfileStrategy)
        self.register_strategy("Fibonacci Retracement", FibonacciRetracementStrategy)
        
        logger.info("Loaded all available strategies")
        
    def get_strategy_templates(self) -> Dict[str, Any]:
        """
        Get available strategy templates.
        
        Returns:
            Dictionary of strategy templates
        """
        # Import strategy classes
        from strategies.moving_average_crossover import MovingAverageCrossover
        from strategies.macd_strategy import MACDStrategy
        from strategies.rsi_strategy import RSIStrategy
        from strategies.bollinger_bands_strategy import BollingerBandsStrategy
        from strategies.volume_profile_strategy import VolumeProfileStrategy
        from strategies.fibonacci_retracement_strategy import FibonacciRetracementStrategy
        
        # Create templates
        templates = {
            "Indicator Based": IndicatorBasedTemplate(MovingAverageCrossover, {
                "fast_period": 20,
                "slow_period": 50,
                "signal_threshold": 0.0
            }),
            "Volume Based": VolumeBasedTemplate(VolumeProfileStrategy, {
                "num_bins": 20,
                "lookback_period": 100,
                "volume_threshold": 0.8
            }),
            "Pattern Recognition": PatternRecognitionTemplate(FibonacciRetracementStrategy, {
                "trend_period": 50,
                "swing_lookback": 20,
                "retracement_levels": [0.236, 0.382, 0.5, 0.618, 0.786]
            })
        }
        
        return templates