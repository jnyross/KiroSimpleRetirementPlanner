#!/usr/bin/env python3
"""
Test comprehensive analysis with fixed withdrawal patterns.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models import UserInput
from main import RetirementCalculatorApp

def test_comprehensive_analysis():
    """Test comprehensive analysis with all portfolios."""
    print("=== Testing Comprehensive Analysis with Fixed Withdrawals ===")
    
    # Test with sample data
    user_input = UserInput(
        current_age=40,
        current_savings=100000,
        monthly_savings=2000,
        desired_annual_income=35000
    )
    
    app = RetirementCalculatorApp(num_simulations=100)  # Reduced for testing
    
    try:
        print("Initializing components...")
        app.initialize_components()
        
        print("Running comprehensive analysis...")
        results = app.run_analysis(user_input)
        
        print(f"\\n=== Analysis Results ===")
        print(f"Recommended Portfolio: {results.recommended_portfolio.name}")
        print(f"Recommended Retirement Age: {results.recommended_retirement_age}")
        
        print(f"\\n=== Portfolio Comparison ===")
        for result in results.portfolio_results:
            print(f"{result.portfolio_allocation.name:<30} Age {result.retirement_age:<3} Success {result.success_rate:.1%}")
            
            # Check if portfolio values decline
            portfolio_values = result.portfolio_values
            if len(portfolio_values) > 5:
                declining = sum(1 for i in range(1, 6) if portfolio_values[i] < portfolio_values[i-1])
                print(f"  → First 5 years declining: {declining}/5")
        
        print(f"\\n=== Percentile Data Check ===")
        for name, percentiles in results.percentile_data.items():
            print(f"{name}:")
            for percentile_name, values in percentiles.items():
                if len(values) > 3:
                    change = values[3] - values[0]  # Change over 3 years
                    print(f"  {percentile_name}: {len(values)} values, 3-year change: £{change:,.0f}")
        
        print("\\n✅ Comprehensive analysis test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_analysis()