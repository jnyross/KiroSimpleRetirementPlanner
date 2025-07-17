"""
Results analysis and statistics calculator for retirement planning.

This module processes simulation outputs to calculate success rates, percentiles,
and determine optimal retirement ages with 99% confidence threshold.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from .models import UserInput, PortfolioAllocation, SimulationResult, RetirementResults


class ResultsAnalyzer:
    """Analyzes simulation results and calculates retirement statistics."""
    
    def __init__(self, confidence_threshold: float = 0.99):
        """
        Initialize the results analyzer.
        
        Args:
            confidence_threshold: Success rate threshold (default: 99%)
        """
        self.confidence_threshold = confidence_threshold
        
    def analyze_simulation_results(self, user_input: UserInput,
                                 portfolio_results: Dict[str, SimulationResult]) -> RetirementResults:
        """
        Analyze simulation results for all portfolios.
        
        Args:
            user_input: User input parameters
            portfolio_results: Dictionary of simulation results by portfolio
            
        Returns:
            Complete retirement analysis results
        """
        # Update confidence threshold to match user's target
        self.confidence_threshold = user_input.target_success_rate
        
        # Convert to list format
        results_list = list(portfolio_results.values())
        
        # Find recommended portfolio
        recommended_portfolio = self._find_recommended_portfolio(portfolio_results)
        recommended_age = self._find_recommended_retirement_age(portfolio_results)
        
        # Calculate percentile data
        percentile_data = self._calculate_percentile_data(portfolio_results)
        
        return RetirementResults(
            user_input=user_input,
            portfolio_results=results_list,
            recommended_portfolio=recommended_portfolio,
            recommended_retirement_age=recommended_age,
            percentile_data=percentile_data
        )
    
    def _find_recommended_portfolio(self, portfolio_results: Dict[str, SimulationResult]) -> PortfolioAllocation:
        """
        Find the recommended portfolio allocation.
        
        Args:
            portfolio_results: Dictionary of simulation results
            
        Returns:
            Recommended portfolio allocation
        """
        best_portfolio = None
        earliest_retirement_age = float('inf')
        
        for name, result in portfolio_results.items():
            if (result.success_rate >= self.confidence_threshold and 
                result.retirement_age < earliest_retirement_age):
                earliest_retirement_age = result.retirement_age
                best_portfolio = result.portfolio_allocation
        
        # If no portfolio meets confidence threshold, return highest success rate
        if best_portfolio is None:
            best_result = max(portfolio_results.values(), key=lambda x: x.success_rate)
            best_portfolio = best_result.portfolio_allocation
        
        return best_portfolio
    
    def _find_recommended_retirement_age(self, portfolio_results: Dict[str, SimulationResult]) -> int:
        """
        Find the recommended retirement age.
        
        Args:
            portfolio_results: Dictionary of simulation results
            
        Returns:
            Recommended retirement age
        """
        earliest_age = float('inf')
        
        for result in portfolio_results.values():
            if (result.success_rate >= self.confidence_threshold and 
                result.retirement_age < earliest_age):
                earliest_age = result.retirement_age
        
        return int(earliest_age) if earliest_age != float('inf') else 95
    
    def _calculate_percentile_data(self, portfolio_results: Dict[str, SimulationResult]) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Calculate percentile data for visualization.
        
        Args:
            portfolio_results: Dictionary of simulation results
            
        Returns:
            Dictionary with percentile data by portfolio
        """
        percentile_data = {}
        
        for name, result in portfolio_results.items():
            # Use actual percentile data from simulation if available
            if hasattr(result, 'percentile_data') and result.percentile_data:
                percentile_data[name] = result.percentile_data
            else:
                # Fallback to synthetic data if percentile data not available
                portfolio_values = result.portfolio_values
                percentile_data[name] = {
                    "10th": portfolio_values * 0.6,  # Conservative estimate
                    "50th": portfolio_values,        # Average values
                    "90th": portfolio_values * 1.4   # Optimistic estimate
                }
        
        return percentile_data
    
    def calculate_success_rate(self, successful_scenarios: int, total_scenarios: int) -> float:
        """
        Calculate success rate from simulation results.
        
        Args:
            successful_scenarios: Number of successful scenarios
            total_scenarios: Total number of scenarios
            
        Returns:
            Success rate as decimal (0.0 to 1.0)
        """
        if total_scenarios == 0:
            return 0.0
        return successful_scenarios / total_scenarios
    
    def calculate_percentiles(self, values: np.ndarray, 
                            percentiles: List[float] = [10, 50, 90]) -> Dict[str, float]:
        """
        Calculate percentiles for a set of values.
        
        Args:
            values: Array of values
            percentiles: List of percentiles to calculate
            
        Returns:
            Dictionary mapping percentile names to values
        """
        if len(values) == 0:
            return {}
        
        result = {}
        for percentile in percentiles:
            result[f"{percentile}th"] = np.percentile(values, percentile)
        
        return result
    
    def calculate_failure_analysis(self, portfolio_results: Dict[str, SimulationResult]) -> Dict[str, Dict[str, float]]:
        """
        Analyze reasons for retirement plan failures.
        
        Args:
            portfolio_results: Dictionary of simulation results
            
        Returns:
            Dictionary with failure analysis by portfolio
        """
        failure_analysis = {}
        
        for name, result in portfolio_results.items():
            failure_rate = 1.0 - result.success_rate
            
            analysis = {
                'failure_rate': failure_rate,
                'success_rate': result.success_rate,
                'retirement_age': result.retirement_age,
                'meets_confidence_threshold': result.success_rate >= self.confidence_threshold,
                'final_portfolio_value': result.final_portfolio_value
            }
            
            failure_analysis[name] = analysis
        
        return failure_analysis
    
    def compare_portfolios(self, portfolio_results: Dict[str, SimulationResult]) -> Dict[str, float]:
        """
        Compare different portfolio allocations.
        
        Args:
            portfolio_results: Dictionary of simulation results
            
        Returns:
            Dictionary with comparison metrics
        """
        if not portfolio_results:
            return {}
        
        success_rates = [result.success_rate for result in portfolio_results.values()]
        retirement_ages = [result.retirement_age for result in portfolio_results.values()]
        final_values = [result.final_portfolio_value for result in portfolio_results.values()]
        
        comparison = {
            'best_success_rate': max(success_rates),
            'worst_success_rate': min(success_rates),
            'earliest_retirement_age': min(retirement_ages),
            'latest_retirement_age': max(retirement_ages),
            'highest_final_value': max(final_values),
            'lowest_final_value': min(final_values),
            'average_success_rate': np.mean(success_rates),
            'average_retirement_age': np.mean(retirement_ages)
        }
        
        return comparison
    
    def calculate_retirement_readiness_score(self, user_input: UserInput,
                                           recommended_result: SimulationResult) -> float:
        """
        Calculate a retirement readiness score (0-100).
        
        Args:
            user_input: User input parameters
            recommended_result: Recommended portfolio simulation result
            
        Returns:
            Retirement readiness score (0-100)
        """
        # Base score from success rate
        base_score = recommended_result.success_rate * 100
        
        # Adjust for retirement age
        years_to_retirement = recommended_result.retirement_age - user_input.current_age
        if years_to_retirement > 30:
            age_penalty = 10  # Retiring too late
        elif years_to_retirement < 10:
            age_penalty = 5   # Retiring very early (risky)
        else:
            age_penalty = 0
        
        # Adjust for savings rate
        annual_savings = user_input.monthly_savings * 12
        savings_rate = annual_savings / user_input.desired_annual_income
        
        if savings_rate > 0.2:  # Saving >20% of desired income
            savings_bonus = 5
        elif savings_rate < 0.1:  # Saving <10% of desired income
            savings_bonus = -10
        else:
            savings_bonus = 0
        
        final_score = max(0, min(100, base_score - age_penalty + savings_bonus))
        return final_score
    
    def generate_improvement_suggestions(self, user_input: UserInput,
                                       portfolio_results: Dict[str, SimulationResult]) -> List[str]:
        """
        Generate suggestions for improving retirement outcomes.
        
        Args:
            user_input: User input parameters
            portfolio_results: Dictionary of simulation results
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Find best result
        best_result = max(portfolio_results.values(), key=lambda x: x.success_rate)
        
        # Check if any portfolio meets confidence threshold
        meets_threshold = any(result.success_rate >= self.confidence_threshold 
                            for result in portfolio_results.values())
        
        if not meets_threshold:
            # Suggest increasing savings
            current_monthly = user_input.monthly_savings
            suggested_increase = current_monthly * 0.2  # 20% increase
            suggestions.append(f"Consider increasing monthly savings by £{suggested_increase:.0f} to improve retirement prospects")
            
            # Suggest reducing desired income
            current_desired = user_input.desired_annual_income
            suggested_reduction = current_desired * 0.1  # 10% reduction
            suggestions.append(f"Consider reducing desired retirement income by £{suggested_reduction:.0f} annually")
            
            # Suggest working longer
            suggestions.append("Consider working 2-3 additional years to significantly improve success rate")
        
        # Portfolio allocation suggestions
        equity_heavy_portfolios = [name for name, result in portfolio_results.items() 
                                 if result.portfolio_allocation.equity_percentage > 0.5]
        
        if equity_heavy_portfolios:
            best_equity_portfolio = max(
                [(name, result) for name, result in portfolio_results.items() 
                 if name in equity_heavy_portfolios],
                key=lambda x: x[1].success_rate
            )
            suggestions.append(f"Consider the {best_equity_portfolio[0]} allocation for potentially better long-term returns")
        
        # Age-specific suggestions
        if user_input.current_age < 40:
            suggestions.append("Take advantage of your young age by considering more aggressive allocations")
        elif user_input.current_age > 55:
            suggestions.append("Consider more conservative allocations as you approach retirement")
        
        return suggestions
    
    def validate_results(self, results: RetirementResults) -> bool:
        """
        Validate retirement results for consistency.
        
        Args:
            results: Retirement results to validate
            
        Returns:
            True if results are valid, False otherwise
        """
        try:
            # Check basic structure
            if not results.portfolio_results:
                return False
            
            # Check success rates are valid
            for result in results.portfolio_results:
                if not (0 <= result.success_rate <= 1):
                    return False
                if result.retirement_age < 18 or result.retirement_age > 100:
                    return False
            
            # Check recommended values
            if results.recommended_retirement_age < 18 or results.recommended_retirement_age > 100:
                return False
            
            return True
            
        except Exception:
            return False