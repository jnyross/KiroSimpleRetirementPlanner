#!/usr/bin/env python3
"""
Unit tests for core implementation components.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from src.models import UserInput, PortfolioAllocation, GuardRailsThresholds
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager
from src.tax_calculator import UKTaxCalculator
from src.guard_rails import GuardRailsEngine
from src.simulator import MonteCarloSimulator


class TestDataManager(unittest.TestCase):
    """Test cases for HistoricalDataManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_manager = HistoricalDataManager()
    
    def test_data_loading(self):
        """Test that historical data loads successfully."""
        self.data_manager.load_all_data()
        
        # Verify data is loaded
        self.assertIsNotNone(self.data_manager.equity_returns)
        self.assertIsNotNone(self.data_manager.bond_returns)
        self.assertIsNotNone(self.data_manager.inflation_rates)
        
        # Verify data validation
        self.assertTrue(self.data_manager.validate_data())
    
    def test_bootstrap_sampling(self):
        """Test bootstrap sampling functionality."""
        self.data_manager.load_all_data()
        
        allocation = PortfolioAllocation("Test", 0.6, 0.4, 0.0)
        returns = self.data_manager.get_bootstrap_returns(allocation, 10)
        
        self.assertEqual(len(returns), 10)
        self.assertTrue(all(isinstance(r, float) for r in returns))


class TestPortfolioManager(unittest.TestCase):
    """Test cases for PortfolioManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_manager = HistoricalDataManager()
        self.data_manager.load_all_data()
        self.portfolio_manager = PortfolioManager(self.data_manager)
    
    def test_portfolio_allocations(self):
        """Test that all portfolio allocations are created correctly."""
        allocations = self.portfolio_manager.get_all_allocations()
        
        # Should have 6 allocations
        self.assertEqual(len(allocations), 6)
        
        # Check specific allocations exist
        self.assertIn("100% Cash", allocations)
        self.assertIn("100% Bonds", allocations)
        self.assertIn("50% Equities/50% Bonds", allocations)
        self.assertIn("100% Equities", allocations)
    
    def test_portfolio_statistics(self):
        """Test portfolio statistics calculation."""
        allocation = self.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        stats = self.portfolio_manager.get_portfolio_statistics(allocation)
        
        self.assertIn('expected_return', stats)
        self.assertIn('volatility', stats)
        self.assertIsInstance(stats['expected_return'], float)
        self.assertIsInstance(stats['volatility'], float)


class TestSimulator(unittest.TestCase):
    """Test cases for MonteCarloSimulator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_manager = HistoricalDataManager()
        self.data_manager.load_all_data()
        
        self.portfolio_manager = PortfolioManager(self.data_manager)
        self.tax_calculator = UKTaxCalculator()
        self.guard_rails = GuardRailsEngine()
        
        self.simulator = MonteCarloSimulator(
            self.data_manager, self.portfolio_manager, self.tax_calculator, 
            self.guard_rails, num_simulations=50  # Reduced for testing
        )
        
        self.user_input = UserInput(
            current_age=35,
            current_savings=50000,
            monthly_savings=1000,
            desired_annual_income=30000
        )
    
    def test_single_simulation(self):
        """Test single simulation execution."""
        allocation = self.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        
        success, final_value, portfolio_values = self.simulator.run_single_simulation(
            self.user_input, allocation, 60
        )
        
        self.assertIsInstance(success, (bool, type(True)))
        self.assertIsInstance(final_value, float)
        self.assertGreater(len(portfolio_values), 0)
    
    def test_simulation_for_retirement_age(self):
        """Test simulation for specific retirement age."""
        allocation = self.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        
        result = self.simulator.run_simulation_for_retirement_age(
            self.user_input, allocation, 60
        )
        
        self.assertEqual(result.retirement_age, 60)
        self.assertGreaterEqual(result.success_rate, 0.0)
        self.assertLessEqual(result.success_rate, 1.0)
        self.assertGreater(len(result.portfolio_values), 0)
    
    def test_parameter_validation(self):
        """Test simulation parameter validation."""
        # Valid parameters
        self.assertTrue(self.simulator.validate_simulation_parameters(self.user_input))
        
        # Invalid parameters - should raise ValueError during UserInput creation
        with self.assertRaises(ValueError):
            invalid_input = UserInput(
                current_age=-5,  # Invalid age
                current_savings=50000,
                monthly_savings=1000,
                desired_annual_income=30000
            )


if __name__ == '__main__':
    unittest.main()