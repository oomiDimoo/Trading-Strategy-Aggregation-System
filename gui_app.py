#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trading Strategy Aggregation System - GUI Application

This is the main entry point for the GUI application that provides a user-friendly
interface to the trading strategy aggregation system.
"""

import sys
import os
import logging
from datetime import datetime

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/gui_app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from PyQt5.QtWidgets import QApplication
    from gui.main_window import MainWindow
except ImportError:
    logger.error("PyQt5 is not installed. Please install it with: pip install PyQt5")
    print("Error: PyQt5 is not installed. Please install it with: pip install PyQt5")
    sys.exit(1)


def main():
    """Main entry point for the GUI application"""
    try:
        # Create the application
        app = QApplication(sys.argv)
        app.setApplicationName("Trading Strategy Aggregation System")
        
        # Create and show the main window
        main_window = MainWindow()
        main_window.show()
        
        # Start the event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"An error occurred in the GUI application: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()