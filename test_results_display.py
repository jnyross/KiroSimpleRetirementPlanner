"""
Test script to verify the results display flow end-to-end
"""

import json
import sys
from flask import Flask
from app import create_app

def test_results_display_flow():
    """Test the complete results display flow"""
    app = create_app()
    
    with app.test_client() as client:
        # Test data
        test_data = {
            'current_age': 35,
            'current_savings': 50000,
            'monthly_savings': 500,
            'desired_annual_income': 40000
        }
        
        print("Testing results display flow...")
        print(f"Input data: {json.dumps(test_data, indent=2)}")
        
        # Test 1: Submit calculation request
        print("\n1. Testing calculation endpoint...")
        response = client.post('/calculate',
                              json=test_data,
                              content_type='application/json')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        result = response.get_json()
        assert result['success'] == True, "Calculation should succeed"
        assert 'results' in result, "Results should be present"
        assert 'charts' in result, "Charts should be present"
        assert 'recommended_portfolio' in result, "Recommended portfolio should be present"
        assert 'user_input' in result, "User input should be echoed back"
        
        print("✓ Calculation endpoint working correctly")
        
        # Test 2: Verify results structure
        print("\n2. Verifying results structure...")
        print(f"   Found {len(result['results'])} portfolio results")
        print(f"   Result keys: {list(result.keys())}")
        if len(result['results']) != 6:
            print(f"   Portfolio results: {[r.get('portfolio_name', 'unnamed') for r in result['results']]}")
        assert len(result['results']) >= 6, f"Should have at least 6 portfolio results, got {len(result['results'])}"
        
        for portfolio_result in result['results']:
            assert 'portfolio_name' in portfolio_result
            assert 'portfolio_allocation' in portfolio_result
            assert 'success_rate' in portfolio_result
            assert 'retirement_age' in portfolio_result
            assert 'final_portfolio_value' in portfolio_result
            
            allocation = portfolio_result['portfolio_allocation']
            assert 'name' in allocation
            assert 'equity_percentage' in allocation
            assert 'bond_percentage' in allocation
            assert 'cash_percentage' in allocation
        
        print("✓ Results structure is correct")
        
        # Test 3: Verify charts structure
        print("\n3. Verifying charts structure...")
        charts = result['charts']
        assert 'portfolio_charts' in charts, "Portfolio charts should be present"
        assert isinstance(charts['portfolio_charts'], dict), "Portfolio charts should be a dict"
        
        # Verify each portfolio has a chart
        for portfolio_result in result['results']:
            portfolio_name = portfolio_result['portfolio_name']
            assert portfolio_name in charts['portfolio_charts'], f"Chart missing for {portfolio_name}"
            
            # Verify chart is valid JSON
            chart_json = charts['portfolio_charts'][portfolio_name]
            chart_data = json.loads(chart_json)
            assert 'data' in chart_data
            assert 'layout' in chart_data
        
        print("✓ Charts structure is correct")
        
        # Test 4: Verify recommendation logic
        print("\n4. Verifying recommendation logic...")
        if result['recommended_portfolio']:
            # Find the recommended portfolio in results
            recommended = next(
                (r for r in result['results'] if r['portfolio_name'] == result['recommended_portfolio']),
                None
            )
            assert recommended is not None, "Recommended portfolio should exist in results"
            assert recommended['success_rate'] >= 0.99, "Recommended portfolio should have 99%+ success rate"
            assert recommended['retirement_age'] == result['recommended_age'], "Ages should match"
            
            # Verify it's the earliest retirement age among successful portfolios
            successful_portfolios = [r for r in result['results'] if r['success_rate'] >= 0.99]
            if successful_portfolios:
                earliest_age = min(p['retirement_age'] for p in successful_portfolios if p['retirement_age'] is not None)
                assert result['recommended_age'] == earliest_age, "Should recommend earliest retirement age"
        
        print("✓ Recommendation logic is correct")
        
        # Test 5: Test form validation
        print("\n5. Testing form validation...")
        invalid_data = {
            'current_age': 150,  # Invalid age
            'current_savings': -1000,  # Negative savings
            'monthly_savings': 0,
            'desired_annual_income': 0  # Zero income
        }
        
        response = client.post('/calculate',
                              json=invalid_data,
                              content_type='application/json')
        
        assert response.status_code == 400, f"Expected 400 for invalid data, got {response.status_code}"
        error_result = response.get_json()
        assert error_result['success'] == False
        assert 'errors' in error_result
        
        print("✓ Form validation working correctly")
        
        # Test 6: Test missing fields
        print("\n6. Testing missing fields...")
        incomplete_data = {
            'current_age': 35,
            'current_savings': 50000
            # Missing monthly_savings and desired_annual_income
        }
        
        response = client.post('/calculate',
                              json=incomplete_data,
                              content_type='application/json')
        
        assert response.status_code == 400, f"Expected 400 for incomplete data, got {response.status_code}"
        
        print("✓ Missing field validation working correctly")
        
        print("\n✅ All results display flow tests passed!")
        
        # Print sample results for verification
        print("\n" + "="*50)
        print("SAMPLE RESULTS SUMMARY")
        print("="*50)
        print(f"Recommended Portfolio: {result.get('recommended_portfolio', 'None')}")
        print(f"Recommended Retirement Age: {result.get('recommended_age', 'N/A')}")
        print("\nPortfolio Results:")
        for r in result['results']:
            print(f"  - {r['portfolio_name']}: "
                  f"Age {r['retirement_age'] or 'N/A'}, "
                  f"Success {r['success_rate']:.1%}")
        
        return True

if __name__ == "__main__":
    try:
        test_results_display_flow()
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)