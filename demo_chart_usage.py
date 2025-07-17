#!/usr/bin/env python3
"""
Demo script showing how to use the web chart generator in a Flask application.

This demonstrates the integration between the chart generator and web routes.
"""

import json
from chart_generator import generate_all_charts, create_mobile_optimized_config


def simulate_web_request():
    """Simulate a web request with calculation results."""
    
    # This would normally come from the actual simulation engine
    simulation_results = [
        {
            "portfolio_name": "Conservative (20/80)",
            "success_rate": 0.92,
            "retirement_age": 65,
            "percentile_data": {
                "10th": [100000 * (1.02 ** year) * 0.7 for year in range(30)],
                "50th": [100000 * (1.04 ** year) for year in range(30)],
                "90th": [100000 * (1.06 ** year) * 1.3 for year in range(30)]
            }
        },
        {
            "portfolio_name": "Balanced (60/40)",
            "success_rate": 0.99,
            "retirement_age": 62,
            "percentile_data": {
                "10th": [100000 * (1.03 ** year) * 0.6 for year in range(30)],
                "50th": [100000 * (1.06 ** year) for year in range(30)],
                "90th": [100000 * (1.09 ** year) * 1.4 for year in range(30)]
            }
        }
    ]
    
    return simulation_results


def demo_flask_route_usage():
    """Demo how charts would be generated in a Flask route."""
    print("🌐 Demo: Flask route chart generation")
    
    # Simulate receiving calculation results
    results = simulate_web_request()
    
    # Generate charts (this would be in your Flask route)
    charts_data = generate_all_charts(results)
    
    # Simulate returning JSON response to frontend
    response_data = {
        'success': True,
        'results': results,
        'charts': charts_data
    }
    
    print(f"✅ Generated response with {len(charts_data['portfolio_charts'])} portfolio charts")
    print(f"✅ Recommended portfolio: {charts_data['selector_data']['default']}")
    print(f"✅ Chart selector has {len(charts_data['selector_data']['options'])} options")
    
    return response_data


def demo_mobile_detection():
    """Demo mobile-specific chart generation."""
    print("📱 Demo: Mobile-optimized chart generation")
    
    results = simulate_web_request()
    
    # Generate mobile-optimized charts
    mobile_config = create_mobile_optimized_config()
    mobile_charts = generate_all_charts(results, mobile_config)
    
    # Parse one chart to show mobile optimizations
    sample_chart = json.loads(list(mobile_charts['portfolio_charts'].values())[0])
    
    print(f"✅ Mobile chart height: {sample_chart['layout']['height']}")
    print(f"✅ Mobile legend orientation: {sample_chart['layout']['legend']['orientation']}")
    print(f"✅ Mobile autosize: {sample_chart['layout'].get('autosize', False)}")
    
    return mobile_charts


def demo_chart_selector_usage():
    """Demo chart selector functionality."""
    print("🎛️  Demo: Chart selector functionality")
    
    results = simulate_web_request()
    charts_data = generate_all_charts(results)
    
    selector_data = charts_data['selector_data']
    
    print("Chart selector options:")
    for option in selector_data['options']:
        recommended_marker = " ⭐" if option['recommended'] else ""
        print(f"  - {option['label']}{recommended_marker}")
    
    print(f"✅ Default selection: {selector_data['default']}")
    
    return selector_data


def demo_error_handling():
    """Demo error handling with invalid data."""
    print("⚠️  Demo: Error handling")
    
    # Test with empty data
    empty_charts = generate_all_charts([])
    print(f"✅ Handled empty data: {len(empty_charts['portfolio_charts'])} charts generated")
    
    # Test with incomplete data
    incomplete_data = [{"portfolio_name": "Test", "success_rate": 0.5}]
    incomplete_charts = generate_all_charts(incomplete_data)
    print(f"✅ Handled incomplete data: {len(incomplete_charts['portfolio_charts'])} charts generated")
    
    return True


def main():
    """Run all demos."""
    print("🚀 Chart Generator Web Integration Demo\n")
    
    try:
        # Demo Flask route usage
        demo_flask_route_usage()
        print()
        
        # Demo mobile detection
        demo_mobile_detection()
        print()
        
        # Demo chart selector
        demo_chart_selector_usage()
        print()
        
        # Demo error handling
        demo_error_handling()
        print()
        
        print("🎉 All demos completed successfully!")
        print("\n📋 Web integration features demonstrated:")
        print("  ✅ Flask route integration")
        print("  ✅ Mobile-optimized chart generation")
        print("  ✅ Chart selector with recommendations")
        print("  ✅ Error handling for invalid data")
        print("  ✅ JSON response formatting")
        print("  ✅ Responsive chart configuration")
        
        print("\n💡 Usage in Flask route:")
        print("```python")
        print("@app.route('/calculate', methods=['POST'])")
        print("def calculate():")
        print("    # ... run simulation ...")
        print("    charts_data = generate_all_charts(simulation_results)")
        print("    return jsonify({")
        print("        'success': True,")
        print("        'results': simulation_results,")
        print("        'charts': charts_data")
        print("    })")
        print("```")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)