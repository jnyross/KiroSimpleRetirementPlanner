#!/usr/bin/env python3
"""
Analyze historical data to understand portfolio performance patterns.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager

def analyze_historical_data():
    """Analyze the historical data to understand portfolio performance."""
    print("=== Historical Data Analysis ===\n")
    
    # Load data
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    print("1. RAW DATA SUMMARY:")
    print(f"   Equity returns: {len(data_manager.equity_returns)} years (1980-2023)")
    print(f"   Bond returns: {len(data_manager.bond_returns)} years (1980-2023)")
    print(f"   Inflation rates: {len(data_manager.inflation_rates)} years (1980-2023)")
    
    # Load raw data for comparison
    equity_df = pd.read_csv("data/uk_equity_returns.csv")
    bond_df = pd.read_csv("data/uk_bond_returns.csv")
    inflation_df = pd.read_csv("data/uk_inflation_rates.csv")
    
    print(f"\n2. NOMINAL RETURNS ANALYSIS:")
    print(f"   Equity returns - Mean: {equity_df['return'].mean():.1%}, Std: {equity_df['return'].std():.1%}")
    print(f"   Bond returns - Mean: {bond_df['return'].mean():.1%}, Std: {bond_df['return'].std():.1%}")
    print(f"   Inflation - Mean: {inflation_df['inflation_rate'].mean():.1%}, Std: {inflation_df['inflation_rate'].std():.1%}")
    
    print(f"\n3. REAL RETURNS ANALYSIS (Current Method):")
    print(f"   Equity real returns - Mean: {data_manager.equity_returns.mean():.1%}, Std: {data_manager.equity_returns.std():.1%}")
    print(f"   Bond real returns - Mean: {data_manager.bond_returns.mean():.1%}, Std: {data_manager.bond_returns.std():.1%}")
    
    # Calculate real returns using proper formula
    print(f"\n4. REAL RETURNS ANALYSIS (Proper Formula):")
    proper_equity_real = []
    proper_bond_real = []
    
    for year in range(1980, 2024):
        if year in equity_df.set_index('year').index and year in inflation_df.set_index('year').index:
            equity_nominal = equity_df.set_index('year').loc[year, 'return']
            bond_nominal = bond_df.set_index('year').loc[year, 'return']
            inflation = inflation_df.set_index('year').loc[year, 'inflation_rate']
            
            # Proper real return formula: (1 + nominal) / (1 + inflation) - 1
            equity_real = (1 + equity_nominal) / (1 + inflation) - 1
            bond_real = (1 + bond_nominal) / (1 + inflation) - 1
            
            proper_equity_real.append(equity_real)
            proper_bond_real.append(bond_real)
    
    print(f"   Equity real returns (proper) - Mean: {np.mean(proper_equity_real):.1%}, Std: {np.std(proper_equity_real):.1%}")
    print(f"   Bond real returns (proper) - Mean: {np.mean(proper_bond_real):.1%}, Std: {np.std(proper_bond_real):.1%}")
    
    # Analyze portfolio performance
    print(f"\n5. PORTFOLIO PERFORMANCE ANALYSIS:")
    portfolio_manager = PortfolioManager(data_manager)
    
    for name, allocation in portfolio_manager.get_all_allocations().items():
        stats = portfolio_manager.get_portfolio_statistics(allocation)
        print(f"   {name:<30} Return: {stats['expected_return']:.1%}, Risk: {stats['volatility']:.1%}, Sharpe: {stats['sharpe_ratio']:.2f}")
    
    # Analyze problematic periods
    print(f"\n6. PROBLEMATIC PERIODS:")
    
    # Find worst equity years
    worst_equity_years = equity_df.nsmallest(5, 'return')
    print(f"   Worst equity years:")
    for _, row in worst_equity_years.iterrows():
        print(f"     {row['year']}: {row['return']:.1%}")
    
    # Find worst bond years
    worst_bond_years = bond_df.nsmallest(5, 'return')
    print(f"   Worst bond years:")
    for _, row in worst_bond_years.iterrows():
        print(f"     {row['year']}: {row['return']:.1%}")
    
    # High inflation periods
    high_inflation_years = inflation_df.nlargest(5, 'inflation_rate')
    print(f"   High inflation years:")
    for _, row in high_inflation_years.iterrows():
        print(f"     {row['year']}: {row['inflation_rate']:.1%}")
    
    # Correlation analysis
    print(f"\n7. CORRELATION ANALYSIS:")
    merged_df = pd.merge(equity_df, bond_df, on='year', suffixes=('_equity', '_bond'))
    merged_df = pd.merge(merged_df, inflation_df, on='year')
    
    corr_equity_bond = merged_df['return_equity'].corr(merged_df['return_bond'])
    corr_equity_inflation = merged_df['return_equity'].corr(merged_df['inflation_rate'])
    corr_bond_inflation = merged_df['return_bond'].corr(merged_df['inflation_rate'])
    
    print(f"   Equity-Bond correlation: {corr_equity_bond:.3f}")
    print(f"   Equity-Inflation correlation: {corr_equity_inflation:.3f}")
    print(f"   Bond-Inflation correlation: {corr_bond_inflation:.3f}")
    
    # Decade analysis
    print(f"\n8. DECADE ANALYSIS:")
    merged_df['decade'] = (merged_df['year'] // 10) * 10
    decade_analysis = merged_df.groupby('decade').agg({
        'return_equity': ['mean', 'std'],
        'return_bond': ['mean', 'std'],
        'inflation_rate': ['mean', 'std']
    }).round(3)
    
    print(decade_analysis)
    
    print(f"\n9. SEQUENCE OF RETURNS RISK:")
    # Look at early retirement periods (first 10 years)
    for start_year in [1980, 1990, 2000, 2010]:
        if start_year + 10 <= 2023:
            period_equity = equity_df[(equity_df['year'] >= start_year) & (equity_df['year'] < start_year + 10)]
            period_bond = bond_df[(bond_df['year'] >= start_year) & (bond_df['year'] < start_year + 10)]
            
            print(f"   {start_year}-{start_year+9}: Equity avg {period_equity['return'].mean():.1%}, Bond avg {period_bond['return'].mean():.1%}")
    
    print(f"\n10. DATA QUALITY CONCERNS:")
    print(f"   - Limited time period: Only 44 years (1980-2023)")
    print(f"   - Recent volatility: 2008 crash, 2022 bond crash may skew results")
    print(f"   - Real return calculation: Using simple subtraction vs proper formula")
    print(f"   - No verification against official sources (FTSE, Bank of England)")
    print(f"   - Missing earlier periods: No 1970s stagflation, 1960s-70s data")

if __name__ == "__main__":
    analyze_historical_data()