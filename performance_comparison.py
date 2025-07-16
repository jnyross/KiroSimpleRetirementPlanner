#!/usr/bin/env python3
"""
Performance comparison script between original and optimized simulators.

This script compares the performance of the original and optimized Monte Carlo
simulators to demonstrate the improvements achieved.
"""

import time
import psutil
import os
from typing import Dict, Any
import numpy as np

from src.models import UserInput
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager
from src.tax_calculator import UKTaxCalculator
from src.guard_rails import GuardRailsEngine
from src.simulator import MonteCarloSimulator, create_simulator


def measure_performance(simulator, user_input: UserInput, allocation, retirement_age: int, 
                       test_name: str) -> Dict[str, Any]:
    """
    Measure performance metrics for a simulator.
    
    Args:
        simulator: Simulator instance to test
        user_input: User input parameters
        allocation: Portfolio allocation
        retirement_age: Retirement age to test
        test_name: Name of the test for reporting
        
    Returns:
        Dictionary with performance metrics
    """
    print(f"🔬 Testing {test_name}...")
    
    # Measure memory before
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    
    # Time the simulation
    start_time = time.time()
    
    try:
        result = simulator.run_simulation_for_retirement_age(
            user_input, allocation, retirement_age, show_progress=False
        )
        
        end_time = time.time()
        success = True
        
        # Measure memory after
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Calculate performance metrics
        duration = end_time - start_time
        num_sims = simulator.num_simulations
        sims_per_second = num_sims / duration if duration > 0 else 0
        
        metrics = {
            'success': success,
            'duration': duration,
            'sims_per_second': sims_per_second,
            'memory_used': memory_used,
            'success_rate': result.success_rate,
            'num_simulations': num_sims,
            'memory_per_sim': memory_used / num_sims * 1000 if num_sims > 0 else 0  # KB per sim
        }
        
        print(f"   ✅ Duration: {duration:.2f}s ({sims_per_second:.0f} sims/sec)")
        print(f"   💾 Memory: {memory_used:.1f} MB ({metrics['memory_per_sim']:.2f} KB/sim)")
        print(f"   📊 Success rate: {result.success_rate:.1%}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        metrics = {
            'success': False,
            'error': str(e),
            'duration': 0,
            'sims_per_second': 0,
            'memory_used': 0,
            'success_rate': 0,
            'num_simulations': 0,
            'memory_per_sim': 0
        }
    
    return metrics


def compare_simulators():
    """Compare performance between original and optimized simulators."""
    print("🚀 Monte Carlo Simulator Performance Comparison")
    print("=" * 80)
    
    # Initialize components
    print("📊 Initializing components...")
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    tax_calculator = UKTaxCalculator()
    guard_rails_engine = GuardRailsEngine()
    
    # Test parameters
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=2000,
        desired_annual_income=30000
    )
    
    allocation = portfolio_manager.get_allocation("50% Equities/50% Bonds")
    retirement_age = 60
    
    print(f"📋 Test Parameters:")
    print(f"   User: Age {user_input.current_age}, £{user_input.current_savings:,} savings")
    print(f"   Portfolio: {allocation.name}")
    print(f"   Retirement age: {retirement_age}")
    print()
    
    # Test different simulation sizes
    test_sizes = [1000, 5000, 10000]
    results = {}
    
    for num_sims in test_sizes:
        print(f"🎲 Testing with {num_sims:,} simulations")
        print("-" * 50)
        
        # Test original simulator
        original_simulator = MonteCarloSimulator(
            data_manager, portfolio_manager, tax_calculator, 
            guard_rails_engine, num_sims
        )
        
        original_metrics = measure_performance(
            original_simulator, user_input, allocation, retirement_age,
            f"Original Simulator ({num_sims:,} sims)"
        )
        
        # Test optimized simulator
        optimized_simulator = create_simulator(
            data_manager, portfolio_manager, tax_calculator, 
            guard_rails_engine, num_sims, use_optimized=True,
            batch_size=min(1000, num_sims), use_parallel=False  # Disable parallel for fair comparison
        )
        
        optimized_metrics = measure_performance(
            optimized_simulator, user_input, allocation, retirement_age,
            f"Optimized Simulator ({num_sims:,} sims)"
        )
        
        # Calculate improvements
        if original_metrics['success'] and optimized_metrics['success']:
            speed_improvement = optimized_metrics['sims_per_second'] / original_metrics['sims_per_second']
            memory_improvement = original_metrics['memory_used'] / optimized_metrics['memory_used'] if optimized_metrics['memory_used'] > 0 else 1
            
            print(f"   📈 Performance Improvements:")
            print(f"      Speed: {speed_improvement:.1f}x faster")
            print(f"      Memory: {memory_improvement:.1f}x more efficient")
            print(f"      Time saved: {original_metrics['duration'] - optimized_metrics['duration']:.1f}s")
        
        results[num_sims] = {
            'original': original_metrics,
            'optimized': optimized_metrics
        }
        
        print()
    
    return results


def test_parallel_processing():
    """Test parallel processing performance."""
    print("🔄 Parallel Processing Performance Test")
    print("=" * 60)
    
    # Initialize components
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    tax_calculator = UKTaxCalculator()
    guard_rails_engine = GuardRailsEngine()
    
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=2000,
        desired_annual_income=30000
    )
    
    num_sims = 5000  # Moderate size for parallel testing
    
    print(f"📋 Test Parameters:")
    print(f"   Simulations: {num_sims:,}")
    print(f"   CPU cores available: {os.cpu_count()}")
    print()
    
    # Test sequential processing
    print("🔄 Testing sequential processing...")
    sequential_simulator = create_simulator(
        data_manager, portfolio_manager, tax_calculator, 
        guard_rails_engine, num_sims, use_optimized=True,
        use_parallel=False
    )
    
    start_time = time.time()
    try:
        sequential_results = sequential_simulator.run_parallel_portfolio_analysis(
            user_input, show_progress=False
        )
        sequential_time = time.time() - start_time
        sequential_success = True
        print(f"   ✅ Sequential: {sequential_time:.1f}s ({len(sequential_results)} portfolios)")
    except Exception as e:
        print(f"   ❌ Sequential failed: {str(e)}")
        sequential_time = 0
        sequential_success = False
    
    # Test parallel processing
    print("🚀 Testing parallel processing...")
    parallel_simulator = create_simulator(
        data_manager, portfolio_manager, tax_calculator, 
        guard_rails_engine, num_sims, use_optimized=True,
        use_parallel=True
    )
    
    start_time = time.time()
    try:
        parallel_results = parallel_simulator.run_parallel_portfolio_analysis(
            user_input, show_progress=False
        )
        parallel_time = time.time() - start_time
        parallel_success = True
        print(f"   ✅ Parallel: {parallel_time:.1f}s ({len(parallel_results)} portfolios)")
    except Exception as e:
        print(f"   ❌ Parallel failed: {str(e)}")
        parallel_time = 0
        parallel_success = False
    
    # Calculate improvement
    if sequential_success and parallel_success and parallel_time > 0:
        parallel_speedup = sequential_time / parallel_time
        print(f"\n📈 Parallel Processing Results:")
        print(f"   Sequential time: {sequential_time:.1f}s")
        print(f"   Parallel time: {parallel_time:.1f}s")
        print(f"   Speedup: {parallel_speedup:.1f}x")
        print(f"   Time saved: {sequential_time - parallel_time:.1f}s")
        
        # Efficiency calculation
        theoretical_max = os.cpu_count()
        efficiency = (parallel_speedup / theoretical_max) * 100
        print(f"   Parallel efficiency: {efficiency:.1f}% (vs {theoretical_max} cores)")
    
    print()


def test_memory_management():
    """Test memory management with different batch sizes."""
    print("💾 Memory Management Test")
    print("=" * 40)
    
    # Initialize components
    data_manager = HistoricalDataManager()
    data_manager.load_all_data()
    
    portfolio_manager = PortfolioManager(data_manager)
    tax_calculator = UKTaxCalculator()
    guard_rails_engine = GuardRailsEngine()
    
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=2000,
        desired_annual_income=30000
    )
    
    allocation = portfolio_manager.get_allocation("50% Equities/50% Bonds")
    retirement_age = 60
    
    num_sims = 10000
    batch_sizes = [500, 1000, 2000, 5000]
    
    print(f"📋 Test Parameters:")
    print(f"   Simulations: {num_sims:,}")
    print(f"   Testing batch sizes: {batch_sizes}")
    print()
    
    for batch_size in batch_sizes:
        print(f"🔬 Testing batch size: {batch_size:,}")
        
        simulator = create_simulator(
            data_manager, portfolio_manager, tax_calculator, 
            guard_rails_engine, num_sims, use_optimized=True,
            batch_size=batch_size, use_parallel=False
        )
        
        # Get memory estimate
        if hasattr(simulator, 'get_memory_usage_estimate'):
            memory_estimate = simulator.get_memory_usage_estimate()
            print(f"   Estimated peak memory: {memory_estimate['estimated_peak_mb']:.1f} MB")
            print(f"   Batch memory: {memory_estimate['batch_memory_mb']:.1f} MB")
        
        # Measure actual performance
        metrics = measure_performance(
            simulator, user_input, allocation, retirement_age,
            f"Batch size {batch_size:,}"
        )
        
        print()


def generate_performance_report(results: Dict):
    """Generate a comprehensive performance report."""
    print("📊 Performance Analysis Summary")
    print("=" * 60)
    
    print("\n🎯 Speed Improvements by Simulation Size:")
    print(f"{'Simulations':<12} {'Original (s)':<12} {'Optimized (s)':<13} {'Speedup':<10}")
    print("-" * 50)
    
    total_speedup = 0
    valid_tests = 0
    
    for num_sims, data in results.items():
        if data['original']['success'] and data['optimized']['success']:
            orig_time = data['original']['duration']
            opt_time = data['optimized']['duration']
            speedup = orig_time / opt_time if opt_time > 0 else 0
            
            print(f"{num_sims:<12,} {orig_time:<12.2f} {opt_time:<13.2f} {speedup:<10.1f}x")
            
            total_speedup += speedup
            valid_tests += 1
    
    if valid_tests > 0:
        avg_speedup = total_speedup / valid_tests
        print(f"\nAverage speedup: {avg_speedup:.1f}x")
    
    print("\n💾 Memory Efficiency:")
    print(f"{'Simulations':<12} {'Original (MB)':<14} {'Optimized (MB)':<15} {'Improvement':<12}")
    print("-" * 55)
    
    for num_sims, data in results.items():
        if data['original']['success'] and data['optimized']['success']:
            orig_mem = data['original']['memory_used']
            opt_mem = data['optimized']['memory_used']
            improvement = orig_mem / opt_mem if opt_mem > 0 else 1
            
            print(f"{num_sims:<12,} {orig_mem:<14.1f} {opt_mem:<15.1f} {improvement:<12.1f}x")
    
    print("\n🔧 Optimization Summary:")
    print("   ✅ Vectorized operations implemented")
    print("   ✅ Batch processing for memory management")
    print("   ✅ Pre-computed historical data arrays")
    print("   ✅ Optimized tax calculations")
    print("   ✅ Parallel processing support")
    print("   ✅ Memory usage estimation")


def main():
    """Run comprehensive performance comparison."""
    try:
        # Run performance comparison
        results = compare_simulators()
        
        # Test parallel processing
        test_parallel_processing()
        
        # Test memory management
        test_memory_management()
        
        # Generate report
        generate_performance_report(results)
        
        print("\n✅ Performance comparison complete!")
        
    except Exception as e:
        print(f"❌ Error during performance comparison: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()