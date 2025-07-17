"""
Test the /calculate endpoint with a real calculation.
"""

import sys
import os
import json
import time

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_calculate_endpoint():
    """Test the /calculate endpoint with real data."""
    try:
        from app import create_app
        
        app = create_app()
        
        # Test data
        test_data = {
            'current_age': 30,
            'current_savings': 50000,
            'monthly_savings': 1000,
            'desired_annual_income': 25000
        }
        
        print("🧪 Testing /calculate endpoint")
        print(f"📊 Test data: {test_data}")
        print("🔄 Running calculation (this may take a moment)...")
        
        with app.test_client() as client:
            start_time = time.time()
            
            # Make POST request to /calculate
            response = client.post('/calculate', 
                                 data=test_data,
                                 content_type='application/x-www-form-urlencoded')
            
            calculation_time = time.time() - start_time
            
            print(f"⏱️  Calculation completed in {calculation_time:.2f} seconds")
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                
                if data.get('success'):
                    print("✅ Calculation successful!")
                    print(f"   Calculation ID: {data.get('calculation_id')}")
                    print(f"   Total portfolios analyzed: {data.get('total_portfolios')}")
                    print(f"   Recommended portfolio: {data.get('recommended_portfolio')}")
                    print(f"   Recommended retirement age: {data.get('recommended_age')}")
                    
                    # Show results summary
                    results = data.get('results', [])
                    print(f"\n📈 Results Summary ({len(results)} portfolios):")
                    
                    for result in results:
                        name = result['portfolio_name']
                        age = result['retirement_age']
                        success_rate = result['success_rate']
                        
                        if age is not None:
                            print(f"   {name}: Age {age}, {success_rate:.1%} success")
                        else:
                            print(f"   {name}: Not achievable")
                    
                    return True
                else:
                    print(f"❌ Calculation failed: {data.get('error')}")
                    if 'errors' in data:
                        print(f"   Validation errors: {data['errors']}")
                    return False
            else:
                print(f"❌ HTTP error {response.status_code}")
                try:
                    error_data = response.get_json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response text: {response.get_data(as_text=True)}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def test_health_endpoint():
    """Test the /health endpoint."""
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/health')
            
            if response.status_code == 200:
                data = response.get_json()
                print("✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   Service: {data.get('service')}")
                print(f"   Calculation engine: {data.get('calculation_engine')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health check test failed: {str(e)}")
        return False

def test_portfolios_endpoint():
    """Test the /portfolios endpoint."""
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/portfolios')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    portfolios = data.get('portfolios', [])
                    print("✅ Portfolios endpoint works")
                    print(f"   Available portfolios: {len(portfolios)}")
                    for portfolio in portfolios:
                        name = portfolio['name']
                        equity = portfolio['equity_percentage']
                        bond = portfolio['bond_percentage']
                        cash = portfolio['cash_percentage']
                        print(f"     {name}: {equity:.0%} equity, {bond:.0%} bonds, {cash:.0%} cash")
                    return True
                else:
                    print(f"❌ Portfolios request failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Portfolios endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Portfolios test failed: {str(e)}")
        return False

def main():
    """Run endpoint tests."""
    print("🧪 Testing Web Endpoints")
    print("=" * 50)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Portfolios Endpoint", test_portfolios_endpoint),
        ("Calculate Endpoint", test_calculate_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All endpoint tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)