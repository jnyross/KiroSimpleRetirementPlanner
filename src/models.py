"""
Core data models for the retirement calculator.

This module contains dataclasses that define the primary data structures
used throughout the retirement planning application.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np


@dataclass
class UserInput:
    """User input data for retirement calculations."""
    current_age: int
    current_savings: float
    monthly_savings: float
    desired_annual_income: float
    target_success_rate: float = 0.95  # Default to 95% (updated in v1.1.0)
    
    # New v1.1.0 features
    cash_buffer_years: float = 2.0  # Years of spending held in cash
    state_pension_age: int = 67  # UK state pension age
    state_pension_amount: float = 9110.0  # Current UK full state pension
    spending_phases: List[Tuple[int, float]] = field(default_factory=lambda: [(75, 0.75)])  # Age, multiplier
    
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
        if not 0.5 <= self.target_success_rate <= 1.0:
            raise ValueError("Target success rate must be between 50% and 100%")
        
        # New v1.1.0 validations
        if self.cash_buffer_years < 0 or self.cash_buffer_years > 5:
            raise ValueError("Cash buffer must be between 0 and 5 years")
        if self.state_pension_age < 60 or self.state_pension_age > 75:
            raise ValueError("State pension age must be between 60 and 75")
        if self.state_pension_amount < 0 or self.state_pension_amount > 20000:
            raise ValueError("State pension amount must be between £0 and £20,000")
        
        # Validate spending phases
        for age, multiplier in self.spending_phases:
            if age < self.current_age or age > 100:
                raise ValueError(f"Spending phase age {age} must be between current age and 100")
            if multiplier < 0.1 or multiplier > 1.0:
                raise ValueError(f"Spending multiplier {multiplier} must be between 0.1 and 1.0")


@dataclass
class PortfolioAllocation:
    """Portfolio allocation configuration."""
    name: str
    equity_percentage: float
    bond_percentage: float
    cash_percentage: float
    is_dynamic: bool = False
    
    def __post_init__(self):
        """Validate portfolio allocation percentages."""
        total = self.equity_percentage + self.bond_percentage + self.cash_percentage
        if abs(total - 1.0) > 0.001:
            raise ValueError("Portfolio allocation percentages must sum to 1.0")
    
    def get_allocation_for_age(self, current_age: int, retirement_age: int) -> Tuple[float, float, float]:
        """
        Get allocation percentages for a given age.
        
        For static allocations, returns the fixed percentages.
        For dynamic allocations, this method should be overridden.
        
        Args:
            current_age: Current age of investor
            retirement_age: Target retirement age
            
        Returns:
            Tuple of (equity_percentage, bond_percentage, cash_percentage)
        """
        return self.equity_percentage, self.bond_percentage, self.cash_percentage


class DynamicGlidePath(PortfolioAllocation):
    """
    Dynamic portfolio allocation that follows a glide path from equity to bonds.
    
    The allocation gradually shifts from high equity when young to high bonds
    in retirement, following a smooth glide path.
    """
    
    def __init__(self):
        # Initialize with placeholder values - actual allocation is dynamic
        super().__init__(
            name="Dynamic Glide Path (Age-Based)",
            equity_percentage=0.5,  # Placeholder - will be calculated dynamically
            bond_percentage=0.5,    # Placeholder - will be calculated dynamically
            cash_percentage=0.0,
            is_dynamic=True
        )
    
    def get_allocation_for_age(self, current_age: int, retirement_age: int) -> Tuple[float, float, float]:
        """
        Calculate allocation based on age using a glide path formula.
        
        The glide path:
        - Starts at 90% equity at age 25 or younger
        - Gradually decreases to 30% equity at retirement
        - Continues to decrease to 20% equity by age 75
        - Maintains minimum 20% equity after age 75
        
        Args:
            current_age: Current age of investor
            retirement_age: Target retirement age
            
        Returns:
            Tuple of (equity_percentage, bond_percentage, cash_percentage)
        """
        # Define glide path parameters
        max_equity_age = 25
        max_equity_pct = 0.90
        retirement_equity_pct = 0.30
        min_equity_age = 75
        min_equity_pct = 0.20
        
        # Calculate equity percentage based on age
        if current_age <= max_equity_age:
            equity_pct = max_equity_pct
        elif current_age >= min_equity_age:
            equity_pct = min_equity_pct
        elif current_age < retirement_age:
            # Pre-retirement: Linear decrease from max to retirement target
            years_to_retirement = retirement_age - current_age
            total_pre_retirement_years = retirement_age - max_equity_age
            progress = 1 - (years_to_retirement / total_pre_retirement_years)
            equity_pct = max_equity_pct - (max_equity_pct - retirement_equity_pct) * progress
        else:
            # Post-retirement: Linear decrease from retirement to minimum
            years_since_retirement = current_age - retirement_age
            total_post_retirement_years = min_equity_age - retirement_age
            if total_post_retirement_years > 0:
                progress = min(1.0, years_since_retirement / total_post_retirement_years)
                equity_pct = retirement_equity_pct - (retirement_equity_pct - min_equity_pct) * progress
            else:
                equity_pct = min_equity_pct
        
        # Ensure equity percentage is within bounds
        equity_pct = max(min_equity_pct, min(max_equity_pct, equity_pct))
        
        # Allocate remaining to bonds (no cash in glide path)
        bond_pct = 1.0 - equity_pct
        cash_pct = 0.0
        
        return equity_pct, bond_pct, cash_pct


class RisingGlidePath(PortfolioAllocation):
    """
    Rising equity glide path that starts conservative and increases equity over time.
    
    Based on Pfau-Kitces research showing this can reduce sequence of returns risk
    by starting with lower equity allocation at retirement and gradually increasing.
    """
    
    def __init__(self):
        super().__init__(
            name="Rising Glide Path (Bond-to-Equity)",
            equity_percentage=0.3,  # Placeholder - will be calculated dynamically
            bond_percentage=0.7,    # Placeholder - will be calculated dynamically
            cash_percentage=0.0,
            is_dynamic=True
        )
    
    def get_allocation_for_age(self, current_age: int, retirement_age: int) -> Tuple[float, float, float]:
        """
        Calculate allocation based on age using a rising glide path.
        
        The glide path:
        - Starts at 30% equity at retirement
        - Gradually increases to 70% equity by age 85
        - Maintains 70% equity after age 85
        
        Args:
            current_age: Current age of investor
            retirement_age: Target retirement age
            
        Returns:
            Tuple of (equity_percentage, bond_percentage, cash_percentage)
        """
        if current_age < retirement_age:
            # Pre-retirement: Use moderate allocation
            equity_pct = 0.50
        else:
            # Post-retirement: Rising equity glide path
            start_equity = 0.30
            end_equity = 0.70
            end_age = 85
            
            if current_age >= end_age:
                equity_pct = end_equity
            else:
                years_since_retirement = current_age - retirement_age
                total_years = end_age - retirement_age
                if total_years > 0:
                    progress = min(1.0, years_since_retirement / total_years)
                    equity_pct = start_equity + (end_equity - start_equity) * progress
                else:
                    equity_pct = start_equity
        
        # Allocate remaining to bonds (no cash in glide path)
        bond_pct = 1.0 - equity_pct
        cash_pct = 0.0
        
        return equity_pct, bond_pct, cash_pct


class TargetDateFund(PortfolioAllocation):
    """
    Target date fund style allocation using the '120 minus age' rule.
    
    Simple and widely used allocation strategy that automatically
    becomes more conservative with age.
    """
    
    def __init__(self):
        super().__init__(
            name="Target Date Fund (120-Age)",
            equity_percentage=0.5,  # Placeholder - will be calculated dynamically
            bond_percentage=0.5,    # Placeholder - will be calculated dynamically
            cash_percentage=0.0,
            is_dynamic=True
        )
    
    def get_allocation_for_age(self, current_age: int, retirement_age: int) -> Tuple[float, float, float]:
        """
        Calculate allocation using 120 minus age formula.
        
        Formula: Equity % = (120 - current_age) / 100
        Minimum equity: 20%
        Maximum equity: 90%
        
        Args:
            current_age: Current age of investor
            retirement_age: Target retirement age (not used in this strategy)
            
        Returns:
            Tuple of (equity_percentage, bond_percentage, cash_percentage)
        """
        # Calculate equity percentage
        equity_pct = (120 - current_age) / 100
        
        # Apply bounds
        equity_pct = max(0.20, min(0.90, equity_pct))
        
        # Allocate remaining to bonds
        bond_pct = 1.0 - equity_pct
        cash_pct = 0.0
        
        return equity_pct, bond_pct, cash_pct


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
    
    # New v1.1.0: Guyton-Klinger enhancements
    enable_ratcheting: bool = True  # Allow permanent spending increases
    ratchet_threshold: float = 0.20  # Trigger ratchet at 20% above initial
    ratchet_increase: float = 0.10  # 10% permanent spending increase
    
    # Dynamic spending strategy selection
    strategy: str = "guardrails"  # Options: "guardrails", "guyton-klinger", "vanguard"
    
    
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