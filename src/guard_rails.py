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
        
    def calculate_withdrawal_adjustment(self, current_portfolio_value: float,
                                      initial_portfolio_value: float,
                                      base_withdrawal: float) -> Tuple[float, str]:
        """
        Calculate withdrawal adjustment based on portfolio performance.
        
        Args:
            current_portfolio_value: Current portfolio value
            initial_portfolio_value: Initial portfolio value at retirement
            base_withdrawal: Base withdrawal amount
            
        Returns:
            Tuple of (adjusted_withdrawal, adjustment_reason)
        """
        if initial_portfolio_value <= 0:
            return base_withdrawal, "normal"
        
        # Calculate performance relative to initial value
        performance_ratio = current_portfolio_value / initial_portfolio_value
        
        # Determine adjustment based on performance thresholds
        if performance_ratio >= (1.0 + self.thresholds.upper_threshold):
            # Above upper guard rail - allow normal spending
            return base_withdrawal, "normal"
        elif performance_ratio <= (1.0 - self.thresholds.severe_threshold):
            # Below severe guard rail - reduce spending by 20%
            adjusted_withdrawal = base_withdrawal * (1.0 - self.thresholds.severe_adjustment)
            return adjusted_withdrawal, "severe_reduction"
        elif performance_ratio <= (1.0 - self.thresholds.lower_threshold):
            # Below lower guard rail - reduce spending by 10%
            adjusted_withdrawal = base_withdrawal * (1.0 - self.thresholds.lower_adjustment)
            return adjusted_withdrawal, "lower_reduction"
        else:
            # Within normal range
            return base_withdrawal, "normal"
    
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