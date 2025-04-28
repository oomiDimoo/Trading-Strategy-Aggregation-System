![Image Description](image.png)

# Trading Strategy Aggregation System

A Python-based system for aggregating signals from multiple trading strategies to generate unified trading decisions.

## Overview

This system allows you to combine signals from different technical analysis strategies with customizable weights to create a more robust trading approach. It includes data loading from various sources, strategy implementation, signal aggregation, and comprehensive reporting.

## Features

- **Data Loading**: Load market data from CSV files, Yahoo Finance, Alpha Vantage, or generate sample data
- **Multiple Strategies**: Includes implementations for:
  - Moving Average Crossover
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
- **Signal Aggregation**: Combine signals using weighted average, majority vote, or consensus methods
- **Reporting**: Generate HTML or CSV reports with performance metrics and visualizations

## Project Structure

```
├── aggregator/
│   └── signal_aggregator.py    # Signal aggregation logic
├── data/
│   └── data_loader.py          # Data loading from various sources
├── reports/
│   └── report_generator.py     # Report generation and visualization
├── strategies/
│   ├── strategy_interface.py   # Strategy base class
│   ├── strategy_factory.py     # Factory for creating strategies
│   ├── moving_average_crossover.py
│   ├── rsi_strategy.py
│   └── macd_strategy.py
├── config/
│   └── config.json             # Configuration file (created on first run)
├── logs/                       # Log files directory
├── main.py                     # Main application entry point
└── requirements.txt            # Project dependencies
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the application with default settings:

```bash
python main.py
```

This will:
1. Load sample market data
2. Process it with the default strategies
3. Aggregate the signals
4. Generate an HTML report with visualizations

### Configuration

On first run, a default configuration file will be created at `config/config.json`. You can modify this file to:

- Change data sources
- Adjust strategy parameters
- Modify aggregation methods
- Configure report formats

To save the default configuration explicitly:

```bash
python main.py --save-config
```

To use a custom configuration file:

```bash
python main.py --config path/to/your/config.json
```

## Adding New Strategies

To add a new strategy:

1. Create a new Python file in the `strategies/` directory
2. Implement a class that inherits from `Strategy` base class
3. Register the strategy in `main.py` or `gui_app.py`
4. Add the strategy to your configuration
