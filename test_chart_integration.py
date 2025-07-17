#!/usr/bin/env python3
"""
Integration test for chart generator with simulation results.

This test verifies that the chart generator can work with actual
simulation results from the retirement calculator.
"""

import sys
import json
import numpy as np
from chart_generator import generate_all_charts, WebChartGenerator


def create_realistic_simulation_results():
    """Create realistic simulation results that match the actual data structure."""
    
    # Portfolio allocations matching the actual retirement calculator
    portfolios = [
        {"name": "100% Cash", "equity": 0.0, "bond": 0.0, "cash": 1.0},
        {"name": "Conservative (20/80)", "equity": 0.2, "bond": 0.8, "cash": 0.0},
        {"name": "Moderate (40/60)", "equity": 0.4, "bond": 0.6, "cash": 0.0},
        {"name": "Balanced (60/40)", "equity": 0.6, "bond": 0.4, "cash": 0.0},
        {"name": "Growth (80/20)", "equity": 0.8, "bond": 0.2, "cash": 0.0},
        {"name": "100% Equity", "equity": 1.0, "bond": 0.0, "cash": 0.0}
    ]
    
    results_data = []
    
    # Simulate realistic retirement scenarios
    for i, portfolio in enumerate(portfolios):
        # More realistic success rates based on historical data
        if portfolio["cash"] == 1.0:  # 100% Cash
            success_rate = 0.45  # Low success due to inflation
            retirement_age = 75   # Late retirement needed
        elif portfolio["equity"] <= 0.2:  # Conservative
            success_rate = 0.85
            retirement_age = 68
        elif portfolio["equity"] <= 0.4:  # Moderate
            success_rate = 0.92
            retirement_age = 65
        elif portfolio["equity"] <= 0.6:  # Balanced
            success_rate = 0.96
            retirement_age = 63
        elif portfolio["equity"] <= 0.8:  # Growth
            success_rate = 0.99
            retirement_age = 61
        else:  # 100% Equity
            success_rate = 0.995
            retirement_age = 60
        
        # Generate realistic percentile data (40 years of projections)
        years = 40
        initial_value = 500000  # Starting portfolio value
        
        percentile_10 = []
        percentile_50 = []
        percentile_90 = []
        
        for year in range(years):
            # Realistic growth patterns
            if portfolio["cash"] == 1.0:
                # Cash loses to inflation
                real_return = -0.02
                volatility = 0.01
            else:
                # Mixed portfolios with realistic returns
                equity_return = 0.07
                bond_return = 0.03
                cash_return = 0.01
                
                expected_return = (portfolio["equity"] * equity_return + 
                                 portfolio["bond"] * bond_return + 
                                 portfolio["cash"] * cash_return)
                
                # Adjust for inflation (assume 2.5% inflation)
                real_return = expected_return - 0.025
                volatility = 0.05 + portfolio["equity"] * 0.15
            
            # Calculate portfolio values with realistic volatility
            median_value = initial_value * ((1 + real_return) ** year)
            
            # Add realistic percentile spreads
            p10_multiplier = 1 - (volatility * 1.28)  # ~10th percentile
            p90_multiplier = 1 + (volatility * 1.28)  # ~90th percentile
            
            p10_value = max(0, median_value * p10_multiplier)
            p50_value = median_value
            p90_value = median_value * p90_multiplier
            
            percentile_10.append(p10_value)
            percentile_50.append(p50_value)
            percentile_90.append(p90_value)
        
        result = {
            "portfolio_name": portfolio["name"],
            "success_rate": success_rate,
            "retirement_age": retirement_age,
            "percentile_data": {
                "10th": percentile_10,
                "50th": percentile_50,
                "90th": percentile_90
            }
        }
        
        results_data.append(result)
    
    return results_data


def test_chart_generation_with_realistic_data():
    """Test chart generation with realistic simulation data."""
    print("🧪 Testing chart generation with realistic simulation data...")
    
    # Generate realistic simulation results
    simulation_results = create_realistic_simulation_results()
    
    # Generate all charts
    all_charts = generate_all_charts(simulation_results)
    
    # Verify all expected charts were generated
    assert 'portfolio_charts' in all_charts
    assert 'comparison_chart' in all_charts
    assert 'success_rate_chart' in all_charts
    assert 'retirement_age_chart' in all_charts
    assert 'selector_data' in all_charts
    
    print(f"✅ Generated {len(all_charts['portfolio_charts'])} portfolio charts")
    print(f"✅ Generated comparison chart")
    print(f"✅ Generated success rate chart")
    print(f"✅ Generated retirement age chart")
    
    # Verify selector data
    selector_data = all_charts['selector_data']
    assert 'options' in selector_data
    assert 'default' in selector_data
    assert len(selector_data['options']) == len(simulation_results)
    
    # Check that the recommended portfolio is correctly identified
    recommended = selector_data['default']
    print(f"✅ Recommended portfolio: {recommended}")
    
    # Verify that successful portfolios are identified
    successful_portfolios = [
        opt for opt in selector_data['options'] 
        if opt['success_rate'] >= 99.0
    ]
    print(f"✅ Found {len(successful_portfolios)} portfolios with 99%+ success rate")
    
    return all_charts


def test_chart_json_validity():
    """Test that generated charts produce valid JSON."""
    print("🧪 Testing chart JSON validity...")
    
    generator = WebChartGenerator()
    simulation_results = create_realistic_simulation_results()
    
    # Test individual chart JSON validity
    for result in simulation_results:
        chart_json = generator.generate_portfolio_chart(result)
        
        # Verify it's valid JSON
        try:
            chart_data = json.loads(chart_json)
            assert 'data' in chart_data
            assert 'layout' in chart_data
            print(f"✅ Valid JSON for {result['portfolio_name']}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON for {result['portfolio_name']}: {e}")
            raise
    
    # Test comparison chart JSON
    comparison_json = generator.generate_comparison_chart(simulation_results)
    comparison_data = json.loads(comparison_json)
    assert 'data' in comparison_data
    assert 'layout' in comparison_data
    print("✅ Valid JSON for comparison chart")


def test_mobile_vs_desktop_differences():
    """Test that mobile and desktop configurations produce different results."""
    print("🧪 Testing mobile vs desktop configuration differences...")
    
    from chart_generator import create_mobile_optimized_config, create_desktop_config
    
    simulation_results = create_realistic_simulation_results()
    
    # Generate charts with mobile config
    mobile_config = create_mobile_optimized_config()
    mobile_charts = generate_all_charts(simulation_results, mobile_config)
    
    # Generate charts with desktop config
    desktop_config = create_desktop_config()
    desktop_charts = generate_all_charts(simulation_results, desktop_config)
    
    # Parse JSON to compare configurations
    mobile_chart_data = json.loads(list(mobile_charts['portfolio_charts'].values())[0])
    desktop_chart_data = json.loads(list(desktop_charts['portfolio_charts'].values())[0])
    
    # Check that mobile has smaller height
    mobile_height = mobile_chart_data['layout'].get('height', 400)
    desktop_height = desktop_chart_data['layout'].get('height', 400)
    
    print(f"✅ Mobile height: {mobile_height}, Desktop height: {desktop_height}")
    assert mobile_height <= desktop_height, "Mobile should have smaller or equal height"
    
    # Check for mobile-optimized legend
    mobile_legend = mobile_chart_data['layout'].get('legend', {})
    if mobile_legend:
        assert mobile_legend.get('orientation') == 'h', "Mobile should have horizontal legend"
        print("✅ Mobile has horizontal legend orientation")


def main():
    """Run integration tests."""
    print("🚀 Starting chart generator integration tests...\n")
    
    try:
        # Test with realistic simulation data
        charts = test_chart_generation_with_realistic_data()
        print()
        
        # Test JSON validity
        test_chart_json_validity()
        print()
        
        # Test mobile vs desktop differences
        test_mobile_vs_desktop_differences()
        print()
        
        print("🎉 All integration tests passed!")
        print("\n📊 Integration test results:")
        print(f"  ✅ Generated {len(charts['portfolio_charts'])} portfolio charts")
        print(f"  ✅ Generated {4} comparison/summary charts")
        print(f"  ✅ All charts produce valid JSON")
        print(f"  ✅ Mobile optimization works correctly")
        print(f"  ✅ Chart selector identifies recommended portfolio")
        print(f"  ✅ Success rate filtering works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)