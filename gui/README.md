# Trading Strategy Aggregation System - GUI Application

## Overview

This directory contains the GUI application for the Trading Strategy Aggregation System. The GUI provides a user-friendly interface for configuring, running, and visualizing trading strategy analyses.

## Structure

The GUI application is organized into the following components:

- `gui_app.py`: Main entry point for the GUI application
- `gui/main_window.py`: Main window implementation
- `gui/controllers/`: Controllers for managing application logic
  - `config_controller.py`: Manages configuration loading/saving
  - `execution_controller.py`: Handles analysis execution
- `gui/components/`: UI components
  - `data_tab.py`: Data source configuration
  - `strategy_tab.py`: Strategy configuration
  - `aggregator_tab.py`: Signal aggregation settings
  - `report_tab.py`: Report generation settings
  - `results_tab.py`: Results visualization

## Usage

To run the GUI application:

```bash
python gui_app.py
```

Make sure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

## Features

- **Data Source Configuration**: Configure data sources including sample data, CSV files, Yahoo Finance, and Alpha Vantage
- **Strategy Management**: Add, edit, and remove trading strategies with custom parameters
- **Aggregation Settings**: Configure how signals from multiple strategies are combined
- **Report Settings**: Customize report generation options
- **Results Visualization**: View strategy signals and performance charts
- **Configuration Management**: Save and load configurations for reuse

## Requirements

- Python 3.6+
- PyQt5
- Other dependencies as listed in requirements.txt