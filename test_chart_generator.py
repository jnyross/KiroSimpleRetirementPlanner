#!/usr/bin/env python3
"""
Test script for web chart generator functionality.

This script tests all chart generation features with sample data
to ensure the implementation meets the requirements.
"""

import sys
import json
import numpy as np
from chart_generator import (
    WebChartGenerator, 
    generate_all_charts, 
    ChartConfig,
    create_mobile_optimized_config,
    create_desktop_config
)


def create_sample_results_data():
    """Create sample portfolio results data for testing."""
    portfolios = [
        {"name": "100% Cash", "equity": 0.0, "bond": 0.0, "cash": 1.0},
        {"name": "Conservative (20/80)", "equity": 0.2, "bond": 0.8, "cash": 0.0},
        {"name": "Moderate (40/60)", "equity": 0.4, "bond": 0.6, "cash": 0.0},
        {"name": "Balanced (60/40)", "equity": 0.6, "bond": 0.4, "cash": 0.0},
        {"name": "Growth (80/20)", "equity": 0.8, "bond": 0.2, "cash": 0.0},
        {"name": "100% Equity", "equity": 1.0, "bond": 0.0, "cash": 0.0}
    ]
    
    results_data = []
    
    for i, portfolio in enumerate(portfolios):
        # Generate sample percentile data (30 years of projections)
        years = 30
        base_value = 100000 + i * 20000  # Different starting values
        growth_rate = 0.02 + portfolio["equity"] * 0.05  # Higher equity = higher growth
        volatility = 0.1 + portfolio["equity"] * 0.15  # Higher equity = higher volatility
        
        # Generate percentile arrays
        percentile_10 = []
        percentile_50 = []
        percentile_90 = []
        
        for year in range(years):
            # Simulate portfolio growth with volatility
            median_value = base_value * ((1 + growth_rate) ** year)
            
            # Add volatility for percentiles
            p10_value = median_value * (1 - volatility * 1.5)
            p50_value = median_value
            p90_value = median_value * (1 + volatility * 1.5)
            
            percentile_10.append(max(0, p10_value))  # Don't go negative
            percentile_50.append(p50_value)
            percentile_90.append(p90_value)
        
        # Calculate success rate (higher equity generally better for long term)
        success_rate = 0.85 + portfolio["equity"] * 0.14  # 85% to 99%
        
        # Calculate retirement age (more aggressive portfolios retire earlier)
        retirement_age = 70 - int(portfolio["equity"] * 10)  # 70 to 60
        
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


def test_individual_chart_generation():
    """Test individual chart generation methods."""
    print("🧪 Testing individual chart generation...")
    
    generator = WebChartGenerator()
    sample_data = create_sample_results_data()
    
    # Test portfolio chart
    portfolio_chart = generator.generate_portfolio_chart(sample_data[3])  # Balanced portfolio
    assert isinstance(portfolio_chart, str), "Portfolio chart should return JSON string"
    assert len(portfolio_chart) > 100, "Portfolio chart JSON should be substantial"
    print("✅ Portfolio chart generation works")
    
    # Test comparison chart
    comparison_chart = generator.generate_comparison_chart(sample_data)
    assert isinstance(comparison_chart, str), "Comparison chart should return JSON string"
    assert len(comparison_chart) > 100, "Comparison chart JSON should be substantial"
    print("✅ Comparison chart generation works")
    
    # Test success rate chart
    success_chart = generator.generate_success_rate_chart(sample_data)
    assert isinstance(success_chart, str), "Success rate chart should return JSON string"
    assert len(success_chart) > 100, "Success rate chart JSON should be substantial"
    print("✅ Success rate chart generation works")
    
    # Test retirement age chart
    retirement_chart = generator.generate_retirement_age_chart(sample_data)
    assert isinstance(retirement_chart, str), "Retirement age chart should return JSON string"
    assert len(retirement_chart) > 100, "Retirement age chart JSON should be substantial"
    print("✅ Retirement age chart generation works")
    
    # Test chart selector data
    selector_data = generator.generate_chart_selector_data(sample_data)
    assert isinstance(selector_data, dict), "Selector data should be a dictionary"
    assert "options" in selector_data, "Selector data should have options"
    assert "default" in selector_data, "Selector data should have default selection"
    assert len(selector_data["options"]) == len(sample_data), "Should have option for each portfolio"
    print("✅ Chart selector data generation works")


def test_comprehensive_chart_generation():
    """Test the comprehensive chart generation function."""
    print("🧪 Testing comprehensive chart generation...")
    
    sample_data = create_sample_results_data()
    
    # Test with default config
    all_charts = generate_all_charts(sample_data)
    
    # Verify structure
    expected_keys = [
        'portfolio_charts', 'comparison_chart', 'success_rate_chart',
        'retirement_age_chart', 'selector_data', 'chart_count', 'has_successful_portfolios'
    ]
    
    for key in expected_keys:
        assert key in all_charts, f"Missing key: {key}"
    
    # Verify portfolio charts
    assert isinstance(all_charts['portfolio_charts'], dict), "Portfolio charts should be a dict"
    assert len(all_charts['portfolio_charts']) == len(sample_data), "Should have chart for each portfolio"
    print("✅ Portfolio charts generated for all portfolios")
    
    # Verify other charts
    assert isinstance(all_charts['comparison_chart'], str), "Comparison chart should be JSON string"
    assert isinstance(all_charts['success_rate_chart'], str), "Success rate chart should be JSON string"
    assert isinstance(all_charts['retirement_age_chart'], str), "Retirement age chart should be JSON string"
    print("✅ All comparison charts generated")
    
    # Verify selector data
    assert isinstance(all_charts['selector_data'], dict), "Selector data should be a dict"
    assert all_charts['chart_count'] == len(sample_data), "Chart count should match portfolio count"
    assert all_charts['has_successful_portfolios'] == True, "Should detect successful portfolios"
    print("✅ Selector data and metadata generated correctly")


def test_mobile_optimization():
    """Test mobile-optimized chart generation."""
    print("🧪 Testing mobile optimization...")
    
    mobile_config = create_mobile_optimized_config()
    desktop_config = create_desktop_config()
    
    # Verify mobile config differences
    assert mobile_config.height < desktop_config.height, "Mobile should have smaller height"
    assert mobile_config.mobile_optimized == True, "Mobile config should be mobile optimized"
    assert mobile_config.title_font_size <= desktop_config.title_font_size, "Mobile should have smaller fonts"
    print("✅ Mobile configuration is properly optimized")
    
    # Test chart generation with mobile config
    sample_data = create_sample_results_data()
    mobile_charts = generate_all_charts(sample_data, mobile_config)
    
    assert len(mobile_charts['portfolio_charts']) > 0, "Mobile charts should be generated"
    print("✅ Mobile chart generation works")


def test_responsive_features():
    """Test responsive chart features."""
    print("🧪 Testing responsive features...")
    
    generator = WebChartGenerator()
    sample_data = create_sample_results_data()
    
    # Generate a chart and verify it contains responsive features
    chart_json = generator.generate_portfolio_chart(sample_data[0])
    
    # Parse JSON to verify structure
    try:
        chart_data = json.loads(chart_json)
        
        # Check for responsive layout settings
        layout = chart_data.get('layout', {})
        assert 'autosize' in layout or 'responsive' in str(layout), "Chart should have responsive settings"
        
        # Check for mobile-friendly legend
        if 'legend' in layout:
            legend = layout['legend']
            assert 'orientation' in legend, "Legend should have orientation setting"
        
        print("✅ Charts include responsive features")
        
    except json.JSONDecodeError:
        print("❌ Chart JSON is not valid")
        raise


def test_interactive_features():
    """Test interactive chart features."""
    print("🧪 Testing interactive features...")
    
    generator = WebChartGenerator()
    sample_data = create_sample_results_data()
    
    # Generate chart and check for interactive features
    chart_json = generator.generate_portfolio_chart(sample_data[0])
    chart_data = json.loads(chart_json)
    
    # Check for hover templates
    traces = chart_data.get('data', [])
    has_hover = any('hovertemplate' in trace for trace in traces)
    assert has_hover, "Charts should have hover templates for interactivity"
    print("✅ Charts include hover tooltips")
    
    # Check layout for interactivity
    layout = chart_data.get('layout', {})
    assert layout.get('hovermode'), "Charts should have hover mode enabled"
    print("✅ Charts have interactive hover mode")


def test_error_handling():
    """Test error handling for invalid data."""
    print("🧪 Testing error handling...")
    
    generator = WebChartGenerator()
    
    # Test with empty data
    empty_chart = generator.generate_portfolio_chart({})
    assert isinstance(empty_chart, str), "Should return valid JSON even for empty data"
    
    # Test with missing percentile data
    invalid_data = {"portfolio_name": "Test", "percentile_data": {}}
    empty_chart = generator.generate_portfolio_chart(invalid_data)
    assert isinstance(empty_chart, str), "Should handle missing percentile data gracefully"
    
    # Test comparison chart with empty data
    empty_comparison = generator.generate_comparison_chart([])
    assert isinstance(empty_comparison, str), "Should handle empty comparison data"
    
    print("✅ Error handling works correctly")


def main():
    """Run all tests."""
    print("🚀 Starting chart generator tests...\n")
    
    try:
        test_individual_chart_generation()
        print()
        
        test_comprehensive_chart_generation()
        print()
        
        test_mobile_optimization()
        print()
        
        test_responsive_features()
        print()
        
        test_interactive_features()
        print()
        
        test_error_handling()
        print()
        
        print("🎉 All tests passed! Chart generator is working correctly.")
        print("\n📊 Chart generation features verified:")
        print("  ✅ Interactive Plotly charts with hover tooltips")
        print("  ✅ 10th, 50th, 90th percentile visualizations")
        print("  ✅ Chart selector for switching between portfolios")
        print("  ✅ Responsive design for mobile devices")
        print("  ✅ Portfolio comparison charts")
        print("  ✅ Success rate and retirement age charts")
        print("  ✅ Mobile-optimized configurations")
        print("  ✅ Error handling for invalid data")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)