"""
Core Data Models

This module defines the core data structures used throughout the retirement
calculator application using Python dataclasses.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserInput:
    """
    User input data for retirement calculation.
    
    All monetary values are in today's purchasing power (real terms).
    """
    current_age: int
    current_savings: float  # In today's pounds
    monthly_savings: float  # In today's pounds
    desired_annual_income: float  # In today's pounds, after-tax
    
    def __post_init__(self):
        """Validate user input data."""
        if self.current_age < 18 or self.current_age > 80:
            raise ValueError("Age must be between 18 and 80")
        if self.current_savings < 0:
            raise ValueError("Current savings cannot be negative")
        if self.monthly_savings < 0:
            raise ValueError("Monthly savings cannot be negative")
        if self.desired_annual_income <= 0:
            raise ValueError("Desired annual income must be positive")


@dataclass
class PortfolioAllocation:
    """
    Portfolio allocation configuration.
    
    Defines the percentage allocation across different asset classes.
    Percentages should sum to 100.
    """
    name: str
    equity_percentage: float
    bond_percentage: float
    cash_percentage: float
    
    def __post_init__(self):
        """Validate portfolio allocation percentages."""
        total = self.equity_percentage + self.bond_percentage + self.cash_percentage
        if abs(total - 100.0) > 0.01:  # Allow for small floating point errors
            raise ValueError(f"Portfolio percentages must sum to 100, got {total}")
        if any(pct < 0 for pct in [self.equity_percentage, self.bond_percentage, self.cash_percentage]):
            raise ValueError("Portfolio percentages cannot be negative")


@dataclass
class SimulationResult:
    """
    Results from Monte Carlo simulation for a specific portfolio allocation.
    
    Contains success rates, retirement age, and portfolio value projections
    over time for statistical analysis and visualization.
    """
    portfolio_allocation: PortfolioAllocation
    retirement_age: Optional[int]  # None if no viable retirement age found
    success_rate: float  # Percentage of scenarios with money at age 100
    portfolio_values_over_time: List[List[float]]  # [scenario][year] portfolio values
    percentile_10: List[float]  # 10th percentile portfolio values by year
    percentile_50: List[float]  # 50th percentile (median) portfolio values by year
    percentile_90: List[float]  # 90th percentile portfolio values by year
    
    def __post_init__(self):
        """Validate simulation result data."""
        if self.success_rate < 0 or self.success_rate > 100:
            raise ValueError("Success rate must be between 0 and 100")
        if self.retirement_age is not None and (self.retirement_age < 18 or self.retirement_age > 100):
            raise ValueError("Retirement age must be between 18 and 100")


# Predefined portfolio allocations for the retirement calculator
PORTFOLIO_ALLOCATIONS = [
    PortfolioAllocation("100% Cash", 0.0, 0.0, 100.0),
    PortfolioAllocation("100% Bonds", 0.0, 100.0, 0.0),
    PortfolioAllocation("25% Equity / 75% Bonds", 25.0, 75.0, 0.0),
    PortfolioAllocation("50% Equity / 50% Bonds", 50.0, 50.0, 0.0),
    PortfolioAllocation("75% Equity / 25% Bonds", 75.0, 25.0, 0.0),
    PortfolioAllocation("100% Equity", 100.0, 0.0, 0.0),
]