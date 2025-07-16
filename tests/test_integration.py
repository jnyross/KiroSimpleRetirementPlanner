#!/usr/bin/env python3
"""
Integration tests for the retirement calculator.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import numpy as np
from src.models import UserInput
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager
from src.tax_calculator import UKTaxCalculator
from src.guard_rails import GuardRailsEngine
from src.simulator import MonteCarloSimulator
from src.analyzer import ResultsAnalyzer


class TestIntegration(unittest.TestCase):
    """Integration test cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_input = UserInput(
            current_age=35,
            current_savings=50000,
            monthly_savings=1000,
            desired_annual_income=30000
        )
        
        # Initialize components
        self.data_manager = HistoricalDataManager()
        self.data_manager.load_all_data()
        
        self.portfolio_manager = PortfolioManager(self.data_manager)
        self.tax_calculator = UKTaxCalculator()
        self.guard_rails_engine = GuardRailsEngine()
        
        self.simulator = MonteCarloSimulator(
            self.data_manager,
            self.portfolio_manager,
            self.tax_calculator,
            self.guard_rails_engine,
            num_simulations=50  # Reduced for testing
        )
        
        self.analyzer = ResultsAnalyzer()
    
    def test_data_loading(self):
        """Test data loading and validation."""
        self.assertTrue(self.data_manager.validate_data())
        self.assertIsNotNone(self.data_manager.equity_returns)
        self.assertIsNotNone(self.data_manager.bond_returns)
        self.assertIsNotNone(self.data_manager.inflation_rates)
    
    def test_portfolio_manager_integration(self):
        """Test portfolio manager integration."""
        allocations = self.portfolio_manager.get_all_allocations()
        self.assertEqual(len(allocations), 6)
        
        # Test portfolio statistics
        for name, allocation in allocations.items():
            stats = self.portfolio_manager.get_portfolio_statistics(allocation)
            self.assertIn('expected_return', stats)
            self.assertIn('volatility', stats)
    
    def test_simulation_integration(self):
        """Test Monte Carlo simulation integration."""
        # Test parameter validation
        self.assertTrue(self.simulator.validate_simulation_parameters(self.user_input))
        
        # Test single simulation
        allocation = self.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        success, final_value, portfolio_values = self.simulator.run_single_simulation(
            self.user_input, allocation, 65
        )
        
        self.assertIsInstance(success, (bool, np.bool_))
        self.assertIsInstance(final_value, float)
        self.assertIsInstance(portfolio_values, np.ndarray)
    
    def test_comprehensive_simulation(self):
        """Test comprehensive simulation across all portfolios."""
        results = self.simulator.run_comprehensive_simulation(self.user_input)
        
        self.assertEqual(len(results), 6)  # 6 portfolio allocations
        
        for name, result in results.items():
            self.assertIsInstance(result.success_rate, float)
            self.assertGreaterEqual(result.success_rate, 0.0)
            self.assertLessEqual(result.success_rate, 1.0)
            self.assertGreaterEqual(result.retirement_age, self.user_input.current_age)
    
    def test_results_analysis(self):
        """Test results analysis integration."""
        portfolio_results = self.simulator.run_comprehensive_simulation(self.user_input)
        results = self.analyzer.analyze_simulation_results(self.user_input, portfolio_results)
        
        self.assertTrue(self.analyzer.validate_results(results))
        self.assertIsNotNone(results.recommended_portfolio)
        self.assertGreaterEqual(results.recommended_retirement_age, self.user_input.current_age)
    
    def test_tax_integration(self):
        """Test tax calculator integration."""
        # Test that tax calculations work with realistic retirement incomes
        test_incomes = [20000, 30000, 40000, 50000]
        
        for income in test_incomes:
            tax = self.tax_calculator.calculate_tax(income)
            net = self.tax_calculator.calculate_net_income(income)
            gross_needed = self.tax_calculator.calculate_gross_needed(net)
            
            self.assertGreaterEqual(tax, 0)
            self.assertLessEqual(net, income)
            self.assertAlmostEqual(gross_needed, income, places=-1)  # Within £10
    
    def test_guard_rails_integration(self):
        """Test guard rails integration with simulation."""
        allocation = self.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        
        # Test that guard rails work with realistic portfolio values
        portfolio_values = np.array([100000, 90000, 80000, 70000, 85000, 90000])
        initial_value = 100000
        base_withdrawal = 4000
        
        withdrawals, reasons = self.guard_rails_engine.simulate_withdrawal_sequence(
            portfolio_values, initial_value, base_withdrawal
        )
        
        self.assertEqual(len(withdrawals), len(portfolio_values))
        self.assertTrue(any(w < base_withdrawal for w in withdrawals))  # Some reductions occurred
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # This tests the entire workflow from input to results
        try:
            # Run comprehensive simulation
            portfolio_results = self.simulator.run_comprehensive_simulation(self.user_input)
            
            # Analyze results
            results = self.analyzer.analyze_simulation_results(self.user_input, portfolio_results)
            
            # Validate results
            self.assertTrue(self.analyzer.validate_results(results))
            
            # Check that we have meaningful results
            self.assertGreater(len(results.portfolio_results), 0)
            self.assertIsNotNone(results.recommended_portfolio)
            
            # Check improvement suggestions
            suggestions = self.analyzer.generate_improvement_suggestions(
                self.user_input, portfolio_results
            )
            self.assertIsInstance(suggestions, list)
            
            # Check readiness score
            recommended_result = None
            for result in results.portfolio_results:
                if result.portfolio_allocation.name == results.recommended_portfolio.name:
                    recommended_result = result
                    break
            
            if recommended_result:
                score = self.analyzer.calculate_retirement_readiness_score(
                    self.user_input, recommended_result
                )
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)
            
        except Exception as e:
            self.fail(f"End-to-end workflow failed: {e}")


if __name__ == '__main__':
    unittest.main()