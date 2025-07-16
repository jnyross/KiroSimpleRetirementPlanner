#!/usr/bin/env python3
"""
Data validation demonstration script for the retirement calculator.

This script demonstrates the comprehensive data validation and quality checking
system for historical market data files.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_manager import HistoricalDataManager
from src.data_validator import DataValidator


def main():
    """Demonstrate data validation functionality."""
    print("🔍 Retirement Calculator Data Validation Demo")
    print("=" * 50)
    
    # Create data manager and validator
    data_manager = HistoricalDataManager()
    validator = DataValidator()
    
    print("\n1. Generating comprehensive data quality report...")
    print("-" * 50)
    
    # Generate and display data quality report
    quality_report = data_manager.get_data_quality_report()
    print(quality_report)
    
    print("\n2. Performing detailed validation...")
    print("-" * 50)
    
    # Perform validation
    validation_result = validator.validate_all_data_files()
    
    if validation_result.is_valid:
        print("✅ All data files passed validation!")
        
        # Show data statistics
        print("\n3. Data Statistics Summary:")
        print("-" * 30)
        stats = data_manager.get_data_statistics()
        
        for data_type, stat_dict in stats.items():
            print(f"\n{data_type.replace('_', ' ').title()}:")
            for key, value in stat_dict.items():
                if key.startswith('year_range'):
                    continue
                elif key in ['mean', 'std', 'min', 'max']:
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
            
            if 'year_range_start' in stat_dict and 'year_range_end' in stat_dict:
                print(f"  year_range: {stat_dict['year_range_start']}-{stat_dict['year_range_end']}")
        
        # Try loading data with validation
        print("\n4. Loading data with validation enabled...")
        print("-" * 45)
        try:
            data_manager.load_all_data(validate_quality=True)
            print("✅ Data loaded successfully with validation!")
            
            # Show loaded data info
            if data_manager.equity_returns is not None:
                print(f"   Equity returns: {len(data_manager.equity_returns)} years")
            if data_manager.bond_returns is not None:
                print(f"   Bond returns: {len(data_manager.bond_returns)} years")
            if data_manager.inflation_rates is not None:
                print(f"   Inflation rates: {len(data_manager.inflation_rates)} years")
                
        except ValueError as e:
            print(f"❌ Data loading failed: {e}")
    
    else:
        print("❌ Data validation failed!")
        print("\nErrors found:")
        for error in validation_result.errors:
            print(f"  • {error}")
        
        if validation_result.warnings:
            print("\nWarnings:")
            for warning in validation_result.warnings:
                print(f"  • {warning}")
    
    print("\n" + "=" * 50)
    print("Data validation demonstration complete!")


if __name__ == "__main__":
    main()