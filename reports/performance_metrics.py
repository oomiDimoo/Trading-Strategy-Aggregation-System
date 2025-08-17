import numpy as np
import pandas as pd

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculate the Sharpe ratio.

    Args:
        returns: A pandas Series of returns.
        risk_free_rate: The risk-free rate of return.

    Returns:
        The Sharpe ratio.
    """
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std()

def calculate_sortino_ratio(returns, risk_free_rate=0.0):
    """
    Calculate the Sortino ratio.

    Args:
        returns: A pandas Series of returns.
        risk_free_rate: The risk-free rate of return.

    Returns:
        The Sortino ratio.
    """
    excess_returns = returns - risk_free_rate
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = downside_returns.std()
    if downside_std == 0:
        return np.inf
    return excess_returns.mean() / downside_std

def calculate_max_drawdown(returns):
    """
    Calculate the maximum drawdown.

    Args:
        returns: A pandas Series of returns.

    Returns:
        The maximum drawdown.
    """
    cumulative_returns = (1 + returns).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    return drawdown.min()

def calculate_profit_factor(returns):
    """
    Calculate the profit factor.

    Args:
        returns: A pandas Series of returns.

    Returns:
        The profit factor.
    """
    gross_profits = returns[returns > 0].sum()
    gross_losses = abs(returns[returns < 0].sum())
    if gross_losses == 0:
        return np.inf
    return gross_profits / gross_losses
