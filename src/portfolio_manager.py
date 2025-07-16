"""
Portfolio allocation system for the retirement calculator.

This module handles the 6 different portfolio allocations and calculates
portfolio returns based on historical data and allocation percentages.
"""

import numpy as np
from typing import Dict, List
from .models import PortfolioAllocation
from .data_manager import HistoricalDataManager


class PortfolioManager:
    """Manages portfolio allocations and return calculations."""
    
    def __init__(self, data_manager: HistoricalDataManager):
        """
        Initialize the portfolio manager.
        
        Args:
            data_manager: Historical data manager instance
        """
        self.data_manager = data_manager
        self.allocations = self._create_portfolio_allocations()
        
    def _create_portfolio_allocations(self) -> Dict[str, PortfolioAllocation]:
        """
        Create the 6 standard portfolio allocations.
        
        Returns:
            Dictionary mapping portfolio names to allocation objects
        """
        allocations = {
            "100% Cash": PortfolioAllocation("100% Cash", 0.0, 0.0, 1.0),
            "100% Bonds": PortfolioAllocation("100% Bonds", 0.0, 1.0, 0.0),
            "25% Equities/75% Bonds": PortfolioAllocation("25% Equities/75% Bonds", 0.25, 0.75, 0.0),
            "50% Equities/50% Bonds": PortfolioAllocation("50% Equities/50% Bonds", 0.50, 0.50, 0.0),
            "75% Equities/25% Bonds": PortfolioAllocation("75% Equities/25% Bonds", 0.75, 0.25, 0.0),
            "100% Equities": PortfolioAllocation("100% Equities", 1.0, 0.0, 0.0)
        }
        return allocations
    
    def get_allocation(self, name: str) -> PortfolioAllocation:
        """
        Get portfolio allocation by name.
        
        Args:
            name: Portfolio allocation name
            
        Returns:
            Portfolio allocation object
        """
        if name not in self.allocations:
            raise ValueError(f"Unknown portfolio allocation: {name}")
        return self.allocations[name]
    
    def get_all_allocations(self) -> Dict[str, PortfolioAllocation]:
        """
        Get all portfolio allocations.
        
        Returns:
            Dictionary of all portfolio allocations
        """
        return self.allocations.copy()
    
    def calculate_portfolio_return(self, allocation: PortfolioAllocation, 
                                 equity_return: float, bond_return: float) -> float:
        """
        Calculate portfolio return for given asset returns.
        
        Args:
            allocation: Portfolio allocation
            equity_return: Equity return for the period
            bond_return: Bond return for the period
            
        Returns:
            Portfolio return
        """
        # Cash returns 0% real return (after inflation)
        cash_return = 0.0
        
        portfolio_return = (
            allocation.equity_percentage * equity_return +
            allocation.bond_percentage * bond_return +
            allocation.cash_percentage * cash_return
        )
        
        return portfolio_return
    
    def calculate_portfolio_returns_sequence(self, allocation: PortfolioAllocation,
                                           equity_returns: np.ndarray,
                                           bond_returns: np.ndarray) -> np.ndarray:
        """
        Calculate portfolio returns for a sequence of asset returns.
        
        Args:
            allocation: Portfolio allocation
            equity_returns: Array of equity returns
            bond_returns: Array of bond returns
            
        Returns:
            Array of portfolio returns
        """
        if len(equity_returns) != len(bond_returns):
            raise ValueError("Equity and bond returns arrays must have same length")
        
        # Cash returns 0% real return (after inflation)
        cash_returns = np.zeros_like(equity_returns)
        
        portfolio_returns = (
            allocation.equity_percentage * equity_returns +
            allocation.bond_percentage * bond_returns +
            allocation.cash_percentage * cash_returns
        )
        
        return portfolio_returns
    
    def generate_bootstrap_returns(self, allocation: PortfolioAllocation,
                                 num_years: int, num_simulations: int = 1) -> np.ndarray:
        """
        Generate bootstrap samples of portfolio returns.
        
        Args:
            allocation: Portfolio allocation
            num_years: Number of years for each simulation
            num_simulations: Number of simulations to run
            
        Returns:
            Array of shape (num_simulations, num_years) with portfolio returns
        """
        if self.data_manager.equity_returns is None or self.data_manager.bond_returns is None:
            raise ValueError("Historical data not loaded")
        
        # Get available years with both equity and bond data
        equity_years = set(self.data_manager.equity_returns.index)
        bond_years = set(self.data_manager.bond_returns.index)
        available_years = list(equity_years & bond_years)
        
        if len(available_years) < 10:  # Minimum 10 years required for bootstrap sampling
            raise ValueError(f"Insufficient historical data. Need at least 10 years, have {len(available_years)}")
        
        results = np.zeros((num_simulations, num_years))
        
        for sim in range(num_simulations):
            # Bootstrap sample years with replacement
            sampled_years = np.random.choice(available_years, size=num_years, replace=True)
            
            # Get returns for sampled years
            equity_returns = np.array([self.data_manager.equity_returns[year] for year in sampled_years])
            bond_returns = np.array([self.data_manager.bond_returns[year] for year in sampled_years])
            
            # Calculate portfolio returns
            portfolio_returns = self.calculate_portfolio_returns_sequence(allocation, equity_returns, bond_returns)
            results[sim] = portfolio_returns
        
        return results
    
    def calculate_expected_return(self, allocation: PortfolioAllocation) -> float:
        """
        Calculate expected annual return for a portfolio allocation.
        
        Args:
            allocation: Portfolio allocation
            
        Returns:
            Expected annual return
        """
        if self.data_manager.equity_returns is None or self.data_manager.bond_returns is None:
            raise ValueError("Historical data not loaded")
        
        # Get historical average returns
        equity_avg = self.data_manager.equity_returns.mean()
        bond_avg = self.data_manager.bond_returns.mean()
        cash_avg = 0.0  # Cash returns 0% real return
        
        expected_return = (
            allocation.equity_percentage * equity_avg +
            allocation.bond_percentage * bond_avg +
            allocation.cash_percentage * cash_avg
        )
        
        return expected_return
    
    def calculate_portfolio_volatility(self, allocation: PortfolioAllocation) -> float:
        """
        Calculate portfolio volatility (standard deviation of returns).
        
        Args:
            allocation: Portfolio allocation
            
        Returns:
            Portfolio volatility (standard deviation)
        """
        if self.data_manager.equity_returns is None or self.data_manager.bond_returns is None:
            raise ValueError("Historical data not loaded")
        
        # Get available years
        equity_years = set(self.data_manager.equity_returns.index)
        bond_years = set(self.data_manager.bond_returns.index)
        available_years = list(equity_years & bond_years)
        
        if len(available_years) < 2:
            raise ValueError("Not enough data to calculate volatility")
        
        # Calculate portfolio returns for all available years
        portfolio_returns = []
        for year in available_years:
            equity_return = self.data_manager.equity_returns[year]
            bond_return = self.data_manager.bond_returns[year]
            portfolio_return = self.calculate_portfolio_return(allocation, equity_return, bond_return)
            portfolio_returns.append(portfolio_return)
        
        # Calculate standard deviation
        return np.std(portfolio_returns)
    
    def get_portfolio_statistics(self, allocation: PortfolioAllocation) -> Dict[str, float]:
        """
        Get comprehensive statistics for a portfolio allocation.
        
        Args:
            allocation: Portfolio allocation
            
        Returns:
            Dictionary with portfolio statistics
        """
        stats = {
            'expected_return': self.calculate_expected_return(allocation),
            'volatility': self.calculate_portfolio_volatility(allocation),
            'equity_percentage': allocation.equity_percentage,
            'bond_percentage': allocation.bond_percentage,
            'cash_percentage': allocation.cash_percentage
        }
        
        # Calculate Sharpe ratio (assuming risk-free rate is 0% real)
        if stats['volatility'] > 0:
            stats['sharpe_ratio'] = stats['expected_return'] / stats['volatility']
        else:
            stats['sharpe_ratio'] = 0.0
        
        return stats
    
    def validate_allocation(self, allocation: PortfolioAllocation) -> bool:
        """
        Validate that portfolio allocation is valid.
        
        Args:
            allocation: Portfolio allocation to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check percentages sum to 1.0
            total = allocation.equity_percentage + allocation.bond_percentage + allocation.cash_percentage
            if abs(total - 1.0) > 0.001:
                return False
            
            # Check all percentages are non-negative
            if any(pct < 0 for pct in [allocation.equity_percentage, allocation.bond_percentage, allocation.cash_percentage]):
                return False
            
            # Check all percentages are <= 1.0
            if any(pct > 1.0 for pct in [allocation.equity_percentage, allocation.bond_percentage, allocation.cash_percentage]):
                return False
            
            return True
            
        except Exception:
            return False