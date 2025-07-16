#!/usr/bin/env python3
"""
Test script to verify withdrawal patterns are correctly shown in charts.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models import UserInput
from main import RetirementCalculatorApp
import matplotlib.pyplot as plt
import numpy as np

def test_withdrawal_patterns():
    """Test that portfolio values decline with withdrawals."""
    print("=== Testing Withdrawal Patterns ===")
    
    # Test with sample data
    user_input = UserInput(
        current_age=60,  # Close to retirement
        current_savings=500000,  # Large initial savings
        monthly_savings=0,  # No additional savings
        desired_annual_income=40000  # Reasonable withdrawal
    )
    
    app = RetirementCalculatorApp(num_simulations=100)  # Reduced for testing
    
    try:
        print("Initializing components...")
        app.initialize_components()
        
        print("Running single portfolio test...")
        # Test with 50/50 allocation
        allocation = app.portfolio_manager.get_allocation("50% Equities/50% Bonds")
        
        # Run simulation for specific retirement age
        result = app.simulator.run_simulation_for_retirement_age(
            user_input, allocation, 65, show_progress=False
        )
        
        print(f"\\nPortfolio: {result.portfolio_allocation.name}")
        print(f"Retirement Age: {result.retirement_age}")
        print(f"Success Rate: {result.success_rate:.1%}")
        print(f"Portfolio Values Length: {len(result.portfolio_values)}")
        
        # Check if portfolio values show declining pattern
        portfolio_values = result.portfolio_values
        print(f"\\nPortfolio Values (first 10 years):")
        for i, value in enumerate(portfolio_values[:10]):
            age = result.retirement_age + i
            print(f"Age {age}: £{value:,.0f}")
        
        # Check if values are declining
        declining_count = 0
        for i in range(1, min(10, len(portfolio_values))):
            if portfolio_values[i] < portfolio_values[i-1]:
                declining_count += 1
        
        print(f"\\nYears with declining portfolio: {declining_count}/9")
        
        # Check percentile data
        if hasattr(result, 'percentile_data'):
            print(f"\\nPercentile data available: {list(result.percentile_data.keys())}")
            
            # Check 50th percentile values
            p50_values = result.percentile_data.get("50th", [])
            if len(p50_values) > 0:
                print(f"50th percentile values (first 5 years):")
                for i, value in enumerate(p50_values[:5]):
                    age = result.retirement_age + i
                    print(f"Age {age}: £{value:,.0f}")
        else:
            print("\\nNo percentile data found in result")
        
        # Test chart generation
        print("\\nTesting chart generation...")
        portfolio_results = {result.portfolio_allocation.name: result}
        analysis_results = app.analyzer.analyze_simulation_results(user_input, portfolio_results)
        
        # Check if percentile data is passed correctly
        print(f"Percentile data in analysis: {list(analysis_results.percentile_data.keys())}")
        
        # Generate chart
        chart_files = app.generate_charts(analysis_results)
        if chart_files:
            print(f"✅ Charts generated successfully: {len(chart_files)} files")
            for chart_type, path in chart_files.items():
                if isinstance(path, str):
                    print(f"  {chart_type}: {os.path.basename(path)}")
        else:
            print("❌ No charts generated")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_withdrawal_patterns()