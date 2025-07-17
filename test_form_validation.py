#!/usr/bin/env python3
"""
Unit tests for the form validation system.

Tests both server-side WTForms validation and integration with UserInput model.
"""

import unittest
from forms import CalculatorForm
from src.models import UserInput


class TestFormValidation(unittest.TestCase):
    """Test cases for the CalculatorForm validation system."""
    
    def test_valid_form_data(self):
        """Test that valid form data passes validation."""
        valid_data = {
            'current_age': 35,
            'current_savings': 50000,
            'monthly_savings': 1200,
            'desired_annual_income': 30000
        }
        
        form = CalculatorForm(data=valid_data)
        self.assertTrue(form.validate())
        
        # Should be able to create UserInput
        user_input = form.to_user_input()
        self.assertIsInstance(user_input, UserInput)
        self.assertEqual(user_input.current_age, 35)
        self.assertEqual(user_input.current_savings, 50000)
    
    def test_zero_values_accepted(self):
        """Test that zero values are accepted for savings fields."""
        zero_data = {
            'current_age': 18,
            'current_savings': 0,
            'monthly_savings': 0,
            'desired_annual_income': 1000
        }
        
        form = CalculatorForm(data=zero_data)
        self.assertTrue(form.validate())
        
        user_input = form.to_user_input()
        self.assertEqual(user_input.current_savings, 0)
        self.assertEqual(user_input.monthly_savings, 0)
    
    def test_age_validation(self):
        """Test age validation boundaries."""
        # Too young
        young_data = {
            'current_age': 17,
            'current_savings': 10000,
            'monthly_savings': 500,
            'desired_annual_income': 20000
        }
        form = CalculatorForm(data=young_data)
        self.assertFalse(form.validate())
        self.assertIn('current_age', form.get_validation_errors())
        
        # Too old
        old_data = {
            'current_age': 81,
            'current_savings': 10000,
            'monthly_savings': 500,
            'desired_annual_income': 20000
        }
        form = CalculatorForm(data=old_data)
        self.assertFalse(form.validate())
        self.assertIn('current_age', form.get_validation_errors())
        
        # Valid boundaries
        for age in [18, 80]:
            valid_data = {
                'current_age': age,
                'current_savings': 10000,
                'monthly_savings': 500,
                'desired_annual_income': 20000
            }
            form = CalculatorForm(data=valid_data)
            self.assertTrue(form.validate(), f"Age {age} should be valid")
    
    def test_negative_values_rejected(self):
        """Test that negative values are rejected."""
        negative_savings_data = {
            'current_age': 30,
            'current_savings': -5000,
            'monthly_savings': 500,
            'desired_annual_income': 20000
        }
        form = CalculatorForm(data=negative_savings_data)
        self.assertFalse(form.validate())
        self.assertIn('current_savings', form.get_validation_errors())
        
        negative_monthly_data = {
            'current_age': 30,
            'current_savings': 10000,
            'monthly_savings': -500,
            'desired_annual_income': 20000
        }
        form = CalculatorForm(data=negative_monthly_data)
        self.assertFalse(form.validate())
        self.assertIn('monthly_savings', form.get_validation_errors())
    
    def test_income_validation(self):
        """Test desired annual income validation."""
        # Too low
        low_income_data = {
            'current_age': 30,
            'current_savings': 10000,
            'monthly_savings': 500,
            'desired_annual_income': 500
        }
        form = CalculatorForm(data=low_income_data)
        self.assertFalse(form.validate())
        self.assertIn('desired_annual_income', form.get_validation_errors())
        
        # Too high
        high_income_data = {
            'current_age': 30,
            'current_savings': 10000,
            'monthly_savings': 500,
            'desired_annual_income': 600000
        }
        form = CalculatorForm(data=high_income_data)
        self.assertFalse(form.validate())
        self.assertIn('desired_annual_income', form.get_validation_errors())
    
    def test_cross_field_validation(self):
        """Test cross-field validation for unrealistic income vs savings."""
        unrealistic_data = {
            'current_age': 25,
            'current_savings': 5000,
            'monthly_savings': 100,  # £1200/year
            'desired_annual_income': 100000  # Way too high for savings rate
        }
        form = CalculatorForm(data=unrealistic_data)
        self.assertFalse(form.validate())
        self.assertIn('desired_annual_income', form.get_validation_errors())
        
        # Realistic ratio should pass
        realistic_data = {
            'current_age': 25,
            'current_savings': 5000,
            'monthly_savings': 1000,  # £12000/year
            'desired_annual_income': 30000  # Reasonable for savings rate
        }
        form = CalculatorForm(data=realistic_data)
        self.assertTrue(form.validate())
    
    def test_missing_required_fields(self):
        """Test that missing required fields are caught."""
        incomplete_data = {
            'current_age': 30,
            # Missing other required fields
        }
        form = CalculatorForm(data=incomplete_data)
        self.assertFalse(form.validate())
        
        errors = form.get_validation_errors()
        self.assertIn('current_savings', errors)
        self.assertIn('monthly_savings', errors)
        self.assertIn('desired_annual_income', errors)
    
    def test_help_text_available(self):
        """Test that help text is available for all fields."""
        form = CalculatorForm()
        help_text = form.get_help_text()
        
        expected_fields = ['current_age', 'current_savings', 'monthly_savings', 'desired_annual_income']
        for field in expected_fields:
            self.assertIn(field, help_text)
            self.assertIsInstance(help_text[field], str)
            self.assertTrue(len(help_text[field]) > 0)
    
    def test_float_values_accepted(self):
        """Test that float values are properly handled."""
        float_data = {
            'current_age': 30,
            'current_savings': 25000.50,
            'monthly_savings': 1250.75,
            'desired_annual_income': 28000.00
        }
        form = CalculatorForm(data=float_data)
        self.assertTrue(form.validate())
        
        user_input = form.to_user_input()
        self.assertEqual(user_input.current_savings, 25000.50)
        self.assertEqual(user_input.monthly_savings, 1250.75)
    
    def test_form_to_user_input_conversion(self):
        """Test that form data is correctly converted to UserInput."""
        form_data = {
            'current_age': 40,
            'current_savings': 75000,
            'monthly_savings': 1500,
            'desired_annual_income': 35000
        }
        
        form = CalculatorForm(data=form_data)
        self.assertTrue(form.validate())
        
        user_input = form.to_user_input()
        
        # Check all fields are correctly mapped
        self.assertEqual(user_input.current_age, 40)
        self.assertEqual(user_input.current_savings, 75000)
        self.assertEqual(user_input.monthly_savings, 1500)
        self.assertEqual(user_input.desired_annual_income, 35000)
        
        # Check default values are set
        self.assertEqual(user_input.target_success_rate, 0.95)
        self.assertEqual(user_input.cash_buffer_years, 2.0)
        self.assertEqual(user_input.state_pension_age, 67)
    
    def test_invalid_form_to_user_input_raises_error(self):
        """Test that invalid form data raises error when converting to UserInput."""
        invalid_data = {
            'current_age': 17,  # Invalid age
            'current_savings': 10000,
            'monthly_savings': 500,
            'desired_annual_income': 20000
        }
        
        form = CalculatorForm(data=invalid_data)
        self.assertFalse(form.validate())
        
        with self.assertRaises(ValueError):
            form.to_user_input()


if __name__ == '__main__':
    unittest.main()