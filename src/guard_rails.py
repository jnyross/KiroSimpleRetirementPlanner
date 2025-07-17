"""
Guard rails withdrawal system for the retirement calculator.

This module implements dynamic spending adjustments based on portfolio
performance to increase the likelihood of successful retirement outcomes.
"""

import numpy as np
from typing import Tuple, Dict, List
from .models import GuardRailsThresholds


class GuardRailsEngine:
    """Implements the guard rails withdrawal system."""
    
    def __init__(self, thresholds: GuardRailsThresholds = None):
        """
        Initialize the guard rails engine.
        
        Args:
            thresholds: Guard rails thresholds configuration
        """
        self.thresholds = thresholds or GuardRailsThresholds()
        self.ratcheted_base = None  # Track ratcheted spending level
        
    def calculate_withdrawal_adjustment(self, current_portfolio_value: float,
                                      initial_portfolio_value: float,
                                      base_withdrawal: float,
                                      current_year: int = 0,
                                      portfolio_return: float = None) -> Tuple[float, str]:
        """
        Calculate withdrawal adjustment based on portfolio performance.
        
        Now supports Guyton-Klinger ratcheting and enhanced rules (v1.1.0).
        
        Args:
            current_portfolio_value: Current portfolio value
            initial_portfolio_value: Initial portfolio value at retirement
            base_withdrawal: Base withdrawal amount
            current_year: Current year in retirement (for ratcheting)
            portfolio_return: Portfolio return for current year (for capital preservation rule)
            
        Returns:
            Tuple of (adjusted_withdrawal, adjustment_reason)
        """
        if initial_portfolio_value <= 0:
            return base_withdrawal, "normal"
        
        # Initialize ratcheted base if needed
        if self.ratcheted_base is None:
            self.ratcheted_base = base_withdrawal
        
        # Use ratcheted base for calculations
        working_withdrawal = self.ratcheted_base
        
        # Calculate performance relative to initial value
        performance_ratio = current_portfolio_value / initial_portfolio_value
        
        # Check for Guyton-Klinger ratcheting opportunity
        if (self.thresholds.strategy == "guyton-klinger" and 
            self.thresholds.enable_ratcheting and
            performance_ratio >= (1.0 + self.thresholds.ratchet_threshold)):
            # Ratchet up spending permanently
            self.ratcheted_base *= (1.0 + self.thresholds.ratchet_increase)
            working_withdrawal = self.ratcheted_base
            adjustment_reason = "ratchet_increase"
        
        # Apply Guyton-Klinger capital preservation rule
        elif (self.thresholds.strategy == "guyton-klinger" and 
              portfolio_return is not None and 
              portfolio_return < 0):
            # Skip withdrawal increase in down years
            adjustment_reason = "capital_preservation"
        
        # Standard guard rails adjustments
        elif performance_ratio <= (1.0 - self.thresholds.severe_threshold):
            # Below severe guard rail - reduce spending by 20%
            working_withdrawal = self.ratcheted_base * (1.0 - self.thresholds.severe_adjustment)
            adjustment_reason = "severe_reduction"
        elif performance_ratio <= (1.0 - self.thresholds.lower_threshold):
            # Below lower guard rail - reduce spending by 10%
            working_withdrawal = self.ratcheted_base * (1.0 - self.thresholds.lower_adjustment)
            adjustment_reason = "lower_reduction"
        else:
            # Within normal range
            adjustment_reason = "normal"
        
        return working_withdrawal, adjustment_reason
    
    def simulate_withdrawal_sequence(self, portfolio_values: np.ndarray,
                                   initial_portfolio_value: float,
                                   base_withdrawal: float) -> Tuple[np.ndarray, List[str]]:
        """
        Simulate withdrawal sequence with guard rails adjustments.
        
        Args:
            portfolio_values: Array of portfolio values over time
            initial_portfolio_value: Initial portfolio value
            base_withdrawal: Base annual withdrawal amount
            
        Returns:
            Tuple of (withdrawal_amounts, adjustment_reasons)
        """
        num_years = len(portfolio_values)
        withdrawal_amounts = np.zeros(num_years)
        adjustment_reasons = []
        
        for year in range(num_years):
            current_value = portfolio_values[year]
            withdrawal, reason = self.calculate_withdrawal_adjustment(
                current_value, initial_portfolio_value, base_withdrawal
            )
            withdrawal_amounts[year] = withdrawal
            adjustment_reasons.append(reason)
        
        return withdrawal_amounts, adjustment_reasons
    
    def calculate_success_probability(self, portfolio_values: np.ndarray,
                                    initial_portfolio_value: float,
                                    base_withdrawal: float) -> float:
        """
        Calculate probability of portfolio surviving with guard rails.
        
        Args:
            portfolio_values: Array of portfolio values over time
            initial_portfolio_value: Initial portfolio value
            base_withdrawal: Base annual withdrawal amount
            
        Returns:
            Probability of success (0.0 to 1.0)
        """
        # Simulate portfolio evolution with guard rails
        current_value = initial_portfolio_value
        
        for year in range(len(portfolio_values)):
            # Calculate withdrawal with guard rails
            withdrawal, _ = self.calculate_withdrawal_adjustment(
                current_value, initial_portfolio_value, base_withdrawal
            )
            
            # Update portfolio value after withdrawal
            current_value = max(0, current_value - withdrawal)
            
            # Apply market return
            if year < len(portfolio_values) - 1:
                return_rate = (portfolio_values[year + 1] / portfolio_values[year]) - 1
                current_value *= (1 + return_rate)
            
            # If portfolio depleted, return failure
            if current_value <= 0:
                return 0.0
        
        return 1.0 if current_value > 0 else 0.0
    
    def get_adjustment_statistics(self, adjustment_reasons: List[str]) -> Dict[str, float]:
        """
        Get statistics about guard rails adjustments.
        
        Args:
            adjustment_reasons: List of adjustment reasons over time
            
        Returns:
            Dictionary with adjustment statistics
        """
        if not adjustment_reasons:
            return {}
        
        total_years = len(adjustment_reasons)
        stats = {
            'normal_years': adjustment_reasons.count('normal') / total_years,
            'lower_reduction_years': adjustment_reasons.count('lower_reduction') / total_years,
            'severe_reduction_years': adjustment_reasons.count('severe_reduction') / total_years,
            'total_adjustment_years': (adjustment_reasons.count('lower_reduction') + 
                                     adjustment_reasons.count('severe_reduction')) / total_years
        }
        
        return stats
    
    def calculate_cumulative_withdrawal(self, withdrawal_amounts: np.ndarray) -> float:
        """
        Calculate cumulative withdrawal amount over time.
        
        Args:
            withdrawal_amounts: Array of annual withdrawal amounts
            
        Returns:
            Total cumulative withdrawal
        """
        return np.sum(withdrawal_amounts)
    
    def get_withdrawal_summary(self, withdrawal_amounts: np.ndarray,
                             adjustment_reasons: List[str]) -> Dict[str, float]:
        """
        Get summary statistics for withdrawal sequence.
        
        Args:
            withdrawal_amounts: Array of annual withdrawal amounts
            adjustment_reasons: List of adjustment reasons
            
        Returns:
            Dictionary with withdrawal summary statistics
        """
        if len(withdrawal_amounts) == 0:
            return {}
        
        stats = {
            'total_withdrawal': np.sum(withdrawal_amounts),
            'average_withdrawal': np.mean(withdrawal_amounts),
            'min_withdrawal': np.min(withdrawal_amounts),
            'max_withdrawal': np.max(withdrawal_amounts),
            'withdrawal_volatility': np.std(withdrawal_amounts)
        }
        
        # Add adjustment statistics
        adjustment_stats = self.get_adjustment_statistics(adjustment_reasons)
        stats.update(adjustment_stats)
        
        return stats
    
    def test_guard_rails_scenarios(self, initial_value: float, 
                                 base_withdrawal: float) -> Dict[str, Tuple[float, str]]:
        """
        Test guard rails adjustments for various portfolio performance scenarios.
        
        Args:
            initial_value: Initial portfolio value
            base_withdrawal: Base withdrawal amount
            
        Returns:
            Dictionary mapping scenarios to (withdrawal, reason) tuples
        """
        scenarios = {
            'excellent_performance': 1.3 * initial_value,  # 30% above initial
            'good_performance': 1.1 * initial_value,       # 10% above initial
            'normal_performance': initial_value,            # Same as initial
            'poor_performance': 0.9 * initial_value,       # 10% below initial
            'bad_performance': 0.8 * initial_value,        # 20% below initial
            'severe_performance': 0.7 * initial_value      # 30% below initial
        }
        
        results = {}
        for scenario, portfolio_value in scenarios.items():
            withdrawal, reason = self.calculate_withdrawal_adjustment(
                portfolio_value, initial_value, base_withdrawal
            )
            results[scenario] = (withdrawal, reason)
        
        return results
    
    def validate_thresholds(self) -> bool:
        """
        Validate guard rails thresholds configuration.
        
        Returns:
            True if thresholds are valid, False otherwise
        """
        try:
            # Check threshold values are reasonable
            if not (0 < self.thresholds.upper_threshold < 1.0):
                return False
            if not (0 < self.thresholds.lower_threshold < 1.0):
                return False
            if not (0 < self.thresholds.severe_threshold < 1.0):
                return False
            
            # Check severe threshold is greater than lower threshold
            if self.thresholds.severe_threshold <= self.thresholds.lower_threshold:
                return False
            
            # Check adjustment percentages are reasonable
            if not (0 < self.thresholds.lower_adjustment < 1.0):
                return False
            if not (0 < self.thresholds.severe_adjustment < 1.0):
                return False
            
            # Check severe adjustment is greater than lower adjustment
            if self.thresholds.severe_adjustment <= self.thresholds.lower_adjustment:
                return False
            
            return True
            
        except Exception:
            return False
    
    def update_thresholds(self, new_thresholds: GuardRailsThresholds) -> None:
        """
        Update guard rails thresholds.
        
        Args:
            new_thresholds: New thresholds configuration
        """
        if not self.validate_thresholds():
            raise ValueError("Invalid guard rails thresholds")
        
        self.thresholds = new_thresholds
    
    def calculate_vanguard_withdrawal(self, previous_withdrawal: float,
                                    inflation_rate: float,
                                    portfolio_performance: float) -> Tuple[float, str]:
        """
        Calculate withdrawal using Vanguard dynamic spending rule (v1.1.0).
        
        Formula: Previous withdrawal × (1 + inflation) × performance factor
        Capped at +5% increase or -2.5% decrease annually.
        
        Args:
            previous_withdrawal: Previous year's withdrawal
            inflation_rate: Current inflation rate
            portfolio_performance: Portfolio performance ratio
            
        Returns:
            Tuple of (adjusted_withdrawal, adjustment_reason)
        """
        # Adjust for inflation
        inflation_adjusted = previous_withdrawal * (1 + inflation_rate)
        
        # Calculate performance factor
        if portfolio_performance > 1.05:
            factor = 1.05  # Cap at 5% increase
            reason = "vanguard_capped_increase"
        elif portfolio_performance < 0.975:
            factor = 0.975  # Floor at 2.5% decrease
            reason = "vanguard_capped_decrease"
        else:
            factor = portfolio_performance
            reason = "vanguard_normal"
        
        adjusted_withdrawal = inflation_adjusted * factor
        
        return adjusted_withdrawal, reason