#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import os
from typing import Dict, Any, List, Union, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates reports and visualizations for trading strategies and aggregated signals.
    
    This class handles creating performance reports, signal visualizations,
    and exporting results to various formats.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the report generator.
        
        Args:
            config: Configuration dictionary for the report generator
        """
        self.config = config or {}
        self.output_dir = self.config.get("output_dir", "reports/output")
        self.report_format = self.config.get("format", "html")
        self.include_plots = self.config.get("include_plots", True)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_report(self, 
                       market_data: pd.DataFrame, 
                       strategy_signals: List[pd.DataFrame], 
                       aggregated_signal: pd.DataFrame,
                       strategy_metadata: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive report of strategy performance and signals.
        
        Args:
            market_data: Original market data
            strategy_signals: List of signal DataFrames from individual strategies
            aggregated_signal: DataFrame with aggregated signals
            strategy_metadata: List of metadata dictionaries from strategies
            
        Returns:
            Path to the generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"trading_report_{timestamp}"
        
        if self.include_plots:
            # Generate plots
            plot_paths = self._generate_plots(market_data, strategy_signals, aggregated_signal, report_filename)
        
        # Generate report based on format
        if self.report_format.lower() == "html":
            report_path = self._generate_html_report(market_data, strategy_signals, 
                                                   aggregated_signal, strategy_metadata, 
                                                   report_filename)
        elif self.report_format.lower() == "csv":
            report_path = self._generate_csv_report(market_data, strategy_signals, 
                                                  aggregated_signal, strategy_metadata, 
                                                  report_filename)
        else:
            logger.warning(f"Unsupported report format: {self.report_format}, using HTML")
            report_path = self._generate_html_report(market_data, strategy_signals, 
                                                   aggregated_signal, strategy_metadata, 
                                                   report_filename)
        
        logger.info(f"Generated report: {report_path}")
        return report_path
    
    def _generate_plots(self, 
                        market_data: pd.DataFrame, 
                        strategy_signals: List[pd.DataFrame], 
                        aggregated_signal: pd.DataFrame,
                        base_filename: str) -> List[str]:
        """
        Generate visualization plots for the report.
        
        Args:
            market_data: Original market data
            strategy_signals: List of signal DataFrames from individual strategies
            aggregated_signal: DataFrame with aggregated signals
            base_filename: Base filename for the plots
            
        Returns:
            List of paths to the generated plot files
        """
        plot_paths = []
        
        # Create plots directory
        plots_dir = os.path.join(self.output_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        
        # 1. Price chart with aggregated signals
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(market_data.index, market_data['close'], label='Close Price')
            
            # Plot buy signals
            if 'binary_signal' in aggregated_signal.columns:
                buy_signals = aggregated_signal[aggregated_signal['binary_signal'] == 1]
                plt.scatter(buy_signals.index, market_data.loc[buy_signals.index, 'close'], 
                           marker='^', color='green', s=100, label='Buy Signal')
                
                # Plot sell signals
                sell_signals = aggregated_signal[aggregated_signal['binary_signal'] == 0]
                sell_signals = sell_signals[sell_signals.index.isin(buy_signals.index.shift(1))]
                plt.scatter(sell_signals.index, market_data.loc[sell_signals.index, 'close'], 
                           marker='v', color='red', s=100, label='Sell Signal')
            
            plt.title('Price Chart with Aggregated Signals')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.legend()
            plt.grid(True)
            
            # Save plot
            price_plot_path = os.path.join(plots_dir, f"{base_filename}_price_signals.png")
            plt.savefig(price_plot_path)
            plt.close()
            plot_paths.append(price_plot_path)
            
        except Exception as e:
            logger.error(f"Error generating price chart: {e}")
        
        # 2. Strategy signals comparison
        try:
            plt.figure(figsize=(12, 6))
            
            # Plot each strategy's signal
            for i, signals in enumerate(strategy_signals):
                if 'signal' in signals.columns:
                    strategy_name = signals['strategy'].iloc[0] if 'strategy' in signals.columns else f"Strategy {i+1}"
                    plt.plot(signals.index, signals['signal'], label=strategy_name)
            
            # Plot aggregated signal
            if 'signal' in aggregated_signal.columns:
                plt.plot(aggregated_signal.index, aggregated_signal['signal'], 
                         label='Aggregated Signal', linewidth=2, color='black')
            
            plt.title('Strategy Signals Comparison')
            plt.xlabel('Date')
            plt.ylabel('Signal Value')
            plt.legend()
            plt.grid(True)
            
            # Save plot
            signals_plot_path = os.path.join(plots_dir, f"{base_filename}_strategy_signals.png")
            plt.savefig(signals_plot_path)
            plt.close()
            plot_paths.append(signals_plot_path)
            
        except Exception as e:
            logger.error(f"Error generating strategy signals comparison: {e}")
        
        return plot_paths
    
    def _generate_html_report(self, 
                             market_data: pd.DataFrame, 
                             strategy_signals: List[pd.DataFrame], 
                             aggregated_signal: pd.DataFrame,
                             strategy_metadata: List[Dict[str, Any]],
                             base_filename: str) -> str:
        """
        Generate an HTML report.
        
        Args:
            market_data: Original market data
            strategy_signals: List of signal DataFrames from individual strategies
            aggregated_signal: DataFrame with aggregated signals
            strategy_metadata: List of metadata dictionaries from strategies
            base_filename: Base filename for the report
            
        Returns:
            Path to the generated HTML report
        """
        try:
            # Create HTML content
            html_content = []
            html_content.append("<!DOCTYPE html>")
            html_content.append("<html>")
            html_content.append("<head>")
            html_content.append("<title>Trading Strategy Report</title>")
            html_content.append("<style>")
            html_content.append("body { font-family: Arial, sans-serif; margin: 20px; }")
            html_content.append("table { border-collapse: collapse; width: 100%; }")
            html_content.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
            html_content.append("th { background-color: #f2f2f2; }")
            html_content.append("tr:nth-child(even) { background-color: #f9f9f9; }")
            html_content.append("h1, h2, h3 { color: #333; }")
            html_content.append("</style>")
            html_content.append("</head>")
            html_content.append("<body>")
            
            # Report header
            html_content.append(f"<h1>Trading Strategy Report</h1>")
            html_content.append(f"<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
            
            # Market data summary
            html_content.append("<h2>Market Data Summary</h2>")
            html_content.append("<table>")
            html_content.append("<tr><th>Metric</th><th>Value</th></tr>")
            html_content.append(f"<tr><td>Symbol</td><td>{market_data.index.name or 'Unknown'}</td></tr>")
            html_content.append(f"<tr><td>Start Date</td><td>{market_data.index.min().strftime('%Y-%m-%d')}</td></tr>")
            html_content.append(f"<tr><td>End Date</td><td>{market_data.index.max().strftime('%Y-%m-%d')}</td></tr>")
            html_content.append(f"<tr><td>Number of Days</td><td>{len(market_data)}</td></tr>")
            html_content.append(f"<tr><td>Starting Price</td><td>{market_data['close'].iloc[0]:.2f}</td></tr>")
            html_content.append(f"<tr><td>Ending Price</td><td>{market_data['close'].iloc[-1]:.2f}</td></tr>")
            html_content.append(f"<tr><td>Return</td><td>{(market_data['close'].iloc[-1] / market_data['close'].iloc[0] - 1) * 100:.2f}%</td></tr>")
            html_content.append("</table>")
            
            # Strategy summary
            html_content.append("<h2>Strategy Summary</h2>")
            html_content.append("<table>")
            html_content.append("<tr><th>Strategy</th><th>Type</th><th>Weight</th><th>Parameters</th><th>Trades</th></tr>")
            
            for metadata in strategy_metadata:
                strategy_name = metadata.get("strategy_name", "Unknown")
                strategy_type = next((s['signal_type'] for s in strategy_signals if s.get('strategy', None) == strategy_name), "Unknown")
                weight = metadata.get("weight", 1.0)
                num_trades = metadata.get("num_trades", 0)
                
                # Format parameters
                params = ", ".join([f"{k}: {v}" for k, v in metadata.items() 
                                  if k not in ["strategy_name", "weight", "num_trades"]])
                
                html_content.append(f"<tr><td>{strategy_name}</td><td>{strategy_type}</td><td>{weight:.2f}</td><td>{params}</td><td>{num_trades}</td></tr>")
            
            html_content.append("</table>")
            
            # Aggregated signal summary
            if not aggregated_signal.empty:
                html_content.append("<h2>Aggregated Signal Summary</h2>")
                html_content.append("<table>")
                html_content.append("<tr><th>Metric</th><th>Value</th></tr>")
                
                buy_signals = aggregated_signal[aggregated_signal['binary_signal'] == 1]
                sell_signals = aggregated_signal[aggregated_signal['binary_signal'] == 0]
                
                html_content.append(f"<tr><td>Total Buy Signals</td><td>{len(buy_signals)}</td></tr>")
                html_content.append(f"<tr><td>Total Sell Signals</td><td>{len(sell_signals)}</td></tr>")
                html_content.append(f"<tr><td>Average Signal Strength</td><td>{aggregated_signal['signal'].mean():.4f}</td></tr>")
                html_content.append("</table>")
            
            # Include plots if available
            plots_dir = os.path.join(self.output_dir, "plots")
            price_plot_path = os.path.join(plots_dir, f"{base_filename}_price_signals.png")
            signals_plot_path = os.path.join(plots_dir, f"{base_filename}_strategy_signals.png")
            
            if os.path.exists(price_plot_path):
                html_content.append("<h2>Price Chart with Signals</h2>")
                html_content.append(f"<img src='plots/{os.path.basename(price_plot_path)}' alt='Price Chart' style='max-width:100%;'>")
            
            if os.path.exists(signals_plot_path):
                html_content.append("<h2>Strategy Signals Comparison</h2>")
                html_content.append(f"<img src='plots/{os.path.basename(signals_plot_path)}' alt='Strategy Signals' style='max-width:100%;'>")
            
            # Close HTML
            html_content.append("</body>")
            html_content.append("</html>")
            
            # Write HTML to file
            report_path = os.path.join(self.output_dir, f"{base_filename}.html")
            with open(report_path, 'w') as f:
                f.write("\n".join(html_content))
            
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return ""
    
    def _generate_csv_report(self, 
                            market_data: pd.DataFrame, 
                            strategy_signals: List[pd.DataFrame], 
                            aggregated_signal: pd.DataFrame,
                            strategy_metadata: List[Dict[str, Any]],
                            base_filename: str) -> str:
        """
        Generate CSV reports for the data and signals.
        
        Args:
            market_data: Original market data
            strategy_signals: List of signal DataFrames from individual strategies
            aggregated_signal: DataFrame with aggregated signals
            strategy_metadata: List of metadata dictionaries from strategies
            base_filename: Base filename for the report
            
        Returns:
            Path to the main CSV report file
        """
        try:
            # Create a combined DataFrame with market data and signals
            combined_data = market_data.copy()
            
            # Add individual strategy signals
            for i, signals in enumerate(strategy_signals):
                strategy_name = signals['strategy'].iloc[0] if 'strategy' in signals.columns else f"Strategy_{i+1}"
                if 'signal' in signals.columns:
                    combined_data[f"{strategy_name}_signal"] = signals['signal']
                if 'binary_signal' in signals.columns:
                    combined_data[f"{strategy_name}_binary"] = signals['binary_signal']
            
            # Add aggregated signals
            if not aggregated_signal.empty:
                if 'signal' in aggregated_signal.columns:
                    combined_data['aggregated_signal'] = aggregated_signal['signal']
                if 'binary_signal' in aggregated_signal.columns:
                    combined_data['aggregated_binary'] = aggregated_signal['binary_signal']
            
            # Save to CSV
            csv_path = os.path.join(self.output_dir, f"{base_filename}.csv")
            combined_data.to_csv(csv_path)
            
            # Also save strategy metadata
            metadata_df = pd.DataFrame(strategy_metadata)
            metadata_csv_path = os.path.join(self.output_dir, f"{base_filename}_metadata.csv")
            metadata_df.to_csv(metadata_csv_path, index=False)
            
            return csv_path
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            return ""