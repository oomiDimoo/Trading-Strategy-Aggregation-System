#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aggregator Tab Component for the Trading Strategy Aggregation System GUI

This module implements the signal aggregation configuration tab of the GUI application.
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QDoubleSpinBox, QGroupBox, QLabel)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class AggregatorTab(QWidget):
    """Tab for configuring signal aggregation settings"""
    
    def __init__(self, config_controller):
        super().__init__()
        self.config_controller = config_controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create aggregation settings group
        aggregation_group = QGroupBox("Aggregation Settings")
        aggregation_layout = QFormLayout(aggregation_group)
        
        # Aggregation method
        self.method_combo = QComboBox()
        self.method_combo.addItems(["weighted_average", "majority_vote", "consensus"])
        self.method_combo.currentTextChanged.connect(self.on_method_changed)
        aggregation_layout.addRow("Aggregation Method:", self.method_combo)
        
        # Description label
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        aggregation_layout.addRow("", self.description_label)
        
        # Threshold
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.05)
        self.threshold_spin.setValue(0.5)
        aggregation_layout.addRow("Signal Threshold:", self.threshold_spin)
        
        # Add group to main layout
        main_layout.addWidget(aggregation_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
        
        # Initialize with current method
        self.on_method_changed(self.method_combo.currentText())
    
    def on_method_changed(self, method):
        """Handle aggregation method change"""
        # Update description based on selected method
        if method == "weighted_average":
            description = "Combines signals using a weighted average of each strategy's signal value. "\
                         "Strategies with higher weights have more influence on the final signal."
        elif method == "majority_vote":
            description = "Each strategy votes for a buy or sell signal based on its signal value. "\
                         "The final decision is based on the majority of votes, weighted by strategy importance."
        elif method == "consensus":
            description = "Requires all strategies to agree on the signal. "\
                         "This is the most conservative approach and may generate fewer signals."
        else:
            description = ""
        
        self.description_label.setText(description)
    
    def update_from_config(self):
        """Update UI from configuration"""
        aggregator_config = self.config_controller.get_aggregator_config()
        
        # Set aggregation method
        method = aggregator_config.get("method", "weighted_average")
        index = self.method_combo.findText(method)
        if index >= 0:
            self.method_combo.setCurrentIndex(index)
        
        # Set threshold
        self.threshold_spin.setValue(aggregator_config.get("threshold", 0.5))
    
    def update_config(self):
        """Update configuration from UI"""
        aggregator_config = {
            "method": self.method_combo.currentText(),
            "threshold": self.threshold_spin.value()
        }
        
        # Update configuration
        self.config_controller.set_aggregator_config(aggregator_config)