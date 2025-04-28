#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Results Tab Component for the Trading Strategy Aggregation System GUI

This module implements the results display tab of the GUI application.
"""

import os
import logging
import webbrowser
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGroupBox, QSplitter, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

logger = logging.getLogger(__name__)

class ResultsTab(QWidget):
    """Tab for displaying analysis results"""
    
    def __init__(self, execution_controller):
        super().__init__()
        self.execution_controller = execution_controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create status label
        self.status_label = QLabel("No analysis results available. Run an analysis to see results.")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Create splitter for results
        self.results_splitter = QSplitter(Qt.Vertical)
        self.results_splitter.setVisible(False)
        
        # Create signals table group
        signals_group = QGroupBox("Strategy Signals")
        signals_layout = QVBoxLayout(signals_group)
        
        # Create signals table
        self.signals_table = QTableWidget()
        self.signals_table.setColumnCount(3)
        self.signals_table.setHorizontalHeaderLabels(["Strategy", "Signal Type", "Performance"])
        self.signals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        signals_layout.addWidget(self.signals_table)
        
        # Create plots group
        plots_group = QGroupBox("Visualization")
        plots_layout = QVBoxLayout(plots_group)
        
        # Create plots layout
        plots_container = QHBoxLayout()
        
        # Price chart
        self.price_chart_label = QLabel("Price chart not available")
        self.price_chart_label.setAlignment(Qt.AlignCenter)
        self.price_chart_label.setFrameShape(QFrame.StyledPanel)
        self.price_chart_label.setMinimumHeight(300)
        plots_container.addWidget(self.price_chart_label)
        
        # Signals chart
        self.signals_chart_label = QLabel("Signals chart not available")
        self.signals_chart_label.setAlignment(Qt.AlignCenter)
        self.signals_chart_label.setFrameShape(QFrame.StyledPanel)
        self.signals_chart_label.setMinimumHeight(300)
        plots_container.addWidget(self.signals_chart_label)
        
        plots_layout.addLayout(plots_container)
        
        # Add groups to splitter
        self.results_splitter.addWidget(signals_group)
        self.results_splitter.addWidget(plots_group)
        
        # Add splitter to main layout
        main_layout.addWidget(self.results_splitter)
        
        # Create buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        
        # Open report button
        self.open_report_button = QPushButton("Open Report")
        self.open_report_button.clicked.connect(self.open_report)
        self.open_report_button.setEnabled(False)
        buttons_layout.addWidget(self.open_report_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def update_results(self):
        """Update the results display with the latest analysis results"""
        # Get results from execution controller
        market_data = self.execution_controller.get_market_data()
        strategy_signals = self.execution_controller.get_strategy_signals()
        strategy_metadata = self.execution_controller.get_strategy_metadata()
        aggregated_signal = self.execution_controller.get_aggregated_signal()
        report_path = self.execution_controller.get_report_path()
        
        if market_data is None or not strategy_signals or aggregated_signal is None:
            self.status_label.setText("No analysis results available. Run an analysis to see results.")
            self.results_splitter.setVisible(False)
            self.open_report_button.setEnabled(False)
            return
        
        # Update status
        self.status_label.setText(f"Analysis completed with {len(market_data)} data points and {len(strategy_signals)} strategies.")
        self.results_splitter.setVisible(True)
        
        # Update signals table
        self.signals_table.setRowCount(0)
        
        for i, (signals, metadata) in enumerate(zip(strategy_signals, strategy_metadata)):
            self.signals_table.insertRow(i)
            
            # Strategy name
            name = metadata.get("name", f"Strategy {i+1}")
            name_item = QTableWidgetItem(name)
            self.signals_table.setItem(i, 0, name_item)
            
            # Signal type
            signal_type = metadata.get("signal_type", "Unknown")
            type_item = QTableWidgetItem(signal_type)
            self.signals_table.setItem(i, 1, type_item)
            
            # Performance (placeholder)
            performance = "N/A"
            if "binary_signal" in signals.columns:
                buy_signals = signals[signals["binary_signal"] == 1]
                performance = f"{len(buy_signals)} signals"
            
            perf_item = QTableWidgetItem(performance)
            self.signals_table.setItem(i, 2, perf_item)
        
        # Update plots
        self._update_plots(report_path)
        
        # Enable report button if report exists
        self.open_report_button.setEnabled(report_path is not None)
    
    def _update_plots(self, report_path):
        """Update the plot displays"""
        if not report_path:
            return
        
        # Get plot paths
        plots_dir = os.path.join(os.path.dirname(report_path), "plots")
        price_plot = None
        signals_plot = None
        
        if os.path.exists(plots_dir):
            for filename in os.listdir(plots_dir):
                if "price_signals" in filename:
                    price_plot = os.path.join(plots_dir, filename)
                elif "strategy_signals" in filename:
                    signals_plot = os.path.join(plots_dir, filename)
        
        # Update price chart
        if price_plot and os.path.exists(price_plot):
            pixmap = QPixmap(price_plot)
            if not pixmap.isNull():
                self.price_chart_label.setPixmap(pixmap.scaled(
                    self.price_chart_label.width(),
                    self.price_chart_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                self.price_chart_label.setScaledContents(True)
            else:
                self.price_chart_label.setText("Failed to load price chart")
        else:
            self.price_chart_label.setText("Price chart not available")
        
        # Update signals chart
        if signals_plot and os.path.exists(signals_plot):
            pixmap = QPixmap(signals_plot)
            if not pixmap.isNull():
                self.signals_chart_label.setPixmap(pixmap.scaled(
                    self.signals_chart_label.width(),
                    self.signals_chart_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                self.signals_chart_label.setScaledContents(True)
            else:
                self.signals_chart_label.setText("Failed to load signals chart")
        else:
            self.signals_chart_label.setText("Signals chart not available")
    
    def open_report(self):
        """Open the generated report in the default web browser"""
        report_path = self.execution_controller.get_report_path()
        if report_path and os.path.exists(report_path):
            try:
                webbrowser.open(f"file://{os.path.abspath(report_path)}")
            except Exception as e:
                logger.error(f"Error opening report: {e}")
        else:
            self.status_label.setText("Report file not found")
    
    def resizeEvent(self, event):
        """Handle resize event to update plot scaling"""
        super().resizeEvent(event)
        report_path = self.execution_controller.get_report_path()
        if report_path:
            self._update_plots(report_path)