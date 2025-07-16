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
        """Load all historical data files with enhanced error handling."""
        errors = []
        
        # Try to load each data file, collecting errors
        try:
            self.inflation_rates = self._load_inflation_rates()
        except Exception as e:
            errors.append(f"Inflation rates: {str(e)}")
        
        try:
            self.equity_returns = self._load_equity_returns()
        except Exception as e:
            errors.append(f"Equity returns: {str(e)}")
        
        try:
            self.bond_returns = self._load_bond_returns()
        except Exception as e:
            errors.append(f"Bond returns: {str(e)}")
        
        try:
            self.portfolio_allocations = self._load_portfolio_allocations()
        except Exception as e:
            errors.append(f"Portfolio allocations: {str(e)}")
        
        # If we have errors, provide comprehensive error message
        if errors:
            error_summary = "\n".join([f"  - {error}" for error in errors])
            raise ValueError(
                f"Failed to load required historical data files:\n{error_summary}\n\n"
                f"Please ensure all required data files are present in the '{self.data_directory}' directory:\n"
                f"  - uk_equity_returns.csv (columns: year, return)\n"
                f"  - uk_bond_returns.csv (columns: year, return)\n"
                f"  - uk_inflation_rates.csv (columns: year, inflation_rate)\n\n"
                f"Each file should contain at least 10 years of annual data."
            )
        
    def _load_equity_returns(self) -> pd.Series:
        """Load UK equity returns data."""
        file_path = os.path.join(self.data_directory, "uk_equity_returns.csv")
        
        # Check if file exists with helpful error message
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Equity returns data file not found.\n"
                f"Expected location: {file_path}\n"
                f"Please ensure the historical data files are in the '{self.data_directory}' directory.\n"
                f"The file should contain columns: 'year' and 'return' with annual equity return data."
            )
            
        try:
            # Load CSV with better error handling
            try:
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                raise ValueError(f"Equity returns file is empty: {file_path}")
            except pd.errors.ParserError as e:
                raise ValueError(f"Cannot parse equity returns file (check CSV format): {file_path}\nError: {str(e)}")
            
            # Validate required columns
            if df.empty:
                raise ValueError(f"Equity returns file contains no data: {file_path}")
            
            required_columns = ['year', 'return']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                available_columns = list(df.columns)
                raise ValueError(
                    f"Equity returns file is missing required columns: {missing_columns}\n"
                    f"Available columns: {available_columns}\n"
                    f"Required columns: {required_columns}\n"
                    f"File: {file_path}"
                )
            
            # Validate data types and ranges
            if not pd.api.types.is_numeric_dtype(df['year']):
                raise ValueError(f"'year' column must contain numeric values in {file_path}")
            
            if not pd.api.types.is_numeric_dtype(df['return']):
                raise ValueError(f"'return' column must contain numeric values in {file_path}")
            
            # Check for reasonable data ranges
            if df['year'].min() < 1800 or df['year'].max() > 2030:
                raise ValueError(f"Year values seem unreasonable (range: {df['year'].min()}-{df['year'].max()}) in {file_path}")
            
            if df['return'].min() < -0.9 or df['return'].max() > 3.0:
                raise ValueError(f"Return values seem unreasonable (range: {df['return'].min():.1%}-{df['return'].max():.1%}) in {file_path}")
            
            # Check for missing values
            if df['year'].isna().any() or df['return'].isna().any():
                raise ValueError(f"Equity returns file contains missing values in {file_path}")
            
            # Load inflation data first if not already loaded
            if self.inflation_rates is None:
                self.inflation_rates = self._load_inflation_rates()
            
            # Convert to real returns (inflation-adjusted) using proper formula
            inflation_rates = self._get_inflation_for_year(df['year'])
            df['real_return'] = (1 + df['return']) / (1 + inflation_rates) - 1
            
            # Validate final data
            if len(df) < 10:
                raise ValueError(f"Insufficient equity data: need at least 10 years, found {len(df)} years in {file_path}")
            
            return df.set_index('year')['real_return']
            
        except FileNotFoundError:
            raise  # Re-raise FileNotFoundError as-is
        except ValueError:
            raise  # Re-raise ValueError as-is
        except Exception as e:
            raise ValueError(
                f"Unexpected error loading equity returns from {file_path}.\n"
                f"Please check the file format and contents.\n"
                f"Error details: {str(e)}"
            )
    
    def _load_bond_returns(self) -> pd.Series:
        """Load UK bond returns data."""
        file_path = os.path.join(self.data_directory, "uk_bond_returns.csv")
        
        # Check if file exists with helpful error message
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Bond returns data file not found.\n"
                f"Expected location: {file_path}\n"
                f"Please ensure the historical data files are in the '{self.data_directory}' directory.\n"
                f"The file should contain columns: 'year' and 'return' with annual bond return data."
            )
            
        try:
            # Load CSV with better error handling
            try:
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                raise ValueError(f"Bond returns file is empty: {file_path}")
            except pd.errors.ParserError as e:
                raise ValueError(f"Cannot parse bond returns file (check CSV format): {file_path}\nError: {str(e)}")
            
            # Validate required columns
            if df.empty:
                raise ValueError(f"Bond returns file contains no data: {file_path}")
            
            required_columns = ['year', 'return']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                available_columns = list(df.columns)
                raise ValueError(
                    f"Bond returns file is missing required columns: {missing_columns}\n"
                    f"Available columns: {available_columns}\n"
                    f"Required columns: {required_columns}\n"
                    f"File: {file_path}"
                )
            
            # Validate data types and ranges
            if not pd.api.types.is_numeric_dtype(df['year']):
                raise ValueError(f"'year' column must contain numeric values in {file_path}")
            
            if not pd.api.types.is_numeric_dtype(df['return']):
                raise ValueError(f"'return' column must contain numeric values in {file_path}")
            
            # Check for reasonable data ranges
            if df['year'].min() < 1800 or df['year'].max() > 2030:
                raise ValueError(f"Year values seem unreasonable (range: {df['year'].min()}-{df['year'].max()}) in {file_path}")
            
            if df['return'].min() < -0.7 or df['return'].max() > 1.5:
                raise ValueError(f"Bond return values seem unreasonable (range: {df['return'].min():.1%}-{df['return'].max():.1%}) in {file_path}")
            
            # Check for missing values
            if df['year'].isna().any() or df['return'].isna().any():
                raise ValueError(f"Bond returns file contains missing values in {file_path}")
            
            # Load inflation data first if not already loaded
            if self.inflation_rates is None:
                self.inflation_rates = self._load_inflation_rates()
            
            # Convert to real returns (inflation-adjusted) using proper formula
            inflation_rates = self._get_inflation_for_year(df['year'])
            df['real_return'] = (1 + df['return']) / (1 + inflation_rates) - 1
            
            # Validate final data
            if len(df) < 10:
                raise ValueError(f"Insufficient bond data: need at least 10 years, found {len(df)} years in {file_path}")
            
            return df.set_index('year')['real_return']
            
        except FileNotFoundError:
            raise  # Re-raise FileNotFoundError as-is
        except ValueError:
            raise  # Re-raise ValueError as-is
        except Exception as e:
            raise ValueError(
                f"Unexpected error loading bond returns from {file_path}.\n"
                f"Please check the file format and contents.\n"
                f"Error details: {str(e)}"
            )
    
    def _load_inflation_rates(self) -> pd.Series:
        """Load UK inflation rates data."""
        file_path = os.path.join(self.data_directory, "uk_inflation_rates.csv")
        
        # Check if file exists with helpful error message
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Inflation rates data file not found.\n"
                f"Expected location: {file_path}\n"
                f"Please ensure the historical data files are in the '{self.data_directory}' directory.\n"
                f"The file should contain columns: 'year' and 'inflation_rate' with annual inflation data."
            )
            
        try:
            # Load CSV with better error handling
            try:
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                raise ValueError(f"Inflation rates file is empty: {file_path}")
            except pd.errors.ParserError as e:
                raise ValueError(f"Cannot parse inflation rates file (check CSV format): {file_path}\nError: {str(e)}")
            
            # Validate required columns
            if df.empty:
                raise ValueError(f"Inflation rates file contains no data: {file_path}")
            
            required_columns = ['year', 'inflation_rate']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                available_columns = list(df.columns)
                raise ValueError(
                    f"Inflation rates file is missing required columns: {missing_columns}\n"
                    f"Available columns: {available_columns}\n"
                    f"Required columns: {required_columns}\n"
                    f"File: {file_path}"
                )
            
            # Validate data types and ranges
            if not pd.api.types.is_numeric_dtype(df['year']):
                raise ValueError(f"'year' column must contain numeric values in {file_path}")
            
            if not pd.api.types.is_numeric_dtype(df['inflation_rate']):
                raise ValueError(f"'inflation_rate' column must contain numeric values in {file_path}")
            
            # Check for reasonable data ranges
            if df['year'].min() < 1800 or df['year'].max() > 2030:
                raise ValueError(f"Year values seem unreasonable (range: {df['year'].min()}-{df['year'].max()}) in {file_path}")
            
            if df['inflation_rate'].min() < -0.3 or df['inflation_rate'].max() > 0.5:
                raise ValueError(f"Inflation rate values seem unreasonable (range: {df['inflation_rate'].min():.1%}-{df['inflation_rate'].max():.1%}) in {file_path}")
            
            # Check for missing values
            if df['year'].isna().any() or df['inflation_rate'].isna().any():
                raise ValueError(f"Inflation rates file contains missing values in {file_path}")
            
            # Validate final data
            if len(df) < 10:
                raise ValueError(f"Insufficient inflation data: need at least 10 years, found {len(df)} years in {file_path}")
            
            return df.set_index('year')['inflation_rate']
            
        except FileNotFoundError:
            raise  # Re-raise FileNotFoundError as-is
        except ValueError:
            raise  # Re-raise ValueError as-is
        except Exception as e:
            raise ValueError(
                f"Unexpected error loading inflation rates from {file_path}.\n"
                f"Please check the file format and contents.\n"
                f"Error details: {str(e)}"
            )
    
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
    
    def get_data_diagnostics(self) -> str:
        """
        Get diagnostic information about loaded data for troubleshooting.
        
        Returns:
            Diagnostic information as formatted string
        """
        diagnostics = ["📊 Data Diagnostics Report"]
        diagnostics.append("=" * 40)
        
        # Check data directory
        if os.path.exists(self.data_directory):
            diagnostics.append(f"✅ Data directory exists: {self.data_directory}")
            files = os.listdir(self.data_directory)
            diagnostics.append(f"   Files found: {files}")
        else:
            diagnostics.append(f"❌ Data directory missing: {self.data_directory}")
            return "\n".join(diagnostics)
        
        # Check each data file
        required_files = [
            ("uk_equity_returns.csv", "Equity returns"),
            ("uk_bond_returns.csv", "Bond returns"),
            ("uk_inflation_rates.csv", "Inflation rates")
        ]
        
        for filename, description in required_files:
            filepath = os.path.join(self.data_directory, filename)
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath)
                    diagnostics.append(f"✅ {description}: {len(df)} rows, columns: {list(df.columns)}")
                    if not df.empty:
                        year_range = f"{df.iloc[0, 0]}-{df.iloc[-1, 0]}" if len(df) > 0 else "N/A"
                        diagnostics.append(f"   Year range: {year_range}")
                except Exception as e:
                    diagnostics.append(f"❌ {description}: File exists but cannot be read - {str(e)}")
            else:
                diagnostics.append(f"❌ {description}: File missing - {filepath}")
        
        # Check loaded data status
        diagnostics.append("\nLoaded Data Status:")
        diagnostics.append(f"  Equity returns: {'✅ Loaded' if self.equity_returns is not None else '❌ Not loaded'}")
        diagnostics.append(f"  Bond returns: {'✅ Loaded' if self.bond_returns is not None else '❌ Not loaded'}")
        diagnostics.append(f"  Inflation rates: {'✅ Loaded' if self.inflation_rates is not None else '❌ Not loaded'}")
        
        # Data overlap analysis
        if all(data is not None for data in [self.equity_returns, self.bond_returns, self.inflation_rates]):
            equity_years = set(self.equity_returns.index)
            bond_years = set(self.bond_returns.index)
            inflation_years = set(self.inflation_rates.index)
            overlapping_years = equity_years & bond_years & inflation_years
            
            diagnostics.append(f"\nData Overlap Analysis:")
            diagnostics.append(f"  Equity years: {len(equity_years)} ({min(equity_years)}-{max(equity_years)})")
            diagnostics.append(f"  Bond years: {len(bond_years)} ({min(bond_years)}-{max(bond_years)})")
            diagnostics.append(f"  Inflation years: {len(inflation_years)} ({min(inflation_years)}-{max(inflation_years)})")
            diagnostics.append(f"  Overlapping years: {len(overlapping_years)}")
            
            if len(overlapping_years) >= 10:
                diagnostics.append("  ✅ Sufficient overlapping data for analysis")
            else:
                diagnostics.append("  ❌ Insufficient overlapping data (need at least 10 years)")
        
        return "\n".join(diagnostics)