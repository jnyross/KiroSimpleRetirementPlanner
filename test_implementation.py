#!/usr/bin/env python3
"""
Test script to verify the current implementation works correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models import UserInput, PortfolioAllocation, GuardRailsThresholds
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager
from src.tax_calculator import UKTaxCalculator
from src.guard_rails import GuardRailsEngine
from src.simulator import MonteCarloSimulator

def test_data_manager():
    print("Testing HistoricalDataManager...")
    data_manager = HistoricalDataManager()
    try:
        data_manager.load_all_data()
        print("✓ Data loaded successfully")
        
        if data_manager.validate_data():
            print("✓ Data validation passed")
        else:
            print("✗ Data validation failed")
            
        # Test bootstrap sampling
        allocation = PortfolioAllocation("Test", 0.6, 0.4, 0.0)
        returns = data_manager.get_bootstrap_returns(allocation, 10)
        print(f"✓ Bootstrap sampling works: {len(returns)} returns generated")
        
    except Exception as e:
        print(f"✗ Data manager error: {e}")

def test_tax_calculator():
    print("\nTesting UKTaxCalculator...")
    tax_calc = UKTaxCalculator()
    
    # Test tax calculation
    gross_income = 50000
    tax = tax_calc.calculate_tax(gross_income)
    net_income = tax_calc.calculate_net_income(gross_income)
    print(f"✓ Tax on £{gross_income}: £{tax:.2f}, Net: £{net_income:.2f}")
    
    # Test gross needed calculation
    desired_net = 30000
    gross_needed = tax_calc.calculate_gross_needed(desired_net)
    print(f"✓ Gross needed for £{desired_net} net: £{gross_needed:.2f}")

def test_portfolio_manager():
    print("\nTesting PortfolioManager...")
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    allocations = portfolio_manager.get_all_allocations()
    print(f"✓ {len(allocations)} portfolio allocations created")
    
    # Test portfolio statistics
    allocation = allocations["50% Equities/50% Bonds"]
    stats = portfolio_manager.get_portfolio_statistics(allocation)
    print(f"✓ 50/50 Portfolio stats: Return={stats['expected_return']:.3f}, Vol={stats['volatility']:.3f}")

def test_guard_rails():
    print("\nTesting GuardRailsEngine...")
    guard_rails = GuardRailsEngine()
    
    # Test scenarios
    initial_value = 100000
    base_withdrawal = 4000
    
    scenarios = guard_rails.test_guard_rails_scenarios(initial_value, base_withdrawal)
    for scenario, (withdrawal, reason) in scenarios.items():
        print(f"✓ {scenario}: £{withdrawal:.0f} ({reason})")

def test_simulator():
    print("\nTesting MonteCarloSimulator...")
    # Initialize all components
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    tax_calculator = UKTaxCalculator()
    guard_rails = GuardRailsEngine()
    
    # Use fewer simulations for testing
    simulator = MonteCarloSimulator(
        data_manager, portfolio_manager, tax_calculator, guard_rails, 
        num_simulations=100
    )
    
    # Test user input
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=1000,
        desired_annual_income=30000
    )
    
    print(f"✓ User input created: Age {user_input.current_age}, Savings £{user_input.current_savings}")
    
    # Test single simulation
    allocation = portfolio_manager.get_allocation("50% Equities/50% Bonds")
    try:
        success, final_value, portfolio_values = simulator.run_single_simulation(
            user_input, allocation, 60
        )
        print(f"✓ Single simulation: Success={success}, Final value=£{final_value:.0f}")
        
        # Test simulation for retirement age
        result = simulator.run_simulation_for_retirement_age(user_input, allocation, 60)
        print(f"✓ Retirement at 60: Success rate={result.success_rate:.1%}")
        
    except Exception as e:
        print(f"✗ Simulation error: {e}")

def main():
    print("=== Testing Kiro Simple Retirement Planner ===\n")
    
    try:
        test_data_manager()
        test_tax_calculator()
        test_portfolio_manager()
        test_guard_rails()
        test_simulator()
        
        print("\n=== All tests completed ===")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()