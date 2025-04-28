#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Tab Component for the Trading Strategy Aggregation System GUI

This module implements the data source configuration tab of the GUI application.
"""

import os
import logging
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QComboBox, QLineEdit, QDateEdit,
                             QPushButton, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt, QDate

logger = logging.getLogger(__name__)

class DataTab(QWidget):
    """Tab for configuring data source settings"""
    
    def __init__(self, config_controller):
        super().__init__()
        self.config_controller = config_controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create data source group
        data_source_group = QGroupBox("Data Source")
        data_source_layout = QFormLayout()
        
        # Data source type
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems(["sample", "csv", "yfinance", "alpha_vantage"])
        self.source_type_combo.currentTextChanged.connect(self.on_source_type_changed)
        data_source_layout.addRow("Source Type:", self.source_type_combo)
        
        # Symbol
        self.symbol_edit = QLineEdit()
        data_source_layout.addRow("Symbol:", self.symbol_edit)
        
        # Timeframe
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1d", "1h", "4h", "1w", "1m"])
        data_source_layout.addRow("Timeframe:", self.timeframe_combo)
        
        # Date range
        date_range_layout = QHBoxLayout()
        
        # Start date
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addYears(-1))
        date_range_layout.addWidget(QLabel("Start Date:"))
        date_range_layout.addWidget(self.start_date_edit)
        
        # End date
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        date_range_layout.addWidget(QLabel("End Date:"))
        date_range_layout.addWidget(self.end_date_edit)
        
        data_source_layout.addRow("", date_range_layout)
        
        # CSV specific options
        self.csv_group = QGroupBox("CSV Options")
        self.csv_group.setVisible(False)
        csv_layout = QFormLayout(self.csv_group)
        
        # CSV file path
        csv_path_layout = QHBoxLayout()
        self.csv_path_edit = QLineEdit()
        self.csv_path_edit.setReadOnly(True)
        csv_path_layout.addWidget(self.csv_path_edit)
        
        # Browse button
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_csv_file)
        csv_path_layout.addWidget(browse_button)
        
        csv_layout.addRow("CSV File:", csv_path_layout)
        
        # Alpha Vantage specific options
        self.alpha_vantage_group = QGroupBox("Alpha Vantage Options")
        self.alpha_vantage_group.setVisible(False)
        alpha_vantage_layout = QFormLayout(self.alpha_vantage_group)
        
        # API key
        self.api_key_edit = QLineEdit()
        alpha_vantage_layout.addRow("API Key:", self.api_key_edit)
        
        # Add groups to main layout
        data_source_group.setLayout(data_source_layout)
        main_layout.addWidget(data_source_group)
        main_layout.addWidget(self.csv_group)
        main_layout.addWidget(self.alpha_vantage_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
    
    def on_source_type_changed(self, source_type):
        """Handle source type change"""
        # Show/hide source-specific options
        self.csv_group.setVisible(source_type == "csv")
        self.alpha_vantage_group.setVisible(source_type == "alpha_vantage")
    
    def browse_csv_file(self):
        """Open file dialog to select CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File",
                                                "data", "CSV Files (*.csv)")
        if file_path:
            self.csv_path_edit.setText(file_path)
    
    def update_from_config(self):
        """Update UI from configuration"""
        data_config = self.config_controller.get_data_source_config()
        
        # Set source type
        source_type = data_config.get("type", "sample")
        index = self.source_type_combo.findText(source_type)
        if index >= 0:
            self.source_type_combo.setCurrentIndex(index)
        
        # Set symbol
        self.symbol_edit.setText(data_config.get("symbol", "AAPL"))
        
        # Set timeframe
        timeframe = data_config.get("timeframe", "1d")
        index = self.timeframe_combo.findText(timeframe)
        if index >= 0:
            self.timeframe_combo.setCurrentIndex(index)
        
        # Set dates
        start_date = data_config.get("start_date")
        if start_date:
            self.start_date_edit.setDate(QDate.fromString(start_date, "yyyy-MM-dd"))
        
        end_date = data_config.get("end_date")
        if end_date:
            self.end_date_edit.setDate(QDate.fromString(end_date, "yyyy-MM-dd"))
        
        # Set CSV path
        if source_type == "csv":
            self.csv_path_edit.setText(data_config.get("path", ""))
        
        # Set Alpha Vantage API key
        if source_type == "alpha_vantage":
            self.api_key_edit.setText(data_config.get("api_key", ""))
    
    def update_config(self):
        """Update configuration from UI"""
        data_config = {}
        
        # Get source type
        data_config["type"] = self.source_type_combo.currentText()
        
        # Get symbol
        data_config["symbol"] = self.symbol_edit.text()
        
        # Get timeframe
        data_config["timeframe"] = self.timeframe_combo.currentText()
        
        # Get dates
        data_config["start_date"] = self.start_date_edit.date().toString("yyyy-MM-dd")
        data_config["end_date"] = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Get CSV path if applicable
        if data_config["type"] == "csv":
            data_config["path"] = self.csv_path_edit.text()
        
        # Get Alpha Vantage API key if applicable
        if data_config["type"] == "alpha_vantage":
            data_config["api_key"] = self.api_key_edit.text()
        
        # Update configuration
        self.config_controller.set_data_source_config(data_config)