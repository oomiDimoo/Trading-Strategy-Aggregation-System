#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Window for the Trading Strategy Aggregation System GUI

This module implements the main window of the GUI application, which serves as
the primary interface for users to interact with the trading strategy system.
"""

import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QMessageBox, QAction,
                             QFileDialog, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Import GUI components
from gui.components.data_tab import DataTab
from gui.components.strategy_tab import StrategyTab
from gui.components.aggregator_tab import AggregatorTab
from gui.components.report_tab import ReportTab
from gui.components.results_tab import ResultsTab
from gui.components.dashboard_tab import DashboardTab

# Import core functionality
from gui.controllers.config_controller import ConfigController
from gui.controllers.execution_controller import ExecutionController

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main window for the Trading Strategy Aggregation System GUI"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize controllers
        self.config_controller = ConfigController()
        self.execution_controller = ExecutionController(self.config_controller)
        
        # Set up the UI
        self.init_ui()
        
        # Load default configuration
        self.load_default_config()
        
        logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle("Trading Strategy Aggregation System")
        self.setMinimumSize(900, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.data_tab = DataTab(self.config_controller)
        self.strategy_tab = StrategyTab(self.config_controller)
        self.aggregator_tab = AggregatorTab(self.config_controller)
        self.report_tab = ReportTab(self.config_controller)
        self.results_tab = ResultsTab(self.execution_controller)
        self.dashboard_tab = DashboardTab(self.execution_controller)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.data_tab, "Data Source")
        self.tabs.addTab(self.strategy_tab, "Strategies")
        self.tabs.addTab(self.aggregator_tab, "Aggregation")
        self.tabs.addTab(self.report_tab, "Report Settings")
        self.tabs.addTab(self.results_tab, "Results")
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Add tab widget to layout
        layout.addWidget(self.tabs)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Set status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create the menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # New configuration action
        new_config_action = QAction("&New Configuration", self)
        new_config_action.setShortcut("Ctrl+N")
        new_config_action.setStatusTip("Create a new configuration")
        new_config_action.triggered.connect(self.new_config)
        file_menu.addAction(new_config_action)
        
        # Load configuration action
        load_config_action = QAction("&Load Configuration", self)
        load_config_action.setShortcut("Ctrl+O")
        load_config_action.setStatusTip("Load configuration from file")
        load_config_action.triggered.connect(self.load_config)
        file_menu.addAction(load_config_action)
        
        # Save configuration action
        save_config_action = QAction("&Save Configuration", self)
        save_config_action.setShortcut("Ctrl+S")
        save_config_action.setStatusTip("Save configuration to file")
        save_config_action.triggered.connect(self.save_config)
        file_menu.addAction(save_config_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Run menu
        run_menu = self.menuBar().addMenu("&Run")
        
        # Run analysis action
        run_action = QAction("&Run Analysis", self)
        run_action.setShortcut("F5")
        run_action.setStatusTip("Run the trading strategy analysis")
        run_action.triggered.connect(self.run_analysis)
        run_menu.addAction(run_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About the application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_config(self):
        """Create a new configuration"""
        if self.config_controller.is_dirty():
            reply = QMessageBox.question(self, "New Configuration",
                                        "You have unsaved changes. Are you sure you want to create a new configuration? "
                                        "All unsaved changes will be lost.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        self.load_default_config()
        self.statusBar().showMessage("New configuration created")
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_controller.is_dirty():
            reply = QMessageBox.question(self, "Load Configuration",
                                        "You have unsaved changes. Are you sure you want to load a new configuration? "
                                        "All unsaved changes will be lost.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        file_path, _ = QFileDialog.getOpenFileName(self, "Load Configuration",
                                                "config", "JSON Files (*.json)")
        
        if file_path:
            success = self.config_controller.load_config(file_path)
            if success:
                self.update_ui_from_config()
                self.statusBar().showMessage(f"Configuration loaded from {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load configuration")
    
    def save_config(self):
        """Save configuration to file"""
        # Update configuration from UI before saving
        self.data_tab.update_config()
        self.strategy_tab.update_config()
        self.aggregator_tab.update_config()
        self.report_tab.update_config()

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration",
                                                "config/config.json", "JSON Files (*.json)")
        
        if file_path:
            success = self.config_controller.save_config(file_path)
            if success:
                self.statusBar().showMessage(f"Configuration saved to {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to save configuration")
    
    def load_default_config(self):
        """Load default configuration"""
        self.config_controller.create_default_config()
        self.update_ui_from_config()
        self.statusBar().showMessage("Default configuration loaded")
    
    def update_ui_from_config(self):
        """Update UI components from the current configuration"""
        self.data_tab.update_from_config()
        self.strategy_tab.update_from_config()
        self.aggregator_tab.update_from_config()
        self.report_tab.update_from_config()
    
    def run_analysis(self):
        """Run the trading strategy analysis"""
        self.statusBar().showMessage("Running analysis...")
        
        # Update configuration from UI
        self.data_tab.update_config()
        self.strategy_tab.update_config()
        self.aggregator_tab.update_config()
        self.report_tab.update_config()
        
        # Run the analysis
        success, message = self.execution_controller.run_analysis()
        
        if success:
            self.statusBar().showMessage("Analysis completed successfully")
            self.tabs.setCurrentWidget(self.results_tab)
            self.results_tab.update_results()
        else:
            self.statusBar().showMessage("Analysis failed")
            QMessageBox.warning(self, "Error", f"Analysis failed: {message}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
                         "<h3>Trading Strategy Aggregation System</h3>"
                         "<p>A system for aggregating signals from multiple "
                         "trading strategies and generating unified reports.</p>"
                         "<p>Version 1.0</p>")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.config_controller.is_dirty():
            reply = QMessageBox.question(self, "Exit",
                                        "You have unsaved changes. Are you sure you want to exit?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
                logger.info("Application closed")
            else:
                event.ignore()
        else:
            event.accept()
            logger.info("Application closed")