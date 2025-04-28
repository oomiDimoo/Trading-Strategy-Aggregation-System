#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dashboard Tab Component for the Trading Strategy Aggregation System GUI

This module implements a modern dashboard for visualizing trading strategy performance.
It provides an interactive, Power BI-like interface with advanced visualization capabilities.
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QGridLayout, QFrame,
                             QSplitter, QScrollArea, QSizePolicy, QTabWidget,
                             QLineEdit, QDateEdit, QCheckBox, QToolButton,
                             QMenu, QAction, QTableWidget, QTableWidgetItem,
                             QHeaderView, QProgressBar, QGroupBox, QRadioButton)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QDate
from PyQt5.QtGui import QColor, QPalette, QIcon, QFont, QPixmap

# For matplotlib integration
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

logger = logging.getLogger(__name__)


class MplCanvas(FigureCanvas):
    """Matplotlib canvas for interactive charts"""
    
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor('#FFFFFF')
        super().__init__(self.fig)
        self.setMinimumSize(QSize(250, 200))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable mouse wheel zooming
        self.mpl_connect('scroll_event', self.zoom_factory)
        self.zoom_scale = 1.1
    
    def zoom_factory(self, event):
        """Handle mouse wheel zoom events"""
        ax = self.figure.axes[0]
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return
            
        if event.button == 'up':
            scale_factor = 1/self.zoom_scale
        elif event.button == 'down':
            scale_factor = self.zoom_scale
        else:
            scale_factor = 1
            
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        
        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])
        
        ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * relx])
        ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * rely])
        self.draw()


class MetricCard(QFrame):
    """Card widget for displaying a performance metric with trend indicator"""
    
    def __init__(self, title, value, unit="", color="#18BC9C", trend=None, trend_value=None):
        super().__init__()
        self.setObjectName("metric-card")
        self.setStyleSheet(
            f"#metric-card {{ "
            f"background-color: #FFFFFF; "
            f"border-radius: 10px; "
            f"border-left: 5px solid {color}; "
            f"padding: 12px; "
            f"border: 1px solid #E0E0E0; "
            f"box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.1); "
            f"transition: all 0.3s ease; "
            f"}} "
            f"#metric-card:hover {{ "
            f"transform: translateY(-3px); "
            f"box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.15); "
            f"}}"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(130)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        
        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #7F8C8D; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Value layout
        value_layout = QHBoxLayout()
        
        # Value label - store as instance attribute so it can be updated
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"font-size: 28px; color: #2C3E50; font-weight: bold;")
        value_layout.addWidget(self.value_label)
        
        # Unit label
        if unit:
            self.unit_label = QLabel(unit)
            self.unit_label.setStyleSheet("font-size: 16px; color: #7F8C8D;")
            value_layout.addWidget(self.unit_label)
            
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Add trend indicator if provided
        self.trend_label = None
        if trend is not None and trend_value is not None:
            trend_layout = QHBoxLayout()
            
            # Trend arrow and color
            if trend == 'up':
                trend_color = '#18BC9C'  # Green for positive
                trend_arrow = '▲'
            elif trend == 'down':
                trend_color = '#E74C3C'  # Red for negative
                trend_arrow = '▼'
            else:
                trend_color = '#7F8C8D'  # Gray for neutral
                trend_arrow = '►'
            
            trend_text = f"{trend_arrow} {trend_value}%"
            self.trend_label = QLabel(trend_text)
            self.trend_label.setStyleSheet(f"font-size: 14px; color: {trend_color}; font-weight: bold;")
            trend_layout.addWidget(self.trend_label)
            
            # Period label
            period_label = QLabel("vs previous period")
            period_label.setStyleSheet("font-size: 12px; color: #95A5A6;")
            trend_layout.addWidget(period_label)
            
            trend_layout.addStretch()
            layout.addLayout(trend_layout)
        else:
            # Create an empty trend label that can be populated later
            trend_layout = QHBoxLayout()
            self.trend_label = QLabel("")
            trend_layout.addWidget(self.trend_label)
            trend_layout.addStretch()
            layout.addLayout(trend_layout)


class ChartPanel(QFrame):
    """Enhanced panel for displaying a chart with title and interactive controls"""
    
    # Signal emitted when period changes
    periodChanged = pyqtSignal(str)
    
    def __init__(self, title, chart_type="line"):
        super().__init__()
        self.setObjectName("chart-panel")
        self.setStyleSheet(
            "#chart-panel { "
            "background-color: #FFFFFF; "
            "border-radius: 10px; "
            "border: 1px solid #E0E0E0; "
            "box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.1); "
            "} "
            "QComboBox { "
            "border: 1px solid #D0D0D0; "
            "border-radius: 4px; "
            "padding: 4px; "
            "background-color: #F8F9FA; "
            "} "
            "QComboBox::drop-down { "
            "border: none; "
            "width: 20px; "
            "} "
            "QToolButton { "
            "border: 1px solid #D0D0D0; "
            "border-radius: 4px; "
            "background-color: #F8F9FA; "
            "padding: 4px; "
            "} "
            "QToolButton:hover { "
            "background-color: #E0E0E0; "
            "}"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chart_type = chart_type
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        
        # Header layout
        header_layout = QHBoxLayout()
        
        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; color: #2C3E50; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Chart type selector
        if chart_type in ["line", "bar", "both"]:
            self.chart_type_combo = QComboBox()
            self.chart_type_combo.addItems(["Line", "Bar", "Candlestick"])
            self.chart_type_combo.setFixedWidth(100)
            self.chart_type_combo.setStyleSheet("margin-right: 10px;")
            self.chart_type_combo.currentTextChanged.connect(self.on_chart_type_changed)
            header_layout.addWidget(self.chart_type_combo)
        
        # Period selector
        self.period_combo = QComboBox()
        self.period_combo.addItems(["1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "All", "Custom"])
        self.period_combo.setCurrentText("1 Month")
        self.period_combo.setFixedWidth(120)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header_layout.addWidget(self.period_combo)
        
        # Options button with menu
        options_button = QToolButton()
        options_button.setText("⋮")
        options_button.setPopupMode(QToolButton.InstantPopup)
        options_menu = QMenu()
        
        # Add menu actions
        export_action = QAction("Export Chart", self)
        export_action.triggered.connect(self.export_chart)
        options_menu.addAction(export_action)
        
        toggle_legend_action = QAction("Toggle Legend", self)
        toggle_legend_action.triggered.connect(self.toggle_legend)
        options_menu.addAction(toggle_legend_action)
        
        options_button.setMenu(options_menu)
        header_layout.addWidget(options_button)
        
        layout.addLayout(header_layout)
        
        # Custom date range (initially hidden)
        self.date_range_widget = QWidget()
        date_range_layout = QHBoxLayout(self.date_range_widget)
        date_range_layout.setContentsMargins(0, 0, 0, 10)
        
        date_range_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_range_layout.addWidget(self.start_date)
        
        date_range_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.end_date)
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_custom_date_range)
        date_range_layout.addWidget(apply_button)
        
        date_range_layout.addStretch()
        self.date_range_widget.setVisible(False)
        layout.addWidget(self.date_range_widget)
        
        # Chart canvas
        self.canvas = MplCanvas()
        layout.addWidget(self.canvas)
        
        # Add toolbar with custom styling
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: #F8F9FA; border-top: 1px solid #E0E0E0;")
        layout.addWidget(self.toolbar)
        
        # Legend visibility flag
        self.legend_visible = True
    
    def on_chart_type_changed(self, chart_type):
        """Handle chart type change"""
        logger.info(f"Chart type changed to {chart_type}")
        # This would be implemented to redraw the chart with the new type
        # For now, we'll just log it
    
    def on_period_changed(self, period):
        """Handle period change"""
        logger.info(f"Period changed to {period}")
        
        # Show/hide custom date range widget
        self.date_range_widget.setVisible(period == "Custom")
        
        # Emit signal for parent to handle
        self.periodChanged.emit(period)
    
    def apply_custom_date_range(self):
        """Apply custom date range"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        logger.info(f"Custom date range applied: {start_date} to {end_date}")
        # This would be implemented to update the chart with the custom date range
    
    def export_chart(self):
        """Export chart as image"""
        logger.info("Exporting chart")
        # This would be implemented to save the chart as an image file
    
    def toggle_legend(self):
        """Toggle legend visibility"""
        self.legend_visible = not self.legend_visible
        for ax in self.canvas.figure.get_axes():
            if ax.get_legend() is not None:
                ax.get_legend().set_visible(self.legend_visible)
        self.canvas.draw()


class DashboardTab(QWidget):
    """Tab for displaying a performance dashboard"""
    
    def __init__(self, execution_controller):
        super().__init__()
        self.execution_controller = execution_controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Set stylesheet for the entire tab
        self.setStyleSheet(
            "QLabel.heading { font-size: 24px; font-weight: bold; color: #2C3E50; margin-bottom: 10px; } "
            "QLabel.subheading { font-size: 18px; font-weight: bold; color: #34495E; margin-top: 15px; margin-bottom: 10px; } "
            "QPushButton.action { background-color: #3498DB; color: white; border-radius: 4px; padding: 8px 16px; font-weight: bold; } "
            "QPushButton.action:hover { background-color: #2980B9; } "
            "QScrollArea { border: none; background-color: #F5F5F5; } "
        )
        
        # Create scroll area for dashboard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create dashboard widget
        dashboard_widget = QWidget()
        dashboard_widget.setStyleSheet("background-color: #F5F5F5;")
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        dashboard_layout.setSpacing(20)
        
        # Add dashboard title
        title_label = QLabel("Strategy Performance Dashboard")
        title_label.setProperty("class", "heading")
        dashboard_layout.addWidget(title_label)
        
        # Create metrics section
        metrics_label = QLabel("Key Performance Metrics")
        metrics_label.setProperty("class", "subheading")
        dashboard_layout.addWidget(metrics_label)
        
        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)
        
        # Sample metrics (these would be populated with real data)
        metrics_grid.addWidget(MetricCard("Total Return", "24.5", "%", "#18BC9C"), 0, 0)
        metrics_grid.addWidget(MetricCard("Sharpe Ratio", "1.8", "", "#3498DB"), 0, 1)
        metrics_grid.addWidget(MetricCard("Max Drawdown", "12.3", "%", "#E74C3C"), 0, 2)
        metrics_grid.addWidget(MetricCard("Win Rate", "68", "%", "#F39C12"), 0, 3)
        
        dashboard_layout.addLayout(metrics_grid)
        
        # Create charts section
        charts_label = QLabel("Performance Charts")
        charts_label.setProperty("class", "subheading")
        dashboard_layout.addWidget(charts_label)
        
        # Charts splitter (allows resizing)
        charts_splitter = QSplitter(Qt.Vertical)
        charts_splitter.setChildrenCollapsible(False)
        
        # Top charts row
        top_charts = QSplitter(Qt.Horizontal)
        top_charts.setChildrenCollapsible(False)
        
        # Returns chart
        returns_chart = ChartPanel("Cumulative Returns")
        self.setup_returns_chart(returns_chart.canvas)
        top_charts.addWidget(returns_chart)
        
        # Strategy comparison chart
        comparison_chart = ChartPanel("Strategy Comparison")
        self.setup_comparison_chart(comparison_chart.canvas)
        top_charts.addWidget(comparison_chart)
        
        charts_splitter.addWidget(top_charts)
        
        # Bottom charts row
        bottom_charts = QSplitter(Qt.Horizontal)
        bottom_charts.setChildrenCollapsible(False)
        
        # Drawdown chart
        drawdown_chart = ChartPanel("Drawdown Analysis")
        self.setup_drawdown_chart(drawdown_chart.canvas)
        bottom_charts.addWidget(drawdown_chart)
        
        # Trade distribution chart
        trade_chart = ChartPanel("Trade Distribution")
        self.setup_trade_chart(trade_chart.canvas)
        bottom_charts.addWidget(trade_chart)
        
        charts_splitter.addWidget(bottom_charts)
        dashboard_layout.addWidget(charts_splitter)
        
        # Set equal sizes for splitters
        top_charts.setSizes([500, 500])
        bottom_charts.setSizes([500, 500])
        charts_splitter.setSizes([400, 400])
        
        # Add dashboard widget to scroll area
        scroll_area.setWidget(dashboard_widget)
        main_layout.addWidget(scroll_area)
        
        # Add refresh button
        refresh_button = QPushButton("Refresh Dashboard")
        refresh_button.setProperty("class", "action")
        refresh_button.clicked.connect(self.refresh_dashboard)
        main_layout.addWidget(refresh_button, alignment=Qt.AlignRight)
    
    def setup_returns_chart(self, canvas):
        """Set up the cumulative returns chart"""
        # Get data from execution controller
        results = self.execution_controller.get_results()
        if not results or 'signals' not in results:
            # Use sample data if no real data is available
            ax = canvas.fig.add_subplot(111)
            dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
            returns = np.cumsum(np.random.normal(0.001, 0.02, 100))
            
            ax.plot(dates, returns, 'b-', linewidth=2)
            ax.set_ylabel('Cumulative Returns (%)')
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        else:
            # Use real data
            signals_df = results['signals']
            market_data = self.execution_controller.get_market_data()
            
            if not market_data.empty and not signals_df.empty:
                ax = canvas.fig.add_subplot(111)
                
                # Plot price data on primary y-axis
                ax1 = ax
                ax1.plot(market_data.index, market_data['close'], 'k-', linewidth=1.5, label='Price')
                ax1.set_ylabel('Price', color='black')
                ax1.tick_params(axis='y', labelcolor='black')
                
                # Create secondary y-axis for returns
                ax2 = ax1.twinx()
                
                # Calculate returns for each strategy
                strategy_returns = {}
                colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']
                
                # Calculate basic returns if available in market data
                if 'returns' in market_data.columns:
                    cumulative_returns = (1 + market_data['returns']).cumprod() - 1
                    ax2.plot(market_data.index, cumulative_returns * 100, 'b-', 
                             linewidth=2, label='Market Returns', color='#3498DB')
                
                # Calculate strategy returns based on signals
                for i, column in enumerate(signals_df.columns):
                    if i < len(colors):
                        color = colors[i]
                    else:
                        color = colors[i % len(colors)]
                    
                    # Simple return calculation based on signals
                    strategy_returns = pd.Series(index=market_data.index)
                    returns = pd.Series(0.0, index=market_data.index)
                    
                    # Use signals to determine position
                    signals = signals_df[column].fillna(0)
                    position = signals.shift(1).fillna(0)
                    
                    # Calculate returns based on position and market returns
                    if 'returns' in market_data.columns:
                        strategy_return = position * market_data['returns']
                        cumulative_return = (1 + strategy_return).cumprod() - 1
                        ax2.plot(market_data.index, cumulative_return * 100, 
                                linewidth=2, label=f'{column} Returns', color=color)
                
                ax2.set_ylabel('Returns (%)', color='#3498DB')
                ax2.tick_params(axis='y', labelcolor='#3498DB')
                ax2.grid(False)
                
                # Format x-axis dates
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
                
                # Combine legends from both axes
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')
                
                ax1.grid(True, linestyle='--', alpha=0.7)
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
        
        canvas.fig.tight_layout()
        canvas.draw()
    
    def setup_comparison_chart(self, canvas):
        """Set up the strategy comparison chart"""
        # Get data from execution controller
        results = self.execution_controller.get_results()
        if not results or 'signals' not in results:
            # Use sample data if no real data is available
            ax = canvas.fig.add_subplot(111)
            
            # Sample data
            strategies = ['MACD', 'RSI', 'MA Cross', 'Combined']
            returns = [15.2, 12.8, 18.5, 24.5]
            colors = ['#3498DB', '#E74C3C', '#F39C12', '#18BC9C']
            
            bars = ax.bar(strategies, returns, color=colors, alpha=0.8)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height}%', ha='center', va='bottom')
        else:
            # Use real data
            signals_df = results['signals']
            market_data = self.execution_controller.get_market_data()
            
            if not market_data.empty and not signals_df.empty:
                ax = canvas.fig.add_subplot(111)
                
                # Calculate returns for each strategy
                strategy_returns = {}
                colors = ['#3498DB', '#E74C3C', '#F39C12', '#18BC9C', '#9B59B6', '#2ECC71']
                
                # Calculate returns based on signals
                for i, column in enumerate(signals_df.columns):
                    # Use signals to determine position
                    signals = signals_df[column].fillna(0)
                    position = signals.shift(1).fillna(0)
                    
                    # Calculate returns based on position and market returns
                    if 'returns' in market_data.columns:
                        strategy_return = position * market_data['returns']
                        total_return = ((1 + strategy_return).cumprod().iloc[-1] - 1) * 100
                        strategy_returns[column] = total_return
                
                # If we have strategy returns, plot them
                if strategy_returns:
                    strategies = list(strategy_returns.keys())
                    returns = list(strategy_returns.values())
                    
                    # Use only available colors
                    plot_colors = colors[:len(strategies)]
                    if len(plot_colors) < len(strategies):
                        # Repeat colors if needed
                        plot_colors = plot_colors * (len(strategies) // len(colors) + 1)
                        plot_colors = plot_colors[:len(strategies)]
                    
                    bars = ax.bar(strategies, returns, color=plot_colors, alpha=0.8)
                    
                    # Add value labels on top of bars
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                f'{height:.1f}%', ha='center', va='bottom')
                else:
                    # No strategy returns available, use sample data
                    strategies = ['No Strategy Data Available']
                    returns = [0]
                    bars = ax.bar(strategies, returns, color='#95A5A6', alpha=0.8)
        
        ax.set_ylabel('Total Return (%)')
        ax.set_title('Strategy Performance Comparison')
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Rotate x-axis labels if there are many strategies
        if len(ax.get_xticklabels()) > 3:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        canvas.fig.tight_layout()
        canvas.draw()
    
    def setup_drawdown_chart(self, canvas):
        """Set up the drawdown analysis chart"""
        # Get data from execution controller
        results = self.execution_controller.get_results()
        if not results or 'signals' not in results:
            # Use sample data if no real data is available
            ax = canvas.fig.add_subplot(111)
            
            # Sample data
            dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
            cumulative = np.cumsum(np.random.normal(0.001, 0.02, 100))
            peak = np.maximum.accumulate(cumulative)
            drawdown = 100 * (cumulative - peak) / peak
            
            ax.fill_between(dates, drawdown, 0, color='#E74C3C', alpha=0.3)
            ax.plot(dates, drawdown, 'r-', linewidth=1)
        else:
            # Use real data
            signals_df = results['signals']
            market_data = self.execution_controller.get_market_data()
            
            if not market_data.empty and not signals_df.empty and 'returns' in market_data.columns:
                ax = canvas.fig.add_subplot(111)
                
                # Calculate market drawdown
                market_cumulative = (1 + market_data['returns']).cumprod()
                market_peak = np.maximum.accumulate(market_cumulative)
                market_drawdown = 100 * (market_cumulative - market_peak) / market_peak
                
                # Plot market drawdown
                ax.fill_between(market_data.index, market_drawdown, 0, color='#E74C3C', alpha=0.3)
                ax.plot(market_data.index, market_drawdown, 'r-', linewidth=1, label='Market Drawdown')
                
                # Calculate and plot strategy drawdowns
                colors = ['#3498DB', '#2ECC71', '#F39C12', '#9B59B6']
                for i, column in enumerate(signals_df.columns[:3]):  # Limit to first 3 strategies to avoid clutter
                    # Use signals to determine position
                    signals = signals_df[column].fillna(0)
                    position = signals.shift(1).fillna(0)
                    
                    # Calculate returns based on position and market returns
                    strategy_return = position * market_data['returns']
                    strategy_cumulative = (1 + strategy_return).cumprod()
                    strategy_peak = np.maximum.accumulate(strategy_cumulative)
                    strategy_drawdown = 100 * (strategy_cumulative - strategy_peak) / strategy_peak
                    
                    # Plot strategy drawdown
                    color = colors[i % len(colors)]
                    ax.plot(market_data.index, strategy_drawdown, linewidth=1, 
                            label=f'{column} Drawdown', color=color, alpha=0.7)
                
                # Format x-axis dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
                
                # Add legend
                ax.legend(loc='lower left')
            else:
                # Fallback to sample data if no returns data
                ax = canvas.fig.add_subplot(111)
                dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
                cumulative = np.cumsum(np.random.normal(0.001, 0.02, 100))
                peak = np.maximum.accumulate(cumulative)
                drawdown = 100 * (cumulative - peak) / peak
                
                ax.fill_between(dates, drawdown, 0, color='#E74C3C', alpha=0.3)
                ax.plot(dates, drawdown, 'r-', linewidth=1)
        
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas.fig.tight_layout()
        canvas.draw()
    
    def setup_trade_chart(self, canvas):
        """Set up the trade distribution chart with signals visualization"""
        # Get data from execution controller
        results = self.execution_controller.get_results()
        if not results or 'signals' not in results:
            # Use sample data if no real data is available
            ax = canvas.fig.add_subplot(111)
            returns = np.random.normal(0.5, 2.5, 100)
            
            ax.hist(returns, bins=20, alpha=0.7, color='#3498DB')
            ax.axvline(x=0, color='#E74C3C', linestyle='--')
            ax.set_xlabel('Trade Return (%)')
            ax.set_ylabel('Frequency')
        else:
            # Use real data to show signals on price chart
            signals_df = results['signals']
            market_data = self.execution_controller.get_market_data()
            
            if not market_data.empty and not signals_df.empty:
                ax = canvas.fig.add_subplot(111)
                
                # Plot price data
                ax.plot(market_data.index, market_data['close'], 'k-', linewidth=1, label='Price')
                
                # Plot signals from all strategies
                for column in signals_df.columns:
                    # Find long signals (1) and short signals (-1)
                    long_signals = signals_df[signals_df[column] == 1]
                    short_signals = signals_df[signals_df[column] == -1]
                    
                    # Plot long signals as green triangles
                    if not long_signals.empty:
                        ax.scatter(long_signals.index, 
                                  market_data.loc[long_signals.index, 'close'], 
                                  marker='^', color='green', s=100, label=f'{column} Buy')
                    
                    # Plot short signals as red triangles
                    if not short_signals.empty:
                        ax.scatter(short_signals.index, 
                                  market_data.loc[short_signals.index, 'close'], 
                                  marker='v', color='red', s=100, label=f'{column} Sell')
                # Handle legend with too many items
                handles, labels = ax.get_legend_handles_labels()
                if len(labels) > 10:  # If too many legend items
                    # Keep only the first few items plus 'Price'
                    price_idx = labels.index('Price') if 'Price' in labels else -1
                    if price_idx >= 0:
                        handles = [handles[price_idx]] + handles[:5]  # Price + first 5 signals
                        labels = [labels[price_idx]] + labels[:5]
                    else:
                        handles = handles[:6]  # Just first 6 items
                        labels = labels[:6]
                    # Add a note about hidden items
                    handles.append(handles[0])
                    labels.append(f'+ {len(ax.get_legend_handles_labels()[0]) - len(handles) + 1} more...')
                    ax.legend(handles, labels)
                else:
                    ax.legend()
                
                ax.set_title('Price Chart with Trading Signals')
                ax.set_xlabel('Date')
                ax.set_ylabel('Price')
                ax.legend()
        
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas.fig.tight_layout()
        canvas.draw()
    
    def refresh_dashboard(self):
        """Refresh the dashboard with the latest data"""
        logger.info("Refreshing dashboard with latest data")
        
        # Get the latest results directly from the execution controller
        results = self.execution_controller.get_results()
        
        if not results or 'signals' not in results:
            logger.warning("No results available to display in dashboard")
            # Update metrics with placeholder data
            metrics_grid = self.findChild(QGridLayout)
            if metrics_grid:
                # Clear existing metrics
                while metrics_grid.count():
                    item = metrics_grid.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                # Add placeholder metrics
                metrics_grid.addWidget(MetricCard("Total Return", "N/A", "%", "#95A5A6"), 0, 0)
                metrics_grid.addWidget(MetricCard("Sharpe Ratio", "N/A", "", "#95A5A6"), 0, 1)
                metrics_grid.addWidget(MetricCard("Max Drawdown", "N/A", "%", "#95A5A6"), 0, 2)
                metrics_grid.addWidget(MetricCard("Win Rate", "N/A", "%", "#95A5A6"), 0, 3)
            
            # Show message to user
            QMessageBox.information(self, "No Data", "No analysis results available. Run an analysis to see performance metrics.")
            return
        
        # Calculate performance metrics if market data is available
        market_data = results.get('market_data')
        signals_df = results.get('signals')
        
        if market_data is not None and not market_data.empty and 'returns' in market_data.columns:
            # Calculate performance metrics for each strategy
            performance_df = pd.DataFrame()
            
            # Add market returns as baseline
            market_returns = market_data['returns']
            market_cum_returns = (1 + market_returns).cumprod() - 1
            
            # Process each strategy
            for column in signals_df.columns:
                # Use signals to determine position
                signals = signals_df[column].fillna(0)
                position = signals.shift(1).fillna(0)
                
                # Calculate strategy returns
                strategy_return = position * market_returns
                strategy_cum_return = (1 + strategy_return).cumprod() - 1
                
                # Calculate metrics
                total_return = strategy_cum_return.iloc[-1] * 100 if len(strategy_cum_return) > 0 else 0
                
                # Calculate Sharpe ratio (annualized)
                if strategy_return.std() > 0:
                    sharpe = np.sqrt(252) * strategy_return.mean() / strategy_return.std()
                else:
                    sharpe = 0
                
                # Calculate max drawdown
                peak = np.maximum.accumulate(1 + strategy_cum_return)
                drawdown = (1 + strategy_cum_return) / peak - 1
                max_drawdown = drawdown.min() * 100
                
                # Calculate win rate
                if len(strategy_return) > 0:
                    win_rate = (strategy_return > 0).sum() / len(strategy_return) * 100
                else:
                    win_rate = 0
                
                # Store metrics for this strategy
                if not hasattr(self, 'strategy_metrics'):
                    self.strategy_metrics = {}
                
                self.strategy_metrics[column] = {
                    'total_return': total_return,
                    'sharpe_ratio': sharpe,
                    'max_drawdown': max_drawdown,
                    'win_rate': win_rate
                }
            
            # Update the dashboard with the latest data
            self.update_dashboard(results)
        else:
            logger.warning("Market data missing or doesn't contain returns")
            QMessageBox.warning(self, "Incomplete Data", "Market data is missing or doesn't contain returns information.")
            return
    
    def update_dashboard(self, results):
        """Update the dashboard with new results"""
        if not results or 'signals' not in results:
            return
            
        signals_df = results['signals']
        performance_df = results.get('performance', pd.DataFrame())
        
        # Calculate strategy metrics
        self.calculate_strategy_metrics(signals_df, performance_df)
        
        # Update all charts and metrics
        self.update_metrics_cards()
        self.update_charts(signals_df, performance_df)
        
    def calculate_strategy_metrics(self, signals_df, performance_df):
        """Calculate performance metrics for each strategy"""
        if signals_df.empty:
            return
            
        # Group by strategy
        if 'strategy' in signals_df.columns:
            strategy_groups = signals_df.groupby('strategy')
            
            for strategy_name, strategy_data in strategy_groups:
                # Calculate basic metrics
                signal_changes = strategy_data['signal'].diff().fillna(0)
                num_trades = (signal_changes != 0).sum()
                
                # Calculate win rate if we have performance data
                win_rate = 0
                total_return = 0
                max_drawdown = 0
                sharpe_ratio = 0
                
                if not performance_df.empty and 'strategy' in performance_df.columns:
                    strategy_perf = performance_df[performance_df['strategy'] == strategy_name]
                    if not strategy_perf.empty:
                        if 'win_rate' in strategy_perf.columns:
                            win_rate = strategy_perf['win_rate'].mean() * 100
                        if 'return' in strategy_perf.columns:
                            total_return = strategy_perf['return'].sum() * 100
                        if 'drawdown' in strategy_perf.columns:
                            max_drawdown = strategy_perf['drawdown'].min() * 100
                        if 'sharpe' in strategy_perf.columns:
                            sharpe_ratio = strategy_perf['sharpe'].mean()
                
                # Store metrics
                self.strategy_metrics[strategy_name] = {
                    'num_trades': num_trades,
                    'win_rate': win_rate,
                    'total_return': total_return,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio
                }
                
                # Store performance data for charts
                if 'cumulative_return' in performance_df.columns:
                    strategy_returns = performance_df[performance_df['strategy'] == strategy_name]['cumulative_return']
                    if not strategy_returns.empty:
                        self.performance_data[strategy_name] = strategy_returns
    
    def update_metrics_cards(self):
        """Update the metrics cards with the latest data"""
        # This would be implemented to update the metrics cards with real data
        # For now, we'll use sample data that includes our new strategies
        
        # Find the metrics grid layout
        metrics_grid = None
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QScrollArea):
                scroll_area = item.widget()
                dashboard_widget = scroll_area.widget()
                dashboard_layout = dashboard_widget.layout()
                
                # Find the metrics grid in the dashboard layout
                for j in range(dashboard_layout.count()):
                    layout_item = dashboard_layout.itemAt(j)
                    if layout_item and isinstance(layout_item, QGridLayout):
                        metrics_grid = layout_item
                        break
        
        if not metrics_grid:
            return
            
        # Clear existing metrics
        while metrics_grid.count():
            item = metrics_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add metrics for all strategies including new ones
        row, col = 0, 0
        max_cols = 4
        
        # Add overall metrics first
        total_return = sum([metrics.get('total_return', 0) for metrics in self.strategy_metrics.values()])
        avg_win_rate = np.mean([metrics.get('win_rate', 0) for metrics in self.strategy_metrics.values()])
        max_dd = min([metrics.get('max_drawdown', 0) for metrics in self.strategy_metrics.values()])
        avg_sharpe = np.mean([metrics.get('sharpe_ratio', 0) for metrics in self.strategy_metrics.values()])
        
        # Add overall metrics
        metrics_grid.addWidget(MetricCard("Total Return", f"{total_return:.1f}", "%", "#18BC9C", 
                                        "up" if total_return > 0 else "down", abs(total_return)), row, col)
        col += 1
        metrics_grid.addWidget(MetricCard("Avg Win Rate", f"{avg_win_rate:.1f}", "%", "#3498DB"), row, col)
        col += 1
        metrics_grid.addWidget(MetricCard("Max Drawdown", f"{abs(max_dd):.1f}", "%", "#E74C3C"), row, col)
        col += 1
        metrics_grid.addWidget(MetricCard("Avg Sharpe", f"{avg_sharpe:.2f}", "", "#F39C12"), row, col)
        
        # Add strategy-specific metrics
        row += 1
        col = 0
        
        # Add metrics for Volume Profile strategy
        if "Volume Profile" in self.strategy_metrics:
            metrics = self.strategy_metrics["Volume Profile"]
            metrics_grid.addWidget(MetricCard("Volume Profile Return", 
                                            f"{metrics.get('total_return', 0):.1f}", "%", "#9B59B6",
                                            "up" if metrics.get('total_return', 0) > 0 else "down", 
                                            abs(metrics.get('total_return', 0))), row, col)
            col += 1
            if col >= max_cols:
                row += 1
                col = 0
        
        # Add metrics for Fibonacci Retracement strategy
        if "Fibonacci Retracement" in self.strategy_metrics:
            metrics = self.strategy_metrics["Fibonacci Retracement"]
            metrics_grid.addWidget(MetricCard("Fibonacci Return", 
                                            f"{metrics.get('total_return', 0):.1f}", "%", "#2ECC71",
                                            "up" if metrics.get('total_return', 0) > 0 else "down", 
                                            abs(metrics.get('total_return', 0))), row, col)
    
    def update_charts(self, signals_df, performance_df):
        """Update all charts with the latest data"""
        # Find all chart panels
        chart_panels = []
        
        # Find the scroll area containing the dashboard
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QScrollArea):
                scroll_area = item.widget()
                dashboard_widget = scroll_area.widget()
                
                # Find all QSplitter widgets that might contain charts
                splitters = dashboard_widget.findChildren(QSplitter)
                for splitter in splitters:
                    # Find all ChartPanel widgets in each splitter
                    for j in range(splitter.count()):
                        widget = splitter.widget(j)
                        if isinstance(widget, QSplitter):
                            # This is a nested splitter, check its children
                            for k in range(widget.count()):
                                child = widget.widget(k)
                                if isinstance(child, ChartPanel):
                                    chart_panels.append(child)
                        elif isinstance(widget, ChartPanel):
                            chart_panels.append(widget)
        
        # Update each chart with real data
        for panel in chart_panels:
            title = panel.findChild(QLabel).text()
            
            if "Cumulative Returns" in title:
                self.update_returns_chart(panel.canvas, performance_df)
            elif "Strategy Comparison" in title:
                self.update_comparison_chart(panel.canvas)
            elif "Drawdown" in title:
                self.update_drawdown_chart(panel.canvas, performance_df)
            elif "Trade Distribution" in title:
                self.update_trade_chart(panel.canvas, signals_df)
    
    def update_returns_chart(self, canvas, performance_df):
        """Update the cumulative returns chart with real data"""
        if performance_df.empty or 'date' not in performance_df.columns or 'cumulative_return' not in performance_df.columns:
            return
            
        # Clear the figure
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        
        # Group by strategy and plot each one
        if 'strategy' in performance_df.columns:
            for strategy, data in performance_df.groupby('strategy'):
                # Sort by date
                data = data.sort_values('date')
                
                # Plot the strategy returns
                color = '#3498DB'  # Default color
                if strategy == 'Volume Profile':
                    color = '#9B59B6'  # Purple for Volume Profile
                elif strategy == 'Fibonacci Retracement':
                    color = '#2ECC71'  # Green for Fibonacci
                
                ax.plot(data['date'], data['cumulative_return'] * 100, 
                        label=strategy, linewidth=2, color=color)
        
        ax.set_ylabel('Cumulative Returns (%)')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend()
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        canvas.fig.tight_layout()
        canvas.draw()
    
    def update_comparison_chart(self, canvas):
        """Update the strategy comparison chart with real data"""
        # Clear the figure
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        
        # Get strategy returns
        strategies = list(self.strategy_metrics.keys())
        returns = [self.strategy_metrics[s].get('total_return', 0) for s in strategies]
        
        # Define colors for each strategy
        colors = ['#3498DB', '#E74C3C', '#F39C12', '#18BC9C', '#9B59B6', '#2ECC71']
        if len(strategies) > len(colors):
            colors = colors * (len(strategies) // len(colors) + 1)
        
        # Create the bar chart
        bars = ax.bar(strategies, returns, color=colors[:len(strategies)], alpha=0.8)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        ax.set_ylabel('Total Return (%)')
        ax.set_title('Strategy Performance Comparison')
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Rotate x-axis labels if there are many strategies
        if len(strategies) > 3:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        canvas.fig.tight_layout()
        canvas.draw()
    
    def update_drawdown_chart(self, canvas, performance_df):
        """Update the drawdown analysis chart with real data"""
        if performance_df.empty or 'date' not in performance_df.columns or 'drawdown' not in performance_df.columns:
            return
            
        # Clear the figure
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        
        # Group by strategy and plot each one
        if 'strategy' in performance_df.columns:
            for strategy, data in performance_df.groupby('strategy'):
                # Sort by date
                data = data.sort_values('date')
                
                # Plot the strategy drawdown
                color = '#E74C3C'  # Default color (red)
                alpha = 0.3
                
                if strategy == 'Volume Profile':
                    color = '#9B59B6'  # Purple for Volume Profile
                elif strategy == 'Fibonacci Retracement':
                    color = '#2ECC71'  # Green for Fibonacci
                
                ax.plot(data['date'], data['drawdown'] * 100, 
                        label=strategy, linewidth=1, color=color)
                ax.fill_between(data['date'], data['drawdown'] * 100, 0, 
                                color=color, alpha=alpha)
        
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend()
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        canvas.fig.tight_layout()
        canvas.draw()
    
    def update_trade_chart(self, canvas, signals_df):
        """Update the trade distribution chart with real data"""
        if signals_df.empty or 'signal' not in signals_df.columns:
            return
            
        # Clear the figure
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        
        # Calculate trade returns (simplified)
        if 'close' in signals_df.columns and 'signal' in signals_df.columns:
            # Calculate price changes
            price_changes = signals_df['close'].pct_change() * 100
            
            # Filter for trades (where signal changes)
            signal_changes = signals_df['signal'].diff().fillna(0)
            trades = price_changes[signal_changes != 0]
            
            # Plot histogram of trade returns
            if not trades.empty:
                ax.hist(trades, bins=20, alpha=0.7, color='#3498DB')
                ax.axvline(x=0, color='#E74C3C', linestyle='--')
        
        ax.set_xlabel('Trade Return (%)')
        ax.set_ylabel('Frequency')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas.fig.tight_layout()
        canvas.draw()