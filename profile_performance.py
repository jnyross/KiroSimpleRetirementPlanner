#!/usr/bin/env python3
"""
Performance profiling script for the Monte Carlo simulator.

This script profiles the current implementation to identify bottlenecks
and measure performance improvements.
"""

import cProfile
import pstats
import time
import numpy as np
from typing import Dict, Any
import psutil
import os
from src.models import UserInput
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager
from src.tax_calculator import UKTaxCalculator
from src.guard_rails import GuardRailsEngine
from src.simulator import MonteCarloSimulator


def profile_simulation_performance():
    """Profile the Monte Carlo simulation performance."""
    print("🔍 Profiling Monte Carlo Simulation Performance")
    print("=" * 60)
    
    # Initialize components
    print("📊 Initializing components...")
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    tax_calculator = UKTaxCalculator()
    guard_rails_engine = GuardRailsEngine()
    
    # Test with different simulation sizes
    test_sizes = [100, 1000, 5000, 10000]
    
    # Sample user input
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=2000,
        desired_annual_income=30000
    )
    
    # Test portfolio allocation
    allocation = portfolio_manager.get_allocation("50% Equities/50% Bonds")
    retirement_age = 60
    
    print(f"📋 Test Parameters:")
    print(f"   User: Age {user_input.current_age}, £{user_input.current_savings:,} savings")
    print(f"   Portfolio: {allocation.name}")
    print(f"   Retirement age: {retirement_age}")
    print()
    
    results = {}
    
    for num_sims in test_sizes:
        print(f"🎲 Testing {num_sims:,} simulations...")
        
        # Create simulator with specific number of simulations
        simulator = MonteCarloSimulator(
            data_manager, portfolio_manager, tax_calculator, 
            guard_rails_engine, num_sims
        )
        
        # Measure memory before
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Time the simulation
        start_time = time.time()
        
        # Run simulation
        result = simulator.run_simulation_for_retirement_age(
            user_input, allocation, retirement_age, show_progress=False
        )
        
        end_time = time.time()
        
        # Measure memory after
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Calculate performance metrics
        duration = end_time - start_time
        sims_per_second = num_sims / duration if duration > 0 else 0
        
        results[num_sims] = {
            'duration': duration,
            'sims_per_second': sims_per_second,
            'memory_used': memory_used,
            'success_rate': result.success_rate
        }
        
        print(f"   ⏱️  Duration: {duration:.2f}s ({sims_per_second:.0f} sims/sec)")
        print(f"   💾 Memory used: {memory_used:.1f} MB")
        print(f"   ✅ Success rate: {result.success_rate:.1%}")
        print()
    
    return results


def profile_detailed_bottlenecks():
    """Profile detailed bottlenecks using cProfile."""
    print("🔬 Detailed Performance Profiling")
    print("=" * 60)
    
    # Initialize components
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    tax_calculator = UKTaxCalculator()
    guard_rails_engine = GuardRailsEngine()
    simulator = MonteCarloSimulator(
        data_manager, portfolio_manager, tax_calculator, 
        guard_rails_engine, 1000  # Moderate size for profiling
    )
    
    # Sample user input
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=2000,
        desired_annual_income=30000
    )
    
    allocation = portfolio_manager.get_allocation("50% Equities/50% Bonds")
    retirement_age = 60
    
    print("🎯 Running detailed profiling (1,000 simulations)...")
    
    # Profile the simulation
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = simulator.run_simulation_for_retirement_age(
        user_input, allocation, retirement_age, show_progress=False
    )
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    
    print("\n📊 Top 20 Functions by Cumulative Time:")
    stats.print_stats(20)
    
    print("\n📊 Top 20 Functions by Total Time:")
    stats.sort_stats('tottime')
    stats.print_stats(20)
    
    return stats


def analyze_memory_usage():
    """Analyze memory usage patterns."""
    print("💾 Memory Usage Analysis")
    print("=" * 60)
    
    # Initialize components
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    tax_calculator = UKTaxCalculator()
    guard_rails_engine = GuardRailsEngine()
    
    # Sample user input
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=2000,
        desired_annual_income=30000
    )
    
    allocation = portfolio_manager.get_allocation("50% Equities/50% Bonds")
    retirement_age = 60
    
    process = psutil.Process(os.getpid())
    
    # Test different simulation sizes and measure memory
    test_sizes = [100, 500, 1000, 2500, 5000, 10000]
    memory_usage = {}
    
    for num_sims in test_sizes:
        print(f"📊 Testing memory usage with {num_sims:,} simulations...")
        
        # Measure baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024
        
        # Create simulator
        simulator = MonteCarloSimulator(
            data_manager, portfolio_manager, tax_calculator, 
            guard_rails_engine, num_sims
        )
        
        # Run simulation and measure peak memory
        peak_memory = baseline_memory
        
        def memory_monitor():
            nonlocal peak_memory
            current_memory = process.memory_info().rss / 1024 / 1024
            if current_memory > peak_memory:
                peak_memory = current_memory
        
        # Run simulation with memory monitoring
        start_time = time.time()
        result = simulator.run_simulation_for_retirement_age(
            user_input, allocation, retirement_age, show_progress=False
        )
        end_time = time.time()
        
        # Final memory measurement
        final_memory = process.memory_info().rss / 1024 / 1024
        
        memory_usage[num_sims] = {
            'baseline': baseline_memory,
            'peak': peak_memory,
            'final': final_memory,
            'increase': final_memory - baseline_memory,
            'duration': end_time - start_time
        }
        
        print(f"   Baseline: {baseline_memory:.1f} MB")
        print(f"   Peak: {peak_memory:.1f} MB")
        print(f"   Final: {final_memory:.1f} MB")
        print(f"   Increase: {final_memory - baseline_memory:.1f} MB")
        print(f"   Memory per simulation: {(final_memory - baseline_memory) / num_sims * 1000:.2f} KB/sim")
        print()
    
    return memory_usage


def benchmark_vectorization_opportunities():
    """Benchmark potential vectorization improvements."""
    print("⚡ Vectorization Opportunities Analysis")
    print("=" * 60)
    
    # Test bootstrap sampling performance
    print("🎲 Testing bootstrap sampling performance...")
    
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    portfolio_manager = PortfolioManager(data_manager)
    allocation = portfolio_manager.get_allocation("50% Equities/50% Bonds")
    
    # Test different approaches to bootstrap sampling
    num_years = 30
    num_simulations = 10000
    
    print(f"   Parameters: {num_years} years, {num_simulations:,} simulations")
    
    # Current approach (one simulation at a time)
    start_time = time.time()
    for _ in range(100):  # Sample of simulations
        returns = portfolio_manager.generate_bootstrap_returns(allocation, num_years, 1)
    current_time = time.time() - start_time
    
    # Vectorized approach (all simulations at once)
    start_time = time.time()
    returns_vectorized = portfolio_manager.generate_bootstrap_returns(allocation, num_years, 100)
    vectorized_time = time.time() - start_time
    
    print(f"   Current approach (100 individual calls): {current_time:.3f}s")
    print(f"   Vectorized approach (1 batch call): {vectorized_time:.3f}s")
    print(f"   Speedup: {current_time / vectorized_time:.1f}x")
    print()
    
    # Test array operations vs loops
    print("🔢 Testing array operations vs loops...")
    
    # Generate test data
    portfolio_values = np.random.uniform(100000, 500000, 10000)
    returns = np.random.normal(0.07, 0.15, 10000)
    withdrawals = np.random.uniform(20000, 40000, 10000)
    
    # Loop-based approach
    start_time = time.time()
    results_loop = []
    for i in range(len(portfolio_values)):
        new_value = portfolio_values[i] * (1 + returns[i]) - withdrawals[i]
        results_loop.append(max(0, new_value))
    loop_time = time.time() - start_time
    
    # Vectorized approach
    start_time = time.time()
    results_vectorized = np.maximum(0, portfolio_values * (1 + returns) - withdrawals)
    vectorized_time = time.time() - start_time
    
    print(f"   Loop-based approach: {loop_time:.3f}s")
    print(f"   Vectorized approach: {vectorized_time:.3f}s")
    print(f"   Speedup: {loop_time / vectorized_time:.1f}x")
    print()
    
    return {
        'bootstrap_speedup': current_time / vectorized_time if vectorized_time > 0 else 0,
        'array_ops_speedup': loop_time / vectorized_time if vectorized_time > 0 else 0
    }


def main():
    """Run comprehensive performance analysis."""
    print("🚀 Monte Carlo Simulator Performance Analysis")
    print("=" * 80)
    print()
    
    try:
        # 1. Basic performance profiling
        perf_results = profile_simulation_performance()
        
        # 2. Detailed bottleneck analysis
        detailed_stats = profile_detailed_bottlenecks()
        
        # 3. Memory usage analysis
        memory_results = analyze_memory_usage()
        
        # 4. Vectorization opportunities
        vector_results = benchmark_vectorization_opportunities()
        
        # Summary report
        print("📋 Performance Analysis Summary")
        print("=" * 60)
        
        print("\n🎯 Simulation Performance:")
        for num_sims, metrics in perf_results.items():
            print(f"   {num_sims:,} sims: {metrics['sims_per_second']:.0f} sims/sec, "
                  f"{metrics['memory_used']:.1f} MB")
        
        print(f"\n⚡ Vectorization Potential:")
        print(f"   Bootstrap sampling speedup: {vector_results['bootstrap_speedup']:.1f}x")
        print(f"   Array operations speedup: {vector_results['array_ops_speedup']:.1f}x")
        
        print(f"\n💾 Memory Efficiency:")
        if 10000 in memory_results:
            mem_per_sim = memory_results[10000]['increase'] / 10000 * 1000
            print(f"   Memory per simulation: {mem_per_sim:.2f} KB")
        
        print("\n🔧 Optimization Recommendations:")
        
        # Performance recommendations
        if perf_results.get(10000, {}).get('sims_per_second', 0) < 1000:
            print("   ⚠️  Simulation speed is below 1,000 sims/sec - consider optimization")
        
        if vector_results['bootstrap_speedup'] > 2:
            print("   ✅ Bootstrap sampling can be significantly optimized with vectorization")
        
        if vector_results['array_ops_speedup'] > 5:
            print("   ✅ Array operations show high vectorization potential")
        
        # Memory recommendations
        if 10000 in memory_results and memory_results[10000]['increase'] > 500:
            print("   ⚠️  High memory usage detected - consider batch processing")
        
        print("\n✅ Performance analysis complete!")
        
    except Exception as e:
        print(f"❌ Error during performance analysis: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()