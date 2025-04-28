#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Report Tab Component for the Trading Strategy Aggregation System GUI

This module implements the report configuration tab of the GUI application.
"""

import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QComboBox, QCheckBox, QLineEdit,
                             QPushButton, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class ReportTab(QWidget):
    """Tab for configuring report generation settings"""
    
    def __init__(self, config_controller):
        super().__init__()
        self.config_controller = config_controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create report settings group
        report_group = QGroupBox("Report Settings")
        report_layout = QFormLayout(report_group)
        
        # Report format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["html", "csv"])
        report_layout.addRow("Report Format:", self.format_combo)
        
        # Include plots
        self.include_plots_check = QCheckBox()
        self.include_plots_check.setChecked(True)
        report_layout.addRow("Include Plots:", self.include_plots_check)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText("reports/output")
        self.output_dir_edit.setReadOnly(True)
        output_dir_layout.addWidget(self.output_dir_edit)
        
        # Browse button
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(browse_button)
        
        report_layout.addRow("Output Directory:", output_dir_layout)
        
        # Add group to main layout
        main_layout.addWidget(report_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
    
    def browse_output_dir(self):
        """Open directory dialog to select output directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory",
                                                 "reports")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def update_from_config(self):
        """Update UI from configuration"""
        report_config = self.config_controller.get_report_config()
        
        # Set report format
        format_str = report_config.get("format", "html")
        index = self.format_combo.findText(format_str)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
        
        # Set include plots
        self.include_plots_check.setChecked(report_config.get("include_plots", True))
        
        # Set output directory
        self.output_dir_edit.setText(report_config.get("output_dir", "reports/output"))
    
    def update_config(self):
        """Update configuration from UI"""
        report_config = {
            "format": self.format_combo.currentText(),
            "include_plots": self.include_plots_check.isChecked(),
            "output_dir": self.output_dir_edit.text()
        }
        
        # Update configuration
        self.config_controller.set_report_config(report_config)