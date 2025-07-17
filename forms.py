"""
Form handling and validation for the retirement calculator web application.

This module provides WTForms-based form validation for user inputs,
ensuring data integrity before processing calculations.
"""

from wtforms import Form, IntegerField, FloatField, validators
from wtforms.validators import ValidationError, Optional
from src.models import UserInput


def NumberRequired(message=None):
    """
    Custom validator that requires a number (including 0) but not None or empty string.
    """
    def _number_required(form, field):
        if field.data is None or field.data == '':
            if message is None:
                message_text = f"{field.label.text} is required"
            else:
                message_text = message
            raise ValidationError(message_text)
    return _number_required


class CalculatorForm(Form):
    """
    Web form for retirement calculator inputs with comprehensive validation.
    
    Validates user financial information including age, savings, and income
    requirements with appropriate ranges and error messages.
    """
    
    current_age = IntegerField(
        'Current Age',
        [
            validators.DataRequired(message="Current age is required"),
            validators.NumberRange(
                min=18, 
                max=80, 
                message="Age must be between 18 and 80 years"
            )
        ],
        description="Your current age (18-80 years)"
    )
    
    current_savings = FloatField(
        'Current Savings (£)',
        [
            NumberRequired(message="Current savings amount is required"),
            validators.NumberRange(
                min=0, 
                message="Current savings cannot be negative"
            )
        ],
        description="Total retirement savings you have now (£0 or more)"
    )
    
    monthly_savings = FloatField(
        'Monthly Savings (£)',
        [
            NumberRequired(message="Monthly savings amount is required"),
            validators.NumberRange(
                min=0, 
                message="Monthly savings cannot be negative"
            )
        ],
        description="How much you save each month for retirement (£0 or more)"
    )
    
    desired_annual_income = FloatField(
        'Desired Annual Income (£)',
        [
            validators.DataRequired(message="Desired annual income is required"),
            validators.NumberRange(
                min=1000, 
                max=500000,
                message="Annual income must be between £1,000 and £500,000"
            )
        ],
        description="After-tax income you want in retirement (today's purchasing power)"
    )
    
    def validate_monthly_savings(self, field):
        """
        Custom validation to ensure monthly savings are reasonable.
        
        Args:
            field: The monthly_savings field being validated
            
        Raises:
            ValidationError: If monthly savings exceed reasonable limits
        """
        if field.data and field.data > 50000:
            raise ValidationError("Monthly savings seem unusually high. Please verify the amount.")
    
    def validate_current_savings(self, field):
        """
        Custom validation to ensure current savings are reasonable.
        
        Args:
            field: The current_savings field being validated
            
        Raises:
            ValidationError: If current savings exceed reasonable limits
        """
        if field.data and field.data > 10000000:
            raise ValidationError("Current savings seem unusually high. Please verify the amount.")
    
    def validate_desired_annual_income(self, field):
        """
        Custom validation for desired annual income reasonableness.
        
        Args:
            field: The desired_annual_income field being validated
            
        Raises:
            ValidationError: If income requirements seem unrealistic
        """
        if field.data and self.monthly_savings.data:
            annual_savings = self.monthly_savings.data * 12
            if field.data > annual_savings * 50:
                raise ValidationError(
                    "Desired income seems very high compared to your savings rate. "
                    "Consider adjusting either your income goal or savings amount."
                )
    
    def to_user_input(self):
        """
        Convert validated form data to UserInput model.
        
        Returns:
            UserInput: Validated user input ready for calculation
            
        Raises:
            ValueError: If form data is invalid or incomplete
        """
        if not self.validate():
            raise ValueError("Form validation failed")
        
        return UserInput(
            current_age=self.current_age.data,
            current_savings=self.current_savings.data,
            monthly_savings=self.monthly_savings.data,
            desired_annual_income=self.desired_annual_income.data
        )
    
    def get_validation_errors(self):
        """
        Get all validation errors in a structured format for JSON responses.
        
        Returns:
            dict: Dictionary of field names to error messages
        """
        errors = {}
        for field_name, field in self._fields.items():
            if field.errors:
                errors[field_name] = field.errors
        return errors
    
    def get_help_text(self):
        """
        Get help text for all form fields.
        
        Returns:
            dict: Dictionary of field names to help text
        """
        return {
            'current_age': self.current_age.description,
            'current_savings': self.current_savings.description,
            'monthly_savings': self.monthly_savings.description,
            'desired_annual_income': self.desired_annual_income.description
        }