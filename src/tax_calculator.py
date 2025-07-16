"""
UK tax calculation engine for retirement withdrawals.

This module handles UK-specific tax calculations including personal allowance,
basic rate, higher rate, and additional rate tax bands.
"""

from typing import List, Tuple
from .models import TaxBracket


class UKTaxCalculator:
    """Calculates UK income tax on retirement withdrawals."""
    
    def __init__(self, tax_year: int = 2024):
        """
        Initialize the UK tax calculator.
        
        Args:
            tax_year: Tax year for which to use tax bands (default: 2024)
        """
        self.tax_year = tax_year
        self.personal_allowance = 12570  # 2024/25 personal allowance
        self.tax_brackets = self._get_tax_brackets()
        
    def _get_tax_brackets(self) -> List[TaxBracket]:
        """
        Get UK tax brackets for the specified tax year.
        
        Returns:
            List of tax brackets with rates and thresholds
        """
        # 2024/25 UK tax brackets
        brackets = [
            TaxBracket(0, self.personal_allowance, 0.0),           # Personal allowance
            TaxBracket(self.personal_allowance, 50270, 0.20),      # Basic rate
            TaxBracket(50270, 125140, 0.40),                      # Higher rate
            TaxBracket(125140, float('inf'), 0.45)                # Additional rate
        ]
        return brackets
    
    def calculate_tax(self, gross_income: float) -> float:
        """
        Calculate UK income tax on gross income.
        
        Args:
            gross_income: Gross annual income
            
        Returns:
            Income tax amount
        """
        if gross_income <= 0:
            return 0.0
            
        total_tax = 0.0
        
        for bracket in self.tax_brackets:
            if gross_income <= bracket.lower_limit:
                break
                
            taxable_in_bracket = min(gross_income, bracket.upper_limit) - bracket.lower_limit
            
            if taxable_in_bracket > 0:
                total_tax += taxable_in_bracket * bracket.rate
                
        return total_tax
    
    def calculate_net_income(self, gross_income: float) -> float:
        """
        Calculate net income after tax.
        
        Args:
            gross_income: Gross annual income
            
        Returns:
            Net income after tax
        """
        tax = self.calculate_tax(gross_income)
        return gross_income - tax
    
    def calculate_gross_needed(self, desired_net_income: float) -> float:
        """
        Calculate gross income needed to achieve desired net income.
        
        Args:
            desired_net_income: Desired net annual income after tax
            
        Returns:
            Gross income needed
        """
        if desired_net_income <= 0:
            return 0.0
            
        # Use binary search to find the required gross income
        low, high = 0.0, desired_net_income * 3.0  # Upper bound estimate
        tolerance = 1.0  # £1 tolerance
        
        while high - low > tolerance:
            mid = (low + high) / 2.0
            net_income = self.calculate_net_income(mid)
            
            if net_income < desired_net_income:
                low = mid
            else:
                high = mid
                
        return high
    
    def get_effective_tax_rate(self, gross_income: float) -> float:
        """
        Calculate effective tax rate for given gross income.
        
        Args:
            gross_income: Gross annual income
            
        Returns:
            Effective tax rate as decimal (e.g., 0.20 for 20%)
        """
        if gross_income <= 0:
            return 0.0
            
        tax = self.calculate_tax(gross_income)
        return tax / gross_income
    
    def get_marginal_tax_rate(self, gross_income: float) -> float:
        """
        Calculate marginal tax rate for given gross income.
        
        Args:
            gross_income: Gross annual income
            
        Returns:
            Marginal tax rate as decimal
        """
        if gross_income <= 0:
            return 0.0
            
        for bracket in self.tax_brackets:
            if bracket.lower_limit <= gross_income < bracket.upper_limit:
                return bracket.rate
                
        # If income is above all brackets, return the highest rate
        return self.tax_brackets[-1].rate
    
    def get_tax_breakdown(self, gross_income: float) -> List[Tuple[str, float, float]]:
        """
        Get detailed breakdown of tax calculation.
        
        Args:
            gross_income: Gross annual income
            
        Returns:
            List of tuples: (bracket_name, taxable_amount, tax_amount)
        """
        if gross_income <= 0:
            return []
            
        breakdown = []
        bracket_names = ["Personal Allowance", "Basic Rate", "Higher Rate", "Additional Rate"]
        
        for i, bracket in enumerate(self.tax_brackets):
            if gross_income <= bracket.lower_limit:
                break
                
            taxable_in_bracket = min(gross_income, bracket.upper_limit) - bracket.lower_limit
            
            if taxable_in_bracket > 0:
                tax_in_bracket = taxable_in_bracket * bracket.rate
                breakdown.append((bracket_names[i], taxable_in_bracket, tax_in_bracket))
                
        return breakdown
    
    def update_tax_year(self, tax_year: int) -> None:
        """
        Update tax year and recalculate tax brackets.
        
        Args:
            tax_year: New tax year
        """
        self.tax_year = tax_year
        
        # Update tax brackets for different years
        if tax_year == 2024:
            self.personal_allowance = 12570
        elif tax_year == 2023:
            self.personal_allowance = 12570
        elif tax_year == 2022:
            self.personal_allowance = 12570
        else:
            # Default to current year values
            self.personal_allowance = 12570
            
        self.tax_brackets = self._get_tax_brackets()
    
    def validate_income(self, income: float) -> bool:
        """
        Validate income value.
        
        Args:
            income: Income value to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(income, (int, float)) and income >= 0 and income < 10_000_000