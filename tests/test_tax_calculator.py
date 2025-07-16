#!/usr/bin/env python3
"""
Unit tests for UK tax calculator.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from src.tax_calculator import UKTaxCalculator


class TestUKTaxCalculator(unittest.TestCase):
    """Test cases for UK tax calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tax_calc = UKTaxCalculator()
    
    def test_personal_allowance(self):
        """Test personal allowance calculations."""
        # Income below personal allowance
        self.assertEqual(self.tax_calc.calculate_tax(10000), 0.0)
        self.assertEqual(self.tax_calc.calculate_tax(12570), 0.0)
    
    def test_basic_rate_tax(self):
        """Test basic rate tax calculations."""
        # Just above personal allowance
        tax = self.tax_calc.calculate_tax(20000)
        expected = (20000 - 12570) * 0.20
        self.assertAlmostEqual(tax, expected, places=2)
        
        # At top of basic rate band
        tax = self.tax_calc.calculate_tax(50270)
        expected = (50270 - 12570) * 0.20
        self.assertAlmostEqual(tax, expected, places=2)
    
    def test_higher_rate_tax(self):
        """Test higher rate tax calculations."""
        # In higher rate band
        tax = self.tax_calc.calculate_tax(60000)
        basic_tax = (50270 - 12570) * 0.20
        higher_tax = (60000 - 50270) * 0.40
        expected = basic_tax + higher_tax
        self.assertAlmostEqual(tax, expected, places=2)
    
    def test_net_income_calculation(self):
        """Test net income calculations."""
        gross = 50000
        tax = self.tax_calc.calculate_tax(gross)
        net = self.tax_calc.calculate_net_income(gross)
        self.assertAlmostEqual(net, gross - tax, places=2)
    
    def test_gross_needed_calculation(self):
        """Test gross income needed calculations."""
        desired_net = 30000
        gross_needed = self.tax_calc.calculate_gross_needed(desired_net)
        actual_net = self.tax_calc.calculate_net_income(gross_needed)
        self.assertAlmostEqual(actual_net, desired_net, places=0)
    
    def test_effective_tax_rate(self):
        """Test effective tax rate calculations."""
        # Test various income levels
        incomes = [20000, 30000, 50000, 100000]
        for income in incomes:
            rate = self.tax_calc.get_effective_tax_rate(income)
            self.assertGreaterEqual(rate, 0.0)
            self.assertLessEqual(rate, 0.45)  # Max rate
    
    def test_validation(self):
        """Test input validation."""
        self.assertTrue(self.tax_calc.validate_income(50000))
        self.assertTrue(self.tax_calc.validate_income(0))
        self.assertFalse(self.tax_calc.validate_income(-1000))


if __name__ == '__main__':
    unittest.main()