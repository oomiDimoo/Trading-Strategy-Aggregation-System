#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Strategy Wizard Component for the Trading Strategy Aggregation System GUI

This module implements a wizard-like interface for easily adding and configuring
trading strategies with templates and guided configuration.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
                             QPushButton, QWizard, QWizardPage, QLineEdit,
                             QGroupBox, QRadioButton, QButtonGroup, QCheckBox,
                             QStackedWidget, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

logger = logging.getLogger(__name__)

class StrategyWizard(QWizard):
    """
    Wizard for creating and configuring trading strategies with templates
    and guided configuration.
    """
    
    # Signal emitted when a strategy is created
    strategyCreated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set wizard properties
        self.setWindowTitle("Strategy Creation Wizard")
        self.setMinimumSize(700, 500)
        
        # Set wizard style
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add wizard pages
        self.addPage(StrategyTypePage())
        self.addPage(StrategyConfigPage())
        self.addPage(StrategyPreviewPage())
        
        # Connect signals
        self.currentIdChanged.connect(self.on_page_changed)
        self.finished.connect(self.on_wizard_finished)
        
        # Initialize strategy data
        self.strategy_data = {}
    
    def on_page_changed(self, page_id):
        """
        Handle page change event
        
        Args:
            page_id: ID of the current page
        """
        if page_id == 1:  # Strategy Config Page
            # Get strategy type from first page
            strategy_type = self.field("strategy_type")
            template_type = self.field("template_type")
            
            # Configure the config page based on strategy type
            config_page = self.page(1)
            config_page.configure_for_strategy(strategy_type, template_type)
        
        elif page_id == 2:  # Strategy Preview Page
            # Prepare strategy data for preview
            self.prepare_strategy_data()
            
            # Update preview page
            preview_page = self.page(2)
            preview_page.update_preview(self.strategy_data)
    
    def prepare_strategy_data(self):
        """
        Prepare strategy data from wizard fields
        """
        # Get strategy type and template
        strategy_type = self.field("strategy_type")
        template_type = self.field("template_type")
        
        # Get common parameters
        strategy_name = self.field("strategy_name")
        weight = self.field("weight")
        
        # Initialize parameters dictionary
        parameters = {}
        
        # Get strategy-specific parameters
        if strategy_type == "MovingAverageCrossover":
            parameters["fast_period"] = self.field("ma_fast_period")
            parameters["slow_period"] = self.field("ma_slow_period")
            
        elif strategy_type == "RSIStrategy":
            parameters["period"] = self.field("rsi_period")
            parameters["overbought"] = self.field("rsi_overbought")
            parameters["oversold"] = self.field("rsi_oversold")
            
        elif strategy_type == "MACDStrategy":
            parameters["fast_period"] = self.field("macd_fast_period")
            parameters["slow_period"] = self.field("macd_slow_period")
            parameters["signal_period"] = self.field("macd_signal_period")
            
        elif strategy_type == "BollingerBandsStrategy":
            parameters["period"] = self.field("bb_period")
            parameters["std_dev"] = self.field("bb_std_dev")
            parameters["price_source"] = "close"
            
        elif strategy_type == "IchimokuCloudStrategy":
            parameters["tenkan_period"] = self.field("tenkan_period")
            parameters["kijun_period"] = self.field("kijun_period")
            parameters["senkou_b_period"] = self.field("senkou_b_period")
            parameters["displacement"] = self.field("displacement")
        
        # Create strategy data dictionary
        self.strategy_data = {
            "name": strategy_type,
            "display_name": strategy_name if strategy_name else strategy_type,
            "parameters": parameters,
            "weight": weight,
            "template": template_type
        }
    
    def on_wizard_finished(self, result):
        """
        Handle wizard finished event
        
        Args:
            result: Result code (QDialog.Accepted or QDialog.Rejected)
        """
        if result == QDialog.Accepted:
            # Prepare final strategy data
            self.prepare_strategy_data()
            
            # Emit signal with created strategy
            self.strategyCreated.emit(self.strategy_data)


class StrategyTypePage(QWizardPage):
    """
    First page of the strategy wizard for selecting strategy type and template
    """
    
    def __init__(self):
        super().__init__()
        
        # Set page title and subtitle
        self.setTitle("Select Strategy Type")
        self.setSubTitle("Choose the type of trading strategy you want to create and a template to start with.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Strategy type selection
        type_group = QGroupBox("Strategy Type")
        type_layout = QFormLayout()
        
        self.strategy_type_combo = QComboBox()
        self.strategy_type_combo.addItems([
            "MovingAverageCrossover", 
            "RSIStrategy", 
            "MACDStrategy",
            "BollingerBandsStrategy",
            "IchimokuCloudStrategy"
        ])
        self.strategy_type_combo.currentTextChanged.connect(self.on_strategy_type_changed)
        type_layout.addRow("Strategy Type:", self.strategy_type_combo)
        
        # Strategy name
        self.strategy_name_edit = QLineEdit()
        self.strategy_name_edit.setPlaceholderText("Optional custom name for this strategy")
        type_layout.addRow("Strategy Name:", self.strategy_name_edit)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Template selection
        template_group = QGroupBox("Strategy Template")
        template_layout = QVBoxLayout()
        
        # Template description
        self.template_description = QLabel("Templates provide pre-configured parameters for common use cases.")
        self.template_description.setWordWrap(True)
        template_layout.addWidget(self.template_description)
        
        # Template options
        self.template_combo = QComboBox()
        self.update_templates("MovingAverageCrossover")
        template_layout.addWidget(self.template_combo)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Strategy description
        description_group = QGroupBox("Strategy Description")
        description_layout = QVBoxLayout()
        
        self.strategy_description = QLabel()
        self.strategy_description.setWordWrap(True)
        self.update_strategy_description("MovingAverageCrossover")
        description_layout.addWidget(self.strategy_description)
        
        description_group.setLayout(description_layout)
        layout.addWidget(description_group)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
        self.setLayout(layout)
        
        # Register fields
        self.registerField("strategy_type*", self.strategy_type_combo, "currentText")
        self.registerField("strategy_name", self.strategy_name_edit)
        self.registerField("template_type*", self.template_combo, "currentText")
    
    def on_strategy_type_changed(self, strategy_type):
        """
        Handle strategy type change
        
        Args:
            strategy_type: Selected strategy type
        """
        # Update templates for the selected strategy type
        self.update_templates(strategy_type)
        
        # Update strategy description
        self.update_strategy_description(strategy_type)
    
    def update_templates(self, strategy_type):
        """
        Update template options based on strategy type
        
        Args:
            strategy_type: Selected strategy type
        """
        self.template_combo.clear()
        
        if strategy_type == "MovingAverageCrossover":
            self.template_combo.addItems(["Default", "Fast Trading", "Trend Following", "Custom"])
        
        elif strategy_type == "RSIStrategy":
            self.template_combo.addItems(["Default", "Conservative", "Aggressive", "Custom"])
        
        elif strategy_type == "MACDStrategy":
            self.template_combo.addItems(["Default", "Fast Signal", "Slow Signal", "Custom"])
        
        elif strategy_type == "BollingerBandsStrategy":
            self.template_combo.addItems(["Default", "Narrow Bands", "Wide Bands", "Custom"])
        
        elif strategy_type == "IchimokuCloudStrategy":
            self.template_combo.addItems(["Default", "Short-term", "Long-term", "Custom"])
    
    def update_strategy_description(self, strategy_type):
        """
        Update strategy description based on strategy type
        
        Args:
            strategy_type: Selected strategy type
        """
        descriptions = {
            "MovingAverageCrossover": "Generates buy signals when a faster moving average crosses above a slower moving average, and sell signals when it crosses below.",
            "RSIStrategy": "Uses the Relative Strength Index (RSI) to identify overbought and oversold conditions in the market.",
            "MACDStrategy": "Uses the Moving Average Convergence Divergence (MACD) indicator to identify changes in momentum.",
            "BollingerBandsStrategy": "Uses Bollinger Bands to identify when prices are relatively high or low compared to recent price action.",
            "IchimokuCloudStrategy": "Uses the Ichimoku Cloud (Ichimoku Kinko Hyo) system to identify trend direction, momentum, and support/resistance levels."
        }
        
        self.strategy_description.setText(descriptions.get(strategy_type, ""))


class StrategyConfigPage(QWizardPage):
    """
    Second page of the strategy wizard for configuring strategy parameters
    """
    
    def __init__(self):
        super().__init__()
        
        # Set page title and subtitle
        self.setTitle("Configure Strategy Parameters")
        self.setSubTitle("Set the parameters for your trading strategy.")
        
        # Create main layout
        self.layout = QVBoxLayout()
        
        # Common parameters group
        common_group = QGroupBox("Common Parameters")
        common_layout = QFormLayout()
        
        # Weight parameter
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 10.0)
        self.weight_spin.setSingleStep(0.1)
        self.weight_spin.setValue(1.0)
        common_layout.addRow("Weight:", self.weight_spin)
        
        common_group.setLayout(common_layout)
        self.layout.addWidget(common_group)
        
        # Strategy-specific parameters group
        self.params_group = QGroupBox("Strategy Parameters")
        self.params_layout = QStackedWidget()
        
        # Create parameter widgets for each strategy type
        self.create_ma_params()
        self.create_rsi_params()
        self.create_macd_params()
        self.create_bb_params()
        self.create_ichimoku_params()
        
        # Add stacked widget to group
        params_container = QVBoxLayout()
        params_container.addWidget(self.params_layout)
        self.params_group.setLayout(params_container)
        
        self.layout.addWidget(self.params_group)
        
        # Add stretch to push everything to the top
        self.layout.addStretch(1)
        
        self.setLayout(self.layout)
        
        # Register common fields
        self.registerField("weight", self.weight_spin)
    
    def create_ma_params(self):
        """
        Create parameter widgets for Moving Average Crossover strategy
        """
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Fast period
        self.ma_fast_period = QSpinBox()
        self.ma_fast_period.setRange(1, 200)
        self.ma_fast_period.setValue(20)
        layout.addRow("Fast Period:", self.ma_fast_period)
        
        # Slow period
        self.ma_slow_period = QSpinBox()
        self.ma_slow_period.setRange(1, 200)
        self.ma_slow_period.setValue(50)
        layout.addRow("Slow Period:", self.ma_slow_period)
        
        self.params_layout.addWidget(widget)
        
        # Register fields
        self.registerField("ma_fast_period", self.ma_fast_period)
        self.registerField("ma_slow_period", self.ma_slow_period)
    
    def create_rsi_params(self):
        """
        Create parameter widgets for RSI strategy
        """
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Period
        self.rsi_period = QSpinBox()
        self.rsi_period.setRange(1, 100)
        self.rsi_period.setValue(14)
        layout.addRow("Period:", self.rsi_period)
        
        # Overbought level
        self.rsi_overbought = QSpinBox()
        self.rsi_overbought.setRange(50, 100)
        self.rsi_overbought.setValue(70)
        layout.addRow("Overbought Level:", self.rsi_overbought)
        
        # Oversold level
        self.rsi_oversold = QSpinBox()
        self.rsi_oversold.setRange(0, 50)
        self.rsi_oversold.setValue(30)
        layout.addRow("Oversold Level:", self.rsi_oversold)
        
        self.params_layout.addWidget(widget)
        
        # Register fields
        self.registerField("rsi_period", self.rsi_period)
        self.registerField("rsi_overbought", self.rsi_overbought)
        self.registerField("rsi_oversold", self.rsi_oversold)
    
    def create_macd_params(self):
        """
        Create parameter widgets for MACD strategy
        """
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Fast period
        self.macd_fast_period = QSpinBox()
        self.macd_fast_period.setRange(1, 100)
        self.macd_fast_period.setValue(12)
        layout.addRow("Fast Period:", self.macd_fast_period)
        
        # Slow period
        self.macd_slow_period = QSpinBox()
        self.macd_slow_period.setRange(1, 100)
        self.macd_slow_period.setValue(26)
        layout.addRow("Slow Period:", self.macd_slow_period)
        
        # Signal period
        self.macd_signal_period = QSpinBox()
        self.macd_signal_period.setRange(1, 100)
        self.macd_signal_period.setValue(9)
        layout.addRow("Signal Period:", self.macd_signal_period)
        
        self.params_layout.addWidget(widget)
        
        # Register fields
        self.registerField("macd_fast_period", self.macd_fast_period)
        self.registerField("macd_slow_period", self.macd_slow_period)
        self.registerField("macd_signal_period", self.macd_signal_period)
    
    def create_bb_params(self):
        """
        Create parameter widgets for Bollinger Bands strategy
        """
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Period
        self.bb_period = QSpinBox()
        self.bb_period.setRange(5, 200)
        self.bb_period.setValue(20)
        layout.addRow("Period:", self.bb_period)
        
        # Standard deviation
        self.bb_std_dev = QDoubleSpinBox()
        self.bb_std_dev.setRange(0.5, 5.0)
        self.bb_std_dev.setSingleStep(0.1)
        self.bb_std_dev.setValue(2.0)
        layout.addRow("Standard Deviation:", self.bb_std_dev)
        
        self.params_layout.addWidget(widget)
        
        # Register fields
        self.registerField("bb_period", self.bb_period)
        self.registerField("bb_std_dev", self.bb_std_dev)
    
    def create_ichimoku_params(self):
        """
        Create parameter widgets for Ichimoku Cloud strategy
        """
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Tenkan period
        self.tenkan_period = QSpinBox()
        self.tenkan_period.setRange(1, 100)
        self.tenkan_period.setValue(9)
        layout.addRow("Tenkan Period:", self.tenkan_period)
        
        # Kijun period
        self.kijun_period = QSpinBox()
        self.kijun_period.setRange(1, 100)
        self.kijun_period.setValue(26)
        layout.addRow("Kijun Period:", self.kijun_period)
        
        # Senkou B period
        self.senkou_b_period = QSpinBox()
        self.senkou_b_period.setRange(1, 100)
        self.senkou_b_period.setValue(52)
        layout.addRow("Senkou B Period:", self.senkou_b_period)
        
        # Displacement
        self.displacement = QSpinBox()
        self.displacement.setRange(1, 100)
        self.displacement.setValue(26)
        layout.addRow("Displacement:", self.displacement)
        
        self.params_layout.addWidget(widget)
        
        # Register fields
        self.registerField("tenkan_period", self.tenkan_period)
        self.registerField("kijun_period", self.kijun_period)
        self.registerField("senkou_b_period", self.senkou_b_period)
        self.registerField("displacement", self.displacement)
    
    def configure_for_strategy(self, strategy_type, template_type):
        """
        Configure the page for the selected strategy type and template
        
        Args:
            strategy_type: Selected strategy type
            template_type: Selected template type
        """
        # Set the appropriate parameter widget
        if strategy_type == "MovingAverageCrossover":
            self.params_layout.setCurrentIndex(0)
            self.apply_ma_template(template_type)
        
        elif strategy_type == "RSIStrategy":
            self.params_layout.setCurrentIndex(1)
            self.apply_rsi_template(template_type)
        
        elif strategy_type == "MACDStrategy":
            self.params_layout.setCurrentIndex(2)
            self.apply_macd_template(template_type)
        
        elif strategy_type == "BollingerBandsStrategy":
            self.params_layout.setCurrentIndex(3)
            self.apply_bb_template(template_type)
        
        elif strategy_type == "IchimokuCloudStrategy":
            self.params_layout.setCurrentIndex(4)
            self.apply_ichimoku_template(template_type)
    
    def apply_ma_template(self, template_type):
        """
        Apply Moving Average Crossover template
        
        Args:
            template_type: Selected template type
        """
        if template_type == "Default":
            self.ma_fast_period.setValue(20)
            self.ma_slow_period.setValue(50)
        
        elif template_type == "Fast Trading":
            self.ma_fast_period.setValue(5)
            self.ma_slow_period.setValue(20)
        
        elif template_type == "Trend Following":
            self.ma_fast_period.setValue(50)
            self.ma_slow_period.setValue(200)
    
    def apply_rsi_template(self, template_type):
        """
        Apply RSI template
        
        Args:
            template_type: Selected template type
        """
        if template_type == "Default":
            self.rsi_period.setValue(14)
            self.rsi_overbought.setValue(70)
            self.rsi_oversold.setValue(30)
        
        elif template_type == "Conservative":
            self.rsi_period.setValue(21)
            self.rsi_overbought.setValue(80)
            self.rsi_oversold.setValue(20)
        
        elif template_type == "Aggressive":
            self.rsi_period.setValue(7)
            self.rsi_overbought.setValue(65)
            self.rsi_oversold.setValue(35)
    
    def apply_macd_template(self, template_type):
        """
        Apply MACD template
        
        Args:
            template_type: Selected template type
        """
        if template_type == "Default":
            self.macd_fast_period.setValue(12)
            self.macd_slow_period.setValue(26)
            self.macd_signal_period.setValue(9)
        
        elif template_type == "Fast Signal":
            self.macd_fast_period.setValue(8)
            self.macd_slow_period.setValue(17)
            self.macd_signal_period.setValue(5)
        
        elif template_type == "Slow Signal":
            self.macd_fast_period.setValue(19)
            self.macd_slow_period.setValue(39)
            self.macd_signal_period.setValue(13)
    
    def apply_bb_template(self, template_type):
        """
        Apply Bollinger Bands template
        
        Args:
            template_type: Selected template type
        """
        if template_type == "Default":
            self.bb_period.setValue(20)
            self.bb_std_dev.setValue(2.0)
        
        elif template_type == "Narrow Bands":
            self.bb_period.setValue(20)
            self.bb_std_dev.setValue(1.5)
        
        elif template_type == "Wide Bands":
            self.bb_period.setValue(20)
            self.bb_std_dev.setValue(2.5)
    
    def apply_ichimoku_template(self, template_type):
        """
        Apply Ichimoku Cloud template
        
        Args:
            template_type: Selected template type
        """
        if template_type == "Default":
            self.tenkan_period.setValue(9)
            self.kijun_period.setValue(26)
            self.senkou_b_period.setValue(52)
            self.displacement.setValue(26)
        
        elif template_type == "Short-term":
            self.tenkan_period.setValue(7)
            self.kijun_period.setValue(22)
            self.senkou_b_period.setValue(44)
            self.displacement.setValue(22)
        
        elif template_type == "Long-term":
            self.tenkan_period.setValue(10)
            self.kijun_period.setValue(30)
            self.senkou_b_period.setValue(60)
            self.displacement.setValue(30)


class StrategyPreviewPage(QWizardPage):
    """
    Third page of the strategy wizard for previewing the strategy configuration
    """
    
    def __init__(self):
        super().__init__()
        
        # Set page title and subtitle
        self.setTitle("Strategy Preview")
        self.setSubTitle("Review your strategy configuration before creating it.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Preview text
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        self.setLayout(layout)
    
    def update_preview(self, strategy_data):
        """
        Update the preview with strategy data
        
        Args:
            strategy_data: Dictionary containing strategy configuration
        """
        # Create preview text
        preview = f"<h3>Strategy Configuration</h3>"
        preview += f"<p><b>Strategy Type:</b> {strategy_data.get('name', '')}</p>"
        
        if strategy_data.get('display_name'):
            preview += f"<p><b>Strategy Name:</b> {strategy_data.get('display_name', '')}</p>"
        
        preview += f"<p><b>Template:</b> {strategy_data.get('template', '')}</p>"
        preview += f"<p><b>Weight:</b> {strategy_data.get('weight', 1.0)}</p>"
        
        # Add parameters
        preview += f"<h3>Parameters</h3>"
        preview += "<ul>"
        
        for key, value in strategy_data.get('parameters', {}).items():
            preview += f"<li><b>{key}:</b> {value}</li>"
        
        preview += "</ul>"
        
        # Set preview text
        self.preview_text.setHtml(preview)