#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Union, Optional, Type
from abc import ABC, abstractmethod

from strategies.strategy_interface import Strategy

logger = logging.getLogger(__name__)

class StrategyTemplate(ABC):
    """
    Abstract base class for strategy templates.
    
    Strategy templates provide a standardized way to create new strategies
    by implementing common patterns and reducing boilerplate code.
    """
    
    @abstractmethod
    def create_strategy(self, name: str, parameters: Dict[str, Any] = None) -> Strategy:
        """
        Create a new strategy instance based on this template.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
            
        Returns:
            A new strategy instance
        """
        pass


class IndicatorBasedTemplate(StrategyTemplate):
    """
    Template for creating indicator-based strategies.
    
    This template simplifies the creation of strategies that generate signals
    based on technical indicators crossing thresholds.
    """
    
    def __init__(self, strategy_class: Type[Strategy], default_parameters: Dict[str, Any] = None):
        """
        Initialize the indicator-based template.
        
        Args:
            strategy_class: The strategy class to instantiate
            default_parameters: Default parameters for the strategy
        """
        self.strategy_class = strategy_class
        self.default_parameters = default_parameters or {}
    
    def create_strategy(self, name: str, parameters: Dict[str, Any] = None) -> Strategy:
        """
        Create a new indicator-based strategy instance.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
            
        Returns:
            A new strategy instance
        """
        # Merge default parameters with provided parameters
        merged_parameters = self.default_parameters.copy()
        if parameters:
            merged_parameters.update(parameters)
        
        # Create and return the strategy instance
        return self.strategy_class(name, merged_parameters)


class PatternRecognitionTemplate(StrategyTemplate):
    """
    Template for creating pattern recognition strategies.
    
    This template simplifies the creation of strategies that generate signals
    based on chart patterns like head and shoulders, triangles, etc.
    """
    
    def __init__(self, strategy_class: Type[Strategy], default_parameters: Dict[str, Any] = None):
        """
        Initialize the pattern recognition template.
        
        Args:
            strategy_class: The strategy class to instantiate
            default_parameters: Default parameters for the strategy
        """
        self.strategy_class = strategy_class
        self.default_parameters = default_parameters or {
            "pattern_lookback": 20,
            "confirmation_threshold": 0.7,
            "signal_threshold": 0.0
        }
    
    def create_strategy(self, name: str, parameters: Dict[str, Any] = None) -> Strategy:
        """
        Create a new pattern recognition strategy instance.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
            
        Returns:
            A new strategy instance
        """
        # Merge default parameters with provided parameters
        merged_parameters = self.default_parameters.copy()
        if parameters:
            merged_parameters.update(parameters)
        
        # Create and return the strategy instance
        return self.strategy_class(name, merged_parameters)


class VolumeBasedTemplate(StrategyTemplate):
    """
    Template for creating volume-based strategies.
    
    This template simplifies the creation of strategies that generate signals
    based on volume patterns and price-volume relationships.
    """
    
    def __init__(self, strategy_class: Type[Strategy], default_parameters: Dict[str, Any] = None):
        """
        Initialize the volume-based template.
        
        Args:
            strategy_class: The strategy class to instantiate
            default_parameters: Default parameters for the strategy
        """
        self.strategy_class = strategy_class
        self.default_parameters = default_parameters or {
            "volume_lookback": 20,
            "volume_threshold": 1.5,
            "price_threshold": 0.0
        }
    
    def create_strategy(self, name: str, parameters: Dict[str, Any] = None) -> Strategy:
        """
        Create a new volume-based strategy instance.
        
        Args:
            name: The name of the strategy
            parameters: Dictionary of strategy-specific parameters
            
        Returns:
            A new strategy instance
        """
        # Merge default parameters with provided parameters
        merged_parameters = self.default_parameters.copy()
        if parameters:
            merged_parameters.update(parameters)
        
        # Create and return the strategy instance
        return self.strategy_class(name, merged_parameters)