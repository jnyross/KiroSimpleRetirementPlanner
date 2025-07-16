#!/usr/bin/env python3
"""
Full application test script.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models import UserInput
from main import RetirementCalculatorApp

def test_full_application():
    """Test the complete application flow."""
    print("=== Testing Full Application ===")
    
    # Test with sample data
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=1000,
        desired_annual_income=30000
    )
    
    app = RetirementCalculatorApp(num_simulations=100)  # Reduced for testing
    
    try:
        print("Initializing components...")
        app.initialize_components()
        
        print("Running analysis...")
        results = app.run_analysis(user_input)
        
        print(f"✅ Analysis complete: {len(results.portfolio_results)} portfolios analyzed")
        print(f"✅ Recommended portfolio: {results.recommended_portfolio.name}")
        print(f"✅ Recommended retirement age: {results.recommended_retirement_age}")
        
        print("\\n=== Portfolio Results ===")
        for result in results.portfolio_results:
            print(f"{result.portfolio_allocation.name}: Age {result.retirement_age}, Success {result.success_rate:.1%}")
        
        print("\\n✅ Full application test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_application()