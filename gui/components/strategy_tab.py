#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Strategy Tab Component for the Trading Strategy Aggregation System GUI

This module implements the strategy configuration tab of the GUI application.
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGroupBox, QMessageBox)
from gui.components.strategy_wizard import StrategyWizard
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class StrategyTab(QWidget):
    """Tab for configuring trading strategies"""
    
    def __init__(self, config_controller):
        super().__init__()
        self.config_controller = config_controller
        self.strategies = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create strategies table
        self.strategies_table = QTableWidget()
        self.strategies_table.setColumnCount(3)
        self.strategies_table.setHorizontalHeaderLabels(["Strategy", "Parameters", "Weight"])
        self.strategies_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.strategies_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.strategies_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.strategies_table.itemSelectionChanged.connect(self.on_strategy_selected)
        main_layout.addWidget(self.strategies_table)
        
        # Create buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add strategy button
        self.add_button = QPushButton("Add Strategy")
        self.add_button.clicked.connect(self.add_strategy)
        buttons_layout.addWidget(self.add_button)
        
        # Add wizard button
        self.wizard_button = QPushButton("Strategy Wizard")
        self.wizard_button.clicked.connect(self.open_strategy_wizard)
        buttons_layout.addWidget(self.wizard_button)
        
        # Edit strategy button
        self.edit_button = QPushButton("Edit Strategy")
        self.edit_button.clicked.connect(self.edit_strategy)
        self.edit_button.setEnabled(False)
        buttons_layout.addWidget(self.edit_button)
        
        # Remove strategy button
        self.remove_button = QPushButton("Remove Strategy")
        self.remove_button.clicked.connect(self.remove_strategy)
        self.remove_button.setEnabled(False)
        buttons_layout.addWidget(self.remove_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Create strategy configuration group
        strategy_group = QGroupBox("Strategy Configuration")
        strategy_layout = QFormLayout(strategy_group)
        
        # Strategy type
        self.strategy_type_combo = QComboBox()
        self.strategy_type_combo.addItems(["MovingAverageCrossover", "RSIStrategy", "MACDStrategy", "BollingerBandsStrategy", "IchimokuCloudStrategy"])
        self.strategy_type_combo.currentTextChanged.connect(self.on_strategy_type_changed)
        strategy_layout.addRow("Strategy Type:", self.strategy_type_combo)
        
        # Strategy weight
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 10.0)
        self.weight_spin.setSingleStep(0.1)
        self.weight_spin.setValue(1.0)
        strategy_layout.addRow("Weight:", self.weight_spin)
        
        # Moving Average Crossover parameters
        self.ma_group = QGroupBox("Moving Average Parameters")
        ma_layout = QFormLayout(self.ma_group)
        
        self.fast_period_spin = QSpinBox()
        self.fast_period_spin.setRange(1, 200)
        self.fast_period_spin.setValue(20)
        ma_layout.addRow("Fast Period:", self.fast_period_spin)
        
        self.slow_period_spin = QSpinBox()
        self.slow_period_spin.setRange(1, 200)
        self.slow_period_spin.setValue(50)
        ma_layout.addRow("Slow Period:", self.slow_period_spin)
        
        # RSI parameters
        self.rsi_group = QGroupBox("RSI Parameters")
        self.rsi_group.setVisible(False)
        rsi_layout = QFormLayout(self.rsi_group)
        
        self.rsi_period_spin = QSpinBox()
        self.rsi_period_spin.setRange(1, 100)
        self.rsi_period_spin.setValue(14)
        rsi_layout.addRow("Period:", self.rsi_period_spin)
        
        self.overbought_spin = QSpinBox()
        self.overbought_spin.setRange(50, 100)
        self.overbought_spin.setValue(70)
        rsi_layout.addRow("Overbought Level:", self.overbought_spin)
        
        self.oversold_spin = QSpinBox()
        self.oversold_spin.setRange(0, 50)
        self.oversold_spin.setValue(30)
        rsi_layout.addRow("Oversold Level:", self.oversold_spin)
        
        # MACD parameters
        self.macd_group = QGroupBox("MACD Parameters")
        self.macd_group.setVisible(False)
        macd_layout = QFormLayout(self.macd_group)
        
        self.macd_fast_period_spin = QSpinBox()
        self.macd_fast_period_spin.setRange(1, 100)
        self.macd_fast_period_spin.setValue(12)
        macd_layout.addRow("Fast Period:", self.macd_fast_period_spin)
        
        self.macd_slow_period_spin = QSpinBox()
        self.macd_slow_period_spin.setRange(1, 100)
        self.macd_slow_period_spin.setValue(26)
        macd_layout.addRow("Slow Period:", self.macd_slow_period_spin)
        
        self.signal_period_spin = QSpinBox()
        self.signal_period_spin.setRange(1, 100)
        self.signal_period_spin.setValue(9)
        macd_layout.addRow("Signal Period:", self.signal_period_spin)
        
        # Bollinger Bands parameters
        self.bb_group = QGroupBox("Bollinger Bands Parameters")
        self.bb_group.setVisible(False)
        bb_layout = QFormLayout(self.bb_group)
        
        self.bb_period_spin = QSpinBox()
        self.bb_period_spin.setRange(5, 200)
        self.bb_period_spin.setValue(20)
        bb_layout.addRow("Period:", self.bb_period_spin)
        
        self.bb_std_dev_spin = QDoubleSpinBox()
        self.bb_std_dev_spin.setRange(0.5, 5.0)
        self.bb_std_dev_spin.setSingleStep(0.1)
        self.bb_std_dev_spin.setValue(2.0)
        bb_layout.addRow("Standard Deviation:", self.bb_std_dev_spin)
        
        # Ichimoku Cloud parameters
        self.ichimoku_group = QGroupBox("Ichimoku Cloud Parameters")
        self.ichimoku_group.setVisible(False)
        ichimoku_layout = QFormLayout(self.ichimoku_group)
        
        self.tenkan_period_spin = QSpinBox()
        self.tenkan_period_spin.setRange(1, 100)
        self.tenkan_period_spin.setValue(9)
        ichimoku_layout.addRow("Tenkan Period:", self.tenkan_period_spin)
        
        self.kijun_period_spin = QSpinBox()
        self.kijun_period_spin.setRange(1, 100)
        self.kijun_period_spin.setValue(26)
        ichimoku_layout.addRow("Kijun Period:", self.kijun_period_spin)
        
        self.senkou_b_period_spin = QSpinBox()
        self.senkou_b_period_spin.setRange(1, 100)
        self.senkou_b_period_spin.setValue(52)
        ichimoku_layout.addRow("Senkou B Period:", self.senkou_b_period_spin)
        
        self.displacement_spin = QSpinBox()
        self.displacement_spin.setRange(1, 100)
        self.displacement_spin.setValue(26)
        ichimoku_layout.addRow("Displacement:", self.displacement_spin)
        
        # Add parameter groups to main layout
        main_layout.addWidget(strategy_group)
        main_layout.addWidget(self.ma_group)
        main_layout.addWidget(self.rsi_group)
        main_layout.addWidget(self.macd_group)
        main_layout.addWidget(self.bb_group)
        main_layout.addWidget(self.ichimoku_group)
        
        # Add save button
        save_layout = QHBoxLayout()
        save_layout.addStretch(1)
        
        self.save_button = QPushButton("Save Strategy")
        self.save_button.clicked.connect(self.save_strategy)
        save_layout.addWidget(self.save_button)
        
        main_layout.addLayout(save_layout)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
        
        # Initialize with current strategy type
        self.on_strategy_type_changed(self.strategy_type_combo.currentText())
    
    def on_strategy_type_changed(self, strategy_type):
        """Handle strategy type change"""
        # Show/hide strategy-specific parameters
        self.ma_group.setVisible(strategy_type == "MovingAverageCrossover")
        self.rsi_group.setVisible(strategy_type == "RSIStrategy")
        self.macd_group.setVisible(strategy_type == "MACDStrategy")
        self.bb_group.setVisible(strategy_type == "BollingerBandsStrategy")
        self.ichimoku_group.setVisible(strategy_type == "IchimokuCloudStrategy")
    
    def on_strategy_selected(self):
        """Handle strategy selection"""
        selected_rows = self.strategies_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)
    
    def update_strategies_table(self):
        """Update the strategies table"""
        self.strategies_table.setRowCount(0)
        
        for i, strategy in enumerate(self.strategies):
            self.strategies_table.insertRow(i)
            
            # Strategy name
            name_item = QTableWidgetItem(strategy["name"])
            self.strategies_table.setItem(i, 0, name_item)
            
            # Parameters
            params_str = ", ".join([f"{k}: {v}" for k, v in strategy["parameters"].items()])
            params_item = QTableWidgetItem(params_str)
            self.strategies_table.setItem(i, 1, params_item)
            
            # Weight
            weight_item = QTableWidgetItem(str(strategy["weight"]))
            self.strategies_table.setItem(i, 2, weight_item)
    
    def add_strategy(self):
        """Add a new strategy"""
        # Reset form for new strategy
        self.strategy_type_combo.setCurrentIndex(0)
        self.weight_spin.setValue(1.0)
        self.fast_period_spin.setValue(20)
        self.slow_period_spin.setValue(50)
        self.rsi_period_spin.setValue(14)
        self.overbought_spin.setValue(70)
        self.oversold_spin.setValue(30)
        self.macd_fast_period_spin.setValue(12)
        self.macd_slow_period_spin.setValue(26)
        self.signal_period_spin.setValue(9)
        self.bb_period_spin.setValue(20)
        self.bb_std_dev_spin.setValue(2.0)
        self.tenkan_period_spin.setValue(9)
        self.kijun_period_spin.setValue(26)
        self.senkou_b_period_spin.setValue(52)
        self.displacement_spin.setValue(26)
        
        # Show appropriate parameter group
        self.on_strategy_type_changed(self.strategy_type_combo.currentText())
        
    def open_strategy_wizard(self):
        """Open the strategy wizard dialog"""
        wizard = StrategyWizard(self)
        wizard.strategyCreated.connect(self.add_strategy_from_wizard)
        wizard.exec_()  # Show the wizard as a modal dialog
    
    def add_strategy_from_wizard(self, strategy_data):
        """Add a strategy created from the wizard
        
        Args:
            strategy_data: Dictionary containing strategy configuration
        """
        # Create strategy configuration
        strategy = {
            "name": strategy_data["name"],
            "parameters": strategy_data["parameters"],
            "weight": strategy_data["weight"]
        }
        
        # Add to strategies list
        self.strategies.append(strategy)
        
        # Update table
        self.update_strategies_table()
    
    def edit_strategy(self):
        """Edit the selected strategy"""
        selected_rows = self.strategies_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        strategy = self.strategies[row]
        
        # Set form values from strategy
        strategy_type = strategy["name"]
        index = self.strategy_type_combo.findText(strategy_type)
        if index >= 0:
            self.strategy_type_combo.setCurrentIndex(index)
        
        self.weight_spin.setValue(strategy["weight"])
        
        # Set parameters based on strategy type
        params = strategy["parameters"]
        if strategy_type == "MovingAverageCrossover":
            self.fast_period_spin.setValue(params.get("fast_period", 20))
            self.slow_period_spin.setValue(params.get("slow_period", 50))
        elif strategy_type == "RSIStrategy":
            self.rsi_period_spin.setValue(params.get("period", 14))
            self.overbought_spin.setValue(params.get("overbought", 70))
            self.oversold_spin.setValue(params.get("oversold", 30))
        elif strategy_type == "MACDStrategy":
            self.macd_fast_period_spin.setValue(params.get("fast_period", 12))
            self.macd_slow_period_spin.setValue(params.get("slow_period", 26))
            self.signal_period_spin.setValue(params.get("signal_period", 9))
        elif strategy_type == "BollingerBandsStrategy":
            self.bb_period_spin.setValue(params.get("period", 20))
            self.bb_std_dev_spin.setValue(params.get("std_dev", 2.0))
        elif strategy_type == "IchimokuCloudStrategy":
            self.tenkan_period_spin.setValue(params.get("tenkan_period", 9))
            self.kijun_period_spin.setValue(params.get("kijun_period", 26))
            self.senkou_b_period_spin.setValue(params.get("senkou_b_period", 52))
            self.displacement_spin.setValue(params.get("displacement", 26))
        
        # Delete the strategy (will be re-added when saved)
        self.strategies.pop(row)
        self.update_strategies_table()
    
    def remove_strategy(self):
        """Remove the selected strategy"""
        selected_rows = self.strategies_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        reply = QMessageBox.question(self, "Remove Strategy",
                                    f"Are you sure you want to remove this strategy?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.strategies.pop(row)
            self.update_strategies_table()
    
    def save_strategy(self):
        """Save the current strategy configuration"""
        strategy_type = self.strategy_type_combo.currentText()
        weight = self.weight_spin.value()
        
        # Get parameters based on strategy type
        parameters = {}
        if strategy_type == "MovingAverageCrossover":
            parameters = {
                "fast_period": self.fast_period_spin.value(),
                "slow_period": self.slow_period_spin.value()
            }
        elif strategy_type == "RSIStrategy":
            parameters = {
                "period": self.rsi_period_spin.value(),
                "overbought": self.overbought_spin.value(),
                "oversold": self.oversold_spin.value()
            }
        elif strategy_type == "MACDStrategy":
            parameters = {
                "fast_period": self.macd_fast_period_spin.value(),
                "slow_period": self.macd_slow_period_spin.value(),
                "signal_period": self.signal_period_spin.value()
            }
        elif strategy_type == "BollingerBandsStrategy":
            parameters = {
                "period": self.bb_period_spin.value(),
                "std_dev": self.bb_std_dev_spin.value(),
                "price_source": "close"
            }
        elif strategy_type == "IchimokuCloudStrategy":
            parameters = {
                "tenkan_period": self.tenkan_period_spin.value(),
                "kijun_period": self.kijun_period_spin.value(),
                "senkou_b_period": self.senkou_b_period_spin.value(),
                "displacement": self.displacement_spin.value()
            }
        
        # Create strategy configuration
        strategy = {
            "name": strategy_type,
            "parameters": parameters,
            "weight": weight
        }
        
        # Add to strategies list
        self.strategies.append(strategy)
        
        # Update table
        self.update_strategies_table()
    
    def update_from_config(self):
        """Update UI from configuration"""
        # Get strategies from configuration
        self.strategies = self.config_controller.get_strategies_config()
        
        # Update table
        self.update_strategies_table()
    
    def update_config(self):
        """Update configuration from UI"""
        # Update configuration with current strategies
        self.config_controller.set_strategies_config(self.strategies)