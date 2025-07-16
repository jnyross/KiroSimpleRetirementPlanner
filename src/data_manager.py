"""
Historical data management system for the retirement calculator.

This module handles loading and validating historical market data from CSV files,
including equity returns, bond returns, and inflation data.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from .models import PortfolioAllocation


class HistoricalDataManager:
    """Manages loading and access to historical market data."""
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the data manager.
        
        Args:
            data_directory: Directory containing CSV data files
        """
        self.data_directory = data_directory
        self.equity_returns: Optional[pd.Series] = None
        self.bond_returns: Optional[pd.Series] = None
        self.inflation_rates: Optional[pd.Series] = None
        self.portfolio_allocations: Optional[Dict[str, PortfolioAllocation]] = None
        
    def load_all_data(self) -> None:
        """Load all historical data files."""
        self.equity_returns = self._load_equity_returns()
        self.bond_returns = self._load_bond_returns()
        self.inflation_rates = self._load_inflation_rates()
        self.portfolio_allocations = self._load_portfolio_allocations()
        
    def _load_equity_returns(self) -> pd.Series:
        """Load UK equity returns data."""
        file_path = os.path.join(self.data_directory, "uk_equity_returns.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Equity returns file not found: {file_path}")
            
        try:
            df = pd.read_csv(file_path)
            if 'year' not in df.columns or 'return' not in df.columns:
                raise ValueError("Equity returns file must contain 'year' and 'return' columns")
            
            # Load inflation data first if not already loaded
            if self.inflation_rates is None:
                self.inflation_rates = self._load_inflation_rates()
            
            # Convert to real returns (inflation-adjusted) using proper formula
            inflation_rates = self._get_inflation_for_year(df['year'])
            df['real_return'] = (1 + df['return']) / (1 + inflation_rates) - 1
            return df.set_index('year')['real_return']
            
        except Exception as e:
            raise ValueError(f"Error loading equity returns: {str(e)}")
    
    def _load_bond_returns(self) -> pd.Series:
        """Load UK bond returns data."""
        file_path = os.path.join(self.data_directory, "uk_bond_returns.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Bond returns file not found: {file_path}")
            
        try:
            df = pd.read_csv(file_path)
            if 'year' not in df.columns or 'return' not in df.columns:
                raise ValueError("Bond returns file must contain 'year' and 'return' columns")
            
            # Load inflation data first if not already loaded
            if self.inflation_rates is None:
                self.inflation_rates = self._load_inflation_rates()
            
            # Convert to real returns (inflation-adjusted) using proper formula
            inflation_rates = self._get_inflation_for_year(df['year'])
            df['real_return'] = (1 + df['return']) / (1 + inflation_rates) - 1
            return df.set_index('year')['real_return']
            
        except Exception as e:
            raise ValueError(f"Error loading bond returns: {str(e)}")
    
    def _load_inflation_rates(self) -> pd.Series:
        """Load UK inflation rates data."""
        file_path = os.path.join(self.data_directory, "uk_inflation_rates.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Inflation rates file not found: {file_path}")
            
        try:
            df = pd.read_csv(file_path)
            if 'year' not in df.columns or 'inflation_rate' not in df.columns:
                raise ValueError("Inflation file must contain 'year' and 'inflation_rate' columns")
            
            return df.set_index('year')['inflation_rate']
            
        except Exception as e:
            raise ValueError(f"Error loading inflation rates: {str(e)}")
    
    def _load_portfolio_allocations(self) -> Dict[str, PortfolioAllocation]:
        """Load portfolio allocation configurations."""
        allocations = {
            "100% Cash": PortfolioAllocation("100% Cash", 0.0, 0.0, 1.0),
            "100% Bonds": PortfolioAllocation("100% Bonds", 0.0, 1.0, 0.0),
            "25% Equities/75% Bonds": PortfolioAllocation("25% Equities/75% Bonds", 0.25, 0.75, 0.0),
            "50% Equities/50% Bonds": PortfolioAllocation("50% Equities/50% Bonds", 0.50, 0.50, 0.0),
            "75% Equities/25% Bonds": PortfolioAllocation("75% Equities/25% Bonds", 0.75, 0.25, 0.0),
            "100% Equities": PortfolioAllocation("100% Equities", 1.0, 0.0, 0.0)
        }
        return allocations
    
    def _get_inflation_for_year(self, years: pd.Series) -> pd.Series:
        """Get inflation rate for given years."""
        if self.inflation_rates is None:
            # Load inflation data if not already loaded
            self.inflation_rates = self._load_inflation_rates()
        
        # Match years to inflation rates
        return years.map(self.inflation_rates).fillna(0.0)
    
    def get_portfolio_return(self, allocation: PortfolioAllocation, year: int) -> float:
        """
        Calculate portfolio return for a given year and allocation.
        
        Args:
            allocation: Portfolio allocation configuration
            year: Year for which to calculate return
            
        Returns:
            Real (inflation-adjusted) portfolio return
        """
        if self.equity_returns is None or self.bond_returns is None:
            raise ValueError("Historical data not loaded. Call load_all_data() first.")
        
        # Cash returns 0% real return (after inflation)
        cash_return = 0.0
        
        # Get equity and bond returns for the year
        equity_return = self.equity_returns.get(year, 0.0)
        bond_return = self.bond_returns.get(year, 0.0)
        
        # Calculate weighted portfolio return
        portfolio_return = (
            allocation.equity_percentage * equity_return +
            allocation.bond_percentage * bond_return +
            allocation.cash_percentage * cash_return
        )
        
        return portfolio_return
    
    def get_bootstrap_returns(self, allocation: PortfolioAllocation, num_years: int) -> np.ndarray:
        """
        Generate bootstrap sample of portfolio returns.
        
        Args:
            allocation: Portfolio allocation configuration
            num_years: Number of years of returns to generate
            
        Returns:
            Array of bootstrap sampled portfolio returns
        """
        if self.equity_returns is None or self.bond_returns is None:
            raise ValueError("Historical data not loaded. Call load_all_data() first.")
        
        # Get available years
        available_years = list(set(self.equity_returns.index) & set(self.bond_returns.index))
        
        if len(available_years) == 0:
            raise ValueError("No overlapping years found in equity and bond data")
        
        # Bootstrap sample years
        sampled_years = np.random.choice(available_years, size=num_years, replace=True)
        
        # Calculate returns for sampled years
        returns = np.array([self.get_portfolio_return(allocation, year) for year in sampled_years])
        
        return returns
    
    def validate_data(self) -> bool:
        """
        Validate that all required data is loaded and consistent.
        
        Returns:
            True if data is valid, False otherwise
        """
        try:
            if self.equity_returns is None or self.bond_returns is None or self.inflation_rates is None:
                return False
            
            # Check for overlapping years
            equity_years = set(self.equity_returns.index)
            bond_years = set(self.bond_returns.index)
            inflation_years = set(self.inflation_rates.index)
            
            overlapping_years = equity_years & bond_years & inflation_years
            
            if len(overlapping_years) < 10:  # Minimum 10 years of data
                return False
            
            # Check for reasonable return values
            if self.equity_returns.min() < -0.8 or self.equity_returns.max() > 2.0:
                return False
            
            if self.bond_returns.min() < -0.5 or self.bond_returns.max() > 1.0:
                return False
            
            return True
            
        except Exception:
            return False