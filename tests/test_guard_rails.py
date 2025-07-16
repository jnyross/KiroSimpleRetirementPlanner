#!/usr/bin/env python3
"""
Unit tests for guard rails system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import numpy as np
from src.guard_rails import GuardRailsEngine
from src.models import GuardRailsThresholds


class TestGuardRailsEngine(unittest.TestCase):
    """Test cases for guard rails engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.guard_rails = GuardRailsEngine()
        self.initial_value = 100000
        self.base_withdrawal = 4000
    
    def test_normal_spending(self):
        """Test normal spending scenarios."""
        # Portfolio at initial value
        withdrawal, reason = self.guard_rails.calculate_withdrawal_adjustment(
            self.initial_value, self.initial_value, self.base_withdrawal
        )
        self.assertEqual(withdrawal, self.base_withdrawal)
        self.assertEqual(reason, "normal")
        
        # Portfolio slightly above initial value
        withdrawal, reason = self.guard_rails.calculate_withdrawal_adjustment(
            self.initial_value * 1.1, self.initial_value, self.base_withdrawal
        )
        self.assertEqual(withdrawal, self.base_withdrawal)
        self.assertEqual(reason, "normal")
    
    def test_lower_guard_rail(self):
        """Test lower guard rail adjustments."""
        # Portfolio 20% below initial value
        current_value = self.initial_value * 0.8
        withdrawal, reason = self.guard_rails.calculate_withdrawal_adjustment(
            current_value, self.initial_value, self.base_withdrawal
        )
        expected = self.base_withdrawal * 0.9  # 10% reduction
        self.assertAlmostEqual(withdrawal, expected, places=2)
        self.assertEqual(reason, "lower_reduction")
    
    def test_severe_guard_rail(self):
        """Test severe guard rail adjustments."""
        # Portfolio 30% below initial value
        current_value = self.initial_value * 0.7
        withdrawal, reason = self.guard_rails.calculate_withdrawal_adjustment(
            current_value, self.initial_value, self.base_withdrawal
        )
        expected = self.base_withdrawal * 0.8  # 20% reduction
        self.assertAlmostEqual(withdrawal, expected, places=2)
        self.assertEqual(reason, "severe_reduction")
    
    def test_upper_guard_rail(self):
        """Test upper guard rail scenarios."""
        # Portfolio 25% above initial value
        current_value = self.initial_value * 1.25
        withdrawal, reason = self.guard_rails.calculate_withdrawal_adjustment(
            current_value, self.initial_value, self.base_withdrawal
        )
        self.assertEqual(withdrawal, self.base_withdrawal)
        self.assertEqual(reason, "normal")
    
    def test_withdrawal_sequence(self):
        """Test withdrawal sequence simulation."""
        portfolio_values = np.array([100000, 90000, 80000, 70000, 85000])
        withdrawals, reasons = self.guard_rails.simulate_withdrawal_sequence(
            portfolio_values, self.initial_value, self.base_withdrawal
        )
        
        self.assertEqual(len(withdrawals), len(portfolio_values))
        self.assertEqual(len(reasons), len(portfolio_values))
        
        # Check that severe reductions occur when portfolio is low
        self.assertIn("severe_reduction", reasons)
    
    def test_threshold_validation(self):
        """Test threshold validation."""
        # Valid thresholds
        self.assertTrue(self.guard_rails.validate_thresholds())
        
        # Invalid thresholds
        invalid_thresholds = GuardRailsThresholds(
            upper_threshold=1.5,  # Too high
            lower_threshold=0.15,
            severe_threshold=0.25
        )
        invalid_guard_rails = GuardRailsEngine(invalid_thresholds)
        self.assertFalse(invalid_guard_rails.validate_thresholds())
    
    def test_scenario_testing(self):
        """Test guard rails scenarios."""
        scenarios = self.guard_rails.test_guard_rails_scenarios(
            self.initial_value, self.base_withdrawal
        )
        
        self.assertIn('excellent_performance', scenarios)
        self.assertIn('severe_performance', scenarios)
        
        # Check that severe performance triggers reduction
        severe_withdrawal, severe_reason = scenarios['severe_performance']
        self.assertLess(severe_withdrawal, self.base_withdrawal)
        self.assertEqual(severe_reason, "severe_reduction")


if __name__ == '__main__':
    unittest.main()