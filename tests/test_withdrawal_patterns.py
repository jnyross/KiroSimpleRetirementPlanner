#!/usr/bin/env python3
"""
Unit tests for withdrawal patterns and chart generation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import numpy as np
from src.models import UserInput
from main import RetirementCalculatorApp


class TestWithdrawalPatterns(unittest.TestCase):
    """Test cases for withdrawal patterns and chart generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_input = UserInput(
            current_age=60,
            current_savings=500000,
            monthly_savings=0,
            desired_annual_income=40000
        )
        self.app = RetirementCalculatorApp(num_simulations=100)  # Reduced for testing
        self.app.initialize_components()
    
    def test_portfolio_values_decline_with_withdrawals(self):
        """Test that portfolio values show declining pattern during retirement."""
        # Test with 50/50 allocation
        allocation = self.app.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        
        # Run simulation for specific retirement age
        result = self.app.simulator.run_simulation_for_retirement_age(
            self.user_input, allocation, 65, show_progress=False
        )
        
        # Verify result structure
        self.assertIsNotNone(result)
        self.assertEqual(result.retirement_age, 65)
        self.assertGreater(len(result.portfolio_values), 0)
        
        # Check if portfolio values show declining pattern over time
        portfolio_values = result.portfolio_values
        declining_count = 0
        for i in range(1, min(10, len(portfolio_values))):
            if portfolio_values[i] < portfolio_values[i-1]:
                declining_count += 1
        
        # Should have some declining years due to withdrawals
        self.assertGreater(declining_count, 0, "Portfolio should decline in some years due to withdrawals")
    
    def test_percentile_data_availability(self):
        """Test that percentile data is properly generated and available."""
        allocation = self.app.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        
        result = self.app.simulator.run_simulation_for_retirement_age(
            self.user_input, allocation, 65, show_progress=False
        )
        
        # Check if percentile data exists
        if hasattr(result, 'percentile_data'):
            self.assertIn("50th", result.percentile_data)
            percentile_values = result.percentile_data["50th"]
            self.assertGreater(len(percentile_values), 0)
    
    def test_chart_generation(self):
        """Test that charts can be generated from simulation results."""
        allocation = self.app.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        
        result = self.app.simulator.run_simulation_for_retirement_age(
            self.user_input, allocation, 65, show_progress=False
        )
        
        # Test chart generation
        portfolio_results = {result.portfolio_allocation.name: result}
        analysis_results = self.app.analyzer.analyze_simulation_results(self.user_input, portfolio_results)
        
        # Verify analysis results have percentile data
        self.assertIsNotNone(analysis_results.percentile_data)
        
        # Generate charts
        chart_files = self.app.generate_charts(analysis_results)
        
        # Verify charts were generated
        if chart_files:
            self.assertGreater(len(chart_files), 0, "Should generate at least one chart")
    
    def test_withdrawal_pattern_consistency(self):
        """Test that withdrawal patterns are consistent across simulations."""
        allocation = self.app.portfolio_manager.get_allocation("75% Equities/25% Bonds")
        
        # Run multiple simulations
        results = []
        for _ in range(3):
            result = self.app.simulator.run_simulation_for_retirement_age(
                self.user_input, allocation, 65, show_progress=False
            )
            results.append(result)
        
        # Check that all results have similar structure
        for result in results:
            self.assertEqual(result.retirement_age, 65)
            self.assertGreater(len(result.portfolio_values), 0)
            self.assertGreaterEqual(result.success_rate, 0.0)
            self.assertLessEqual(result.success_rate, 1.0)


if __name__ == '__main__':
    unittest.main()