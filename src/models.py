"""
Core data models for the retirement calculator.

This module contains dataclasses that define the primary data structures
used throughout the retirement planning application.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np


@dataclass
class UserInput:
    """User input data for retirement calculations."""
    current_age: int
    current_savings: float
    monthly_savings: float
    desired_annual_income: float
    
    def __post_init__(self):
        """Validate user input data."""
        if self.current_age < 18 or self.current_age > 80:
            raise ValueError("Current age must be between 18 and 80")
        if self.current_savings < 0:
            raise ValueError("Current savings cannot be negative")
        if self.monthly_savings < 0:
            raise ValueError("Monthly savings cannot be negative")
        if self.desired_annual_income <= 0:
            raise ValueError("Desired annual income must be positive")


@dataclass
class PortfolioAllocation:
    """Portfolio allocation configuration."""
    name: str
    equity_percentage: float
    bond_percentage: float
    cash_percentage: float
    
    def __post_init__(self):
        """Validate portfolio allocation percentages."""
        total = self.equity_percentage + self.bond_percentage + self.cash_percentage
        if abs(total - 1.0) > 0.001:
            raise ValueError("Portfolio allocation percentages must sum to 1.0")


@dataclass
class SimulationResult:
    """Results from a single Monte Carlo simulation scenario."""
    portfolio_allocation: PortfolioAllocation
    retirement_age: int
    success_rate: float
    portfolio_values: np.ndarray
    withdrawal_amounts: np.ndarray
    final_portfolio_value: float
    percentile_data: Optional[Dict[str, np.ndarray]] = None
    
    
@dataclass
class GuardRailsThresholds:
    """Guard rails thresholds for spending adjustments."""
    upper_threshold: float = 0.20  # 20% above initial portfolio value
    lower_threshold: float = 0.15  # 15% below initial portfolio value
    severe_threshold: float = 0.25  # 25% below initial portfolio value
    lower_adjustment: float = 0.10  # 10% spending reduction
    severe_adjustment: float = 0.20  # 20% spending reduction
    
    
@dataclass
class TaxBracket:
    """UK tax bracket information."""
    lower_limit: float
    upper_limit: float
    rate: float
    
    
@dataclass
class RetirementResults:
    """Complete retirement calculation results."""
    user_input: UserInput
    portfolio_results: List[SimulationResult]
    recommended_portfolio: PortfolioAllocation
    recommended_retirement_age: int
    percentile_data: Dict[str, Dict[str, np.ndarray]]  # portfolio_name -> {10th, 50th, 90th}