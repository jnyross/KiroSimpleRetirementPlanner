"""
Test script to verify the routes integration works correctly.
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_app_creation():
    """Test that the Flask app can be created successfully."""
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create Flask app: {str(e)}")
        return False

def test_routes_registration():
    """Test that routes are registered correctly."""
    try:
        from app import create_app
        app = create_app()
        
        # Check if routes are registered
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        print("✅ Routes registered:")
        for route in routes:
            print(f"   {route}")
        
        # Check for expected routes
        expected_routes = ['/', '/calculate', '/health', '/portfolios']
        registered_paths = [rule.rule for rule in app.url_map.iter_rules()]
        
        missing_routes = [route for route in expected_routes if route not in registered_paths]
        if missing_routes:
            print(f"⚠️  Missing expected routes: {missing_routes}")
        else:
            print("✅ All expected routes are registered")
        
        return True
    except Exception as e:
        print(f"❌ Failed to check routes: {str(e)}")
        return False

def test_calculation_engine_init():
    """Test that the calculation engine can be initialized."""
    try:
        from routes import get_calculation_engine
        
        print("🔄 Testing calculation engine initialization...")
        data_manager, portfolio_manager, tax_calculator, guard_rails_engine, simulator = get_calculation_engine()
        
        print("✅ Calculation engine components initialized:")
        print(f"   Data manager: {type(data_manager).__name__}")
        print(f"   Portfolio manager: {type(portfolio_manager).__name__}")
        print(f"   Tax calculator: {type(tax_calculator).__name__}")
        print(f"   Guard rails engine: {type(guard_rails_engine).__name__}")
        print(f"   Simulator: {type(simulator).__name__}")
        
        # Test portfolio allocations
        allocations = portfolio_manager.get_all_allocations()
        print(f"   Available portfolios: {len(allocations)}")
        for name in allocations.keys():
            print(f"     - {name}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize calculation engine: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def test_form_validation():
    """Test that form validation works correctly."""
    try:
        from forms import CalculatorForm
        
        # Test valid form data
        valid_data = {
            'current_age': 30,
            'current_savings': 50000,
            'monthly_savings': 1000,
            'desired_annual_income': 30000
        }
        
        form = CalculatorForm(data=valid_data)
        if form.validate():
            print("✅ Form validation works for valid data")
            user_input = form.to_user_input()
            print(f"   Converted to UserInput: {user_input}")
        else:
            print(f"❌ Form validation failed for valid data: {form.errors}")
            return False
        
        # Test invalid form data
        invalid_data = {
            'current_age': 150,  # Invalid age
            'current_savings': -1000,  # Negative savings
            'monthly_savings': 500,
            'desired_annual_income': 30000
        }
        
        form = CalculatorForm(data=invalid_data)
        if not form.validate():
            print("✅ Form validation correctly rejects invalid data")
            print(f"   Validation errors: {form.errors}")
        else:
            print("❌ Form validation should have failed for invalid data")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to test form validation: {str(e)}")
        return False

def main():
    """Run all integration tests."""
    print("🧪 Testing Routes Integration")
    print("=" * 50)
    
    tests = [
        ("App Creation", test_app_creation),
        ("Routes Registration", test_routes_registration),
        ("Form Validation", test_form_validation),
        ("Calculation Engine", test_calculation_engine_init),
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
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)