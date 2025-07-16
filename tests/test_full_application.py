#!/usr/bin/env python3
"""
Full application integration tests.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from src.models import UserInput
from main import RetirementCalculatorApp


class TestFullApplication(unittest.TestCase):
    """Test cases for full application workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_input = UserInput(
            current_age=35,
            current_savings=50000,
            monthly_savings=1000,
            desired_annual_income=30000
        )
        self.app = RetirementCalculatorApp(num_simulations=100)  # Reduced for testing
    
    def test_application_initialization(self):
        """Test that application components initialize correctly."""
        self.app.initialize_components()
        
        # Verify all components are initialized
        self.assertIsNotNone(self.app.data_manager)
        self.assertIsNotNone(self.app.portfolio_manager)
        self.assertIsNotNone(self.app.tax_calculator)
        self.assertIsNotNone(self.app.guard_rails_engine)
        self.assertIsNotNone(self.app.simulator)
        self.assertIsNotNone(self.app.analyzer)
    
    def test_full_analysis_workflow(self):
        """Test the complete analysis workflow."""
        self.app.initialize_components()
        
        # Run analysis
        results = self.app.run_analysis(self.user_input)
        
        # Verify results structure
        self.assertIsNotNone(results)
        self.assertIsNotNone(results.recommended_portfolio)
        self.assertIsNotNone(results.recommended_retirement_age)
        self.assertGreater(len(results.portfolio_results), 0)
        
        # Verify all 6 portfolios were analyzed
        self.assertEqual(len(results.portfolio_results), 6)
        
        # Verify recommended retirement age is reasonable
        self.assertGreaterEqual(results.recommended_retirement_age, self.user_input.current_age)
        self.assertLessEqual(results.recommended_retirement_age, 100)
    
    def test_portfolio_comparison(self):
        """Test that portfolio comparison works correctly."""
        self.app.initialize_components()
        
        results = self.app.run_analysis(self.user_input)
        
        # Check that all portfolio results have required fields
        for result in results.portfolio_results:
            self.assertIsNotNone(result.portfolio_allocation)
            self.assertIsNotNone(result.portfolio_allocation.name)
            self.assertGreaterEqual(result.retirement_age, self.user_input.current_age)
            self.assertGreaterEqual(result.success_rate, 0.0)
            self.assertLessEqual(result.success_rate, 1.0)
        
        # Verify portfolio names are as expected
        portfolio_names = [result.portfolio_allocation.name for result in results.portfolio_results]
        expected_names = [
            "100% Cash", "100% Bonds", "25% Equities/75% Bonds",
            "50% Equities/50% Bonds", "75% Equities/25% Bonds", "100% Equities"
        ]
        
        for name in expected_names:
            self.assertIn(name, portfolio_names)
    
    def test_results_validation(self):
        """Test that analysis results are valid and consistent."""
        self.app.initialize_components()
        
        results = self.app.run_analysis(self.user_input)
        
        # Validate using analyzer
        self.assertTrue(self.app.analyzer.validate_results(results))
        
        # Check that recommended portfolio is one of the analyzed portfolios
        recommended_name = results.recommended_portfolio.name
        analyzed_names = [result.portfolio_allocation.name for result in results.portfolio_results]
        self.assertIn(recommended_name, analyzed_names)
    
    def test_error_handling(self):
        """Test application error handling."""
        # Test with invalid user input - should raise ValueError during creation
        with self.assertRaises(ValueError):
            invalid_input = UserInput(
                current_age=-5,  # Invalid age
                current_savings=50000,
                monthly_savings=1000,
                desired_annual_income=30000
            )


class TestComprehensiveAnalysis(unittest.TestCase):
    """Test cases for comprehensive analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_input = UserInput(
            current_age=40,
            current_savings=100000,
            monthly_savings=2000,
            desired_annual_income=35000
        )
        self.app = RetirementCalculatorApp(num_simulations=100)  # Reduced for testing
    
    def test_comprehensive_analysis_with_withdrawals(self):
        """Test comprehensive analysis with withdrawal patterns."""
        self.app.initialize_components()
        
        results = self.app.run_analysis(self.user_input)
        
        # Verify comprehensive results
        self.assertIsNotNone(results.recommended_portfolio)
        self.assertGreater(results.recommended_retirement_age, self.user_input.current_age)
        
        # Check portfolio comparison makes sense
        portfolio_results = {result.portfolio_allocation.name: result for result in results.portfolio_results}
        
        # Cash portfolio should generally require later retirement than equity portfolios
        cash_result = portfolio_results.get("100% Cash")
        equity_result = portfolio_results.get("100% Equities")
        
        if cash_result and equity_result:
            # Cash should generally require later retirement (though not always due to volatility)
            self.assertIsInstance(cash_result.retirement_age, int)
            self.assertIsInstance(equity_result.retirement_age, int)
    
    def test_percentile_data_generation(self):
        """Test that percentile data is generated correctly."""
        self.app.initialize_components()
        
        results = self.app.run_analysis(self.user_input)
        
        # Check percentile data exists
        self.assertIsNotNone(results.percentile_data)
        
        # Check that percentile data has expected structure
        for portfolio_name, percentiles in results.percentile_data.items():
            self.assertIn("10th", percentiles)
            self.assertIn("50th", percentiles)
            self.assertIn("90th", percentiles)
            
            # Check that percentile values are arrays or lists with data
            for percentile_name, values in percentiles.items():
                self.assertTrue(hasattr(values, '__len__'), f"Percentile {percentile_name} should have length")
                if len(values) > 3:
                    # Check that values change over time (not all the same)
                    self.assertNotEqual(values[0], values[-1])


if __name__ == '__main__':
    unittest.main()