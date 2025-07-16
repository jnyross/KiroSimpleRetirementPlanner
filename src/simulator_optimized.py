"""
Optimized Monte Carlo simulation engine for retirement planning.

This module implements performance-optimized Monte Carlo simulation logic using
vectorized operations and efficient memory management.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from .models import UserInput, PortfolioAllocation, SimulationResult, GuardRailsThresholds
from .data_manager import HistoricalDataManager
from .portfolio_manager import PortfolioManager
from .tax_calculator import UKTaxCalculator
from .guard_rails import GuardRailsEngine


class OptimizedMonteCarloSimulator:
    """Optimized Monte Carlo simulation engine for retirement planning."""
    
    def __init__(self, data_manager: HistoricalDataManager, 
                 portfolio_manager: PortfolioManager,
                 tax_calculator: UKTaxCalculator,
                 guard_rails_engine: GuardRailsEngine,
                 num_simulations: int = 10000,
                 batch_size: int = 1000,
                 use_parallel: bool = True):
        """
        Initialize the optimized Monte Carlo simulator.
        
        Args:
            data_manager: Historical data manager
            portfolio_manager: Portfolio manager
            tax_calculator: UK tax calculator
            guard_rails_engine: Guard rails engine
            num_simulations: Number of simulations to run
            batch_size: Batch size for memory management
            use_parallel: Whether to use parallel processing
        """
        self.data_manager = data_manager
        self.portfolio_manager = portfolio_manager
        self.tax_calculator = tax_calculator
        self.guard_rails_engine = guard_rails_engine
        self.num_simulations = num_simulations
        self.batch_size = min(batch_size, num_simulations)
        self.use_parallel = use_parallel and mp.cpu_count() > 1
        
        # Pre-compute historical data arrays for faster access
        self._precompute_historical_data()
        
    def _precompute_historical_data(self):
        """Pre-compute historical data arrays for vectorized operations."""
        if self.data_manager.equity_returns is None or self.data_manager.bond_returns is None:
            raise ValueError("Historical data not loaded")
        
        # Get available years with both equity and bond data
        equity_years = set(self.data_manager.equity_returns.index)
        bond_years = set(self.data_manager.bond_returns.index)
        self.available_years = np.array(list(equity_years & bond_years))
        
        if len(self.available_years) < 10:
            raise ValueError(f"Insufficient historical data. Need at least 10 years, have {len(self.available_years)}")
        
        # Pre-compute return arrays for faster lookup
        self.equity_returns_array = np.array([
            self.data_manager.equity_returns[year] for year in self.available_years
        ])
        self.bond_returns_array = np.array([
            self.data_manager.bond_returns[year] for year in self.available_years
        ])
        
        # Pre-compute tax brackets for vectorized tax calculations
        tax_brackets_list = self.tax_calculator.tax_brackets
        self.tax_brackets = np.array([
            (bracket.lower_limit, bracket.upper_limit, bracket.rate)
            for bracket in tax_brackets_list
        ])
    
    def _vectorized_bootstrap_returns(self, allocation: PortfolioAllocation,
                                    num_years: int, num_simulations: int) -> np.ndarray:
        """
        Generate vectorized bootstrap samples of portfolio returns.
        
        Args:
            allocation: Portfolio allocation
            num_years: Number of years for each simulation
            num_simulations: Number of simulations
            
        Returns:
            Array of shape (num_simulations, num_years) with portfolio returns
        """
        # Vectorized bootstrap sampling
        year_indices = np.random.choice(
            len(self.available_years), 
            size=(num_simulations, num_years), 
            replace=True
        )
        
        # Vectorized return calculation
        equity_returns = self.equity_returns_array[year_indices]
        bond_returns = self.bond_returns_array[year_indices]
        
        # Vectorized portfolio return calculation
        portfolio_returns = (
            allocation.equity_percentage * equity_returns +
            allocation.bond_percentage * bond_returns +
            allocation.cash_percentage * 0.0  # Cash returns 0% real
        )
        
        return portfolio_returns
    
    def _vectorized_tax_calculation(self, gross_incomes: np.ndarray) -> np.ndarray:
        """
        Vectorized tax calculation for multiple income values.
        
        Args:
            gross_incomes: Array of gross income values
            
        Returns:
            Array of corresponding tax amounts
        """
        taxes = np.zeros_like(gross_incomes)
        
        for lower, upper, rate in self.tax_brackets:
            # Calculate taxable amount in this bracket
            taxable = np.maximum(0, np.minimum(gross_incomes - lower, upper - lower))
            taxes += taxable * rate
        
        return taxes
    
    def _vectorized_gross_needed(self, desired_net_incomes: np.ndarray) -> np.ndarray:
        """
        Vectorized calculation of gross income needed for desired net income.
        
        Args:
            desired_net_incomes: Array of desired net income values
            
        Returns:
            Array of required gross income values
        """
        # Use binary search approach vectorized
        gross_estimates = desired_net_incomes * 1.3  # Initial estimate
        
        # Iterative refinement (vectorized Newton-Raphson style)
        for _ in range(10):  # Usually converges in 3-4 iterations
            taxes = self._vectorized_tax_calculation(gross_estimates)
            net_estimates = gross_estimates - taxes
            
            # Adjust estimates based on error
            error = desired_net_incomes - net_estimates
            adjustment = error / (1 - 0.25)  # Approximate marginal tax rate
            gross_estimates += adjustment
            
            # Check convergence
            if np.all(np.abs(error) < 1.0):  # £1 accuracy
                break
        
        return gross_estimates
    
    def run_vectorized_batch_simulation(self, user_input: UserInput,
                                      allocation: PortfolioAllocation,
                                      retirement_age: int,
                                      batch_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Run a batch of simulations using vectorized operations.
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            retirement_age: Age at retirement
            batch_size: Number of simulations in this batch
            
        Returns:
            Tuple of (success_flags, final_values, portfolio_trajectories)
        """
        years_to_retirement = retirement_age - user_input.current_age
        years_in_retirement = 100 - retirement_age
        
        # Pre-calculate retirement portfolio values (vectorized)
        if years_to_retirement > 0:
            # Generate accumulation returns
            accumulation_returns = self._vectorized_bootstrap_returns(
                allocation, years_to_retirement, batch_size
            )
            
            # Vectorized portfolio growth calculation
            portfolio_values = np.full(batch_size, user_input.current_savings, dtype=np.float64)
            annual_contribution = user_input.monthly_savings * 12
            
            for year in range(years_to_retirement):
                portfolio_values += annual_contribution
                portfolio_values *= (1 + accumulation_returns[:, year])
        else:
            portfolio_values = np.full(batch_size, user_input.current_savings, dtype=np.float64)
        
        # Calculate gross withdrawal needed (vectorized)
        desired_net = np.full(batch_size, user_input.desired_annual_income)
        gross_withdrawals = self._vectorized_gross_needed(desired_net)
        
        # Generate retirement returns
        retirement_returns = self._vectorized_bootstrap_returns(
            allocation, years_in_retirement, batch_size
        )
        
        # Vectorized retirement simulation
        portfolio_trajectories = np.zeros((batch_size, years_in_retirement + 1))
        portfolio_trajectories[:, 0] = portfolio_values
        
        initial_portfolio_values = portfolio_values.copy()
        
        for year in range(years_in_retirement):
            current_values = portfolio_trajectories[:, year]
            
            # Apply market returns (vectorized)
            current_values = np.maximum(0, current_values * (1 + retirement_returns[:, year]))
            
            # Calculate guard rails adjustments (vectorized)
            guard_rail_factors = self._vectorized_guard_rails(
                current_values, initial_portfolio_values, gross_withdrawals
            )
            
            # Apply withdrawals with guard rails
            adjusted_withdrawals = gross_withdrawals * guard_rail_factors
            portfolio_trajectories[:, year + 1] = np.maximum(0, current_values - adjusted_withdrawals)
        
        # Calculate success flags and final values
        success_flags = portfolio_trajectories[:, -1] > 0
        final_values = portfolio_trajectories[:, -1]
        
        return success_flags, final_values, portfolio_trajectories
    
    def _vectorized_guard_rails(self, current_values: np.ndarray,
                              initial_values: np.ndarray,
                              base_withdrawals: np.ndarray) -> np.ndarray:
        """
        Vectorized guard rails calculation.
        
        Args:
            current_values: Current portfolio values
            initial_values: Initial portfolio values at retirement
            base_withdrawals: Base withdrawal amounts
            
        Returns:
            Array of guard rail adjustment factors
        """
        # Calculate performance ratios
        performance_ratios = current_values / initial_values
        
        # Initialize adjustment factors
        factors = np.ones_like(performance_ratios)
        
        # Apply guard rails (vectorized conditions)
        # Severe guard rail: 25% below initial value
        severe_mask = performance_ratios < 0.75
        factors[severe_mask] = 0.8  # Reduce spending by 20%
        
        # Lower guard rail: 15% below initial value
        lower_mask = (performance_ratios < 0.85) & ~severe_mask
        factors[lower_mask] = 0.9  # Reduce spending by 10%
        
        # Upper guard rail: 20% above initial value (allow normal spending)
        # No adjustment needed for upper guard rail in this implementation
        
        return factors
    
    def validate_simulation_parameters(self, user_input: UserInput) -> bool:
        """
        Validate simulation parameters.
        
        Args:
            user_input: User input parameters
            
        Returns:
            True if parameters are valid, False otherwise
        """
        try:
            # Validate user input
            if not (18 <= user_input.current_age <= 80):
                return False
            if user_input.current_savings < 0:
                return False
            if user_input.monthly_savings < 0:
                return False
            if user_input.desired_annual_income <= 0:
                return False
            
            # Validate data availability
            if not self.data_manager.validate_data():
                return False
            
            return True
            
        except Exception:
            return False
    
    def run_simulation_for_retirement_age(self, user_input: UserInput,
                                        allocation: PortfolioAllocation,
                                        retirement_age: int,
                                        show_progress: bool = True) -> SimulationResult:
        """
        Run optimized Monte Carlo simulation for a specific retirement age.
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            retirement_age: Age at retirement
            show_progress: Whether to show progress bar
            
        Returns:
            Simulation result
        """
        if retirement_age <= user_input.current_age or retirement_age >= 100:
            raise ValueError("Invalid retirement age")
        
        years_in_retirement = 100 - retirement_age
        
        # Initialize result arrays
        all_success_flags = []
        all_final_values = []
        all_trajectories = []
        
        # Calculate number of batches
        num_batches = (self.num_simulations + self.batch_size - 1) // self.batch_size
        
        # Create progress bar
        desc = f"Optimized {allocation.name} (Age {retirement_age})"
        progress_bar = tqdm(
            range(num_batches),
            desc=desc,
            unit="batch",
            disable=not show_progress,
            leave=False
        )
        
        for batch_idx in progress_bar:
            # Calculate batch size (handle last batch)
            current_batch_size = min(
                self.batch_size, 
                self.num_simulations - batch_idx * self.batch_size
            )
            
            # Run vectorized batch simulation
            success_flags, final_values, trajectories = self.run_vectorized_batch_simulation(
                user_input, allocation, retirement_age, current_batch_size
            )
            
            # Collect results
            all_success_flags.extend(success_flags)
            all_final_values.extend(final_values)
            all_trajectories.append(trajectories)
            
            # Update progress bar
            current_successes = sum(all_success_flags)
            current_total = len(all_success_flags)
            success_rate = current_successes / current_total * 100 if current_total > 0 else 0
            progress_bar.set_postfix(success_rate=f"{success_rate:.1f}%")
        
        # Combine all trajectories
        combined_trajectories = np.vstack(all_trajectories)
        
        # Calculate final statistics
        success_rate = sum(all_success_flags) / len(all_success_flags)
        
        # Calculate percentiles efficiently
        percentile_data = {}
        for percentile in [10, 50, 90]:
            percentile_values = np.percentile(combined_trajectories, percentile, axis=0)
            percentile_data[f"{percentile}th"] = percentile_values
        
        # Calculate average portfolio values
        avg_portfolio_values = np.mean(combined_trajectories, axis=0)
        
        # Calculate withdrawal amounts
        gross_withdrawal = self.tax_calculator.calculate_gross_needed(
            user_input.desired_annual_income
        )
        withdrawal_amounts = np.full(years_in_retirement, gross_withdrawal)
        
        # Create result
        result = SimulationResult(
            portfolio_allocation=allocation,
            retirement_age=retirement_age,
            success_rate=success_rate,
            portfolio_values=avg_portfolio_values,
            withdrawal_amounts=withdrawal_amounts,
            final_portfolio_value=np.mean(all_final_values)
        )
        
        # Add percentile data
        result.percentile_data = percentile_data
        
        return result
    
    def run_parallel_portfolio_analysis(self, user_input: UserInput,
                                      target_success_rate: float = 0.99,
                                      show_progress: bool = True) -> Dict[str, SimulationResult]:
        """
        Run parallel analysis across all portfolio allocations.
        
        Args:
            user_input: User input parameters
            target_success_rate: Target success rate
            show_progress: Whether to show progress
            
        Returns:
            Dictionary mapping portfolio names to simulation results
        """
        if not self.use_parallel:
            # Fall back to sequential processing
            return self._run_sequential_analysis(user_input, target_success_rate, show_progress)
        
        allocations = self.portfolio_manager.get_all_allocations()
        results = {}
        
        if show_progress:
            print(f"\n🚀 Starting parallel retirement analysis...")
            print(f"   Target success rate: {target_success_rate:.1%}")
            print(f"   Simulations per portfolio: {self.num_simulations:,}")
            print(f"   Portfolio allocations: {len(allocations)}")
            print(f"   CPU cores available: {mp.cpu_count()}")
            print(f"   Batch size: {self.batch_size:,}")
            print()
        
        # Use ProcessPoolExecutor for CPU-bound tasks
        max_workers = min(mp.cpu_count(), len(allocations))
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all portfolio analysis tasks
            future_to_portfolio = {}
            
            for name, allocation in allocations.items():
                future = executor.submit(
                    self._analyze_single_portfolio_parallel,
                    user_input, allocation, target_success_rate
                )
                future_to_portfolio[future] = name
            
            # Collect results as they complete
            completed = 0
            total = len(allocations)
            
            for future in as_completed(future_to_portfolio):
                portfolio_name = future_to_portfolio[future]
                completed += 1
                
                try:
                    result = future.result()
                    results[portfolio_name] = result
                    
                    if show_progress:
                        status = "✅" if result.success_rate >= target_success_rate else "⚠️"
                        print(f"  {status} {portfolio_name} ({completed}/{total}): "
                              f"Age {result.retirement_age}, {result.success_rate:.1%} success")
                        
                except Exception as e:
                    if show_progress:
                        print(f"  ❌ {portfolio_name} ({completed}/{total}): Error - {str(e)}")
                    
                    # Create failed result
                    result = SimulationResult(
                        portfolio_allocation=allocations[portfolio_name],
                        retirement_age=95,
                        success_rate=0.0,
                        portfolio_values=np.zeros(6),
                        withdrawal_amounts=np.zeros(5),
                        final_portfolio_value=0.0
                    )
                    results[portfolio_name] = result
        
        if show_progress:
            successful_count = sum(1 for r in results.values() if r.success_rate >= target_success_rate)
            print(f"\n🎉 Parallel analysis complete!")
            print(f"   ✅ Portfolios meeting {target_success_rate:.0%} target: {successful_count}/{len(results)}")
        
        return results
    
    def _analyze_single_portfolio_parallel(self, user_input: UserInput,
                                         allocation: PortfolioAllocation,
                                         target_success_rate: float) -> SimulationResult:
        """
        Analyze a single portfolio allocation (for parallel processing).
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            target_success_rate: Target success rate
            
        Returns:
            Simulation result
        """
        # Find optimal retirement age using binary search
        optimal_age = self._find_optimal_age_binary_search(
            user_input, allocation, target_success_rate
        )
        
        if optimal_age is not None:
            # Run full simulation for optimal age
            return self.run_simulation_for_retirement_age(
                user_input, allocation, optimal_age, show_progress=False
            )
        else:
            # Create result indicating retirement not achievable
            return SimulationResult(
                portfolio_allocation=allocation,
                retirement_age=95,
                success_rate=0.0,
                portfolio_values=np.zeros(6),
                withdrawal_amounts=np.zeros(5),
                final_portfolio_value=0.0
            )
    
    def _find_optimal_age_binary_search(self, user_input: UserInput,
                                      allocation: PortfolioAllocation,
                                      target_success_rate: float) -> Optional[int]:
        """
        Find optimal retirement age using binary search with reduced simulations.
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            target_success_rate: Target success rate
            
        Returns:
            Optimal retirement age or None if not achievable
        """
        min_age = user_input.current_age + 1
        max_age = 95
        
        # Use smaller simulation count for binary search
        original_num_sims = self.num_simulations
        self.num_simulations = min(1000, original_num_sims)  # Faster search
        
        try:
            left, right = min_age, max_age
            best_age = None
            
            while left <= right:
                mid_age = (left + right) // 2
                
                # Quick simulation for this age
                result = self.run_simulation_for_retirement_age(
                    user_input, allocation, mid_age, show_progress=False
                )
                
                if result.success_rate >= target_success_rate:
                    best_age = mid_age
                    right = mid_age - 1  # Try earlier retirement
                else:
                    left = mid_age + 1   # Need to retire later
            
            return best_age
            
        finally:
            # Restore original simulation count
            self.num_simulations = original_num_sims
    
    def _run_sequential_analysis(self, user_input: UserInput,
                               target_success_rate: float,
                               show_progress: bool) -> Dict[str, SimulationResult]:
        """
        Run sequential analysis (fallback when parallel processing is disabled).
        
        Args:
            user_input: User input parameters
            target_success_rate: Target success rate
            show_progress: Whether to show progress
            
        Returns:
            Dictionary mapping portfolio names to simulation results
        """
        allocations = self.portfolio_manager.get_all_allocations()
        results = {}
        
        if show_progress:
            print(f"\n🚀 Starting sequential retirement analysis...")
            print(f"   Target success rate: {target_success_rate:.1%}")
            print(f"   Simulations per portfolio: {self.num_simulations:,}")
            print(f"   Portfolio allocations: {len(allocations)}")
            print()
        
        for i, (name, allocation) in enumerate(allocations.items(), 1):
            if show_progress:
                print(f"🎯 Analyzing {name} ({i}/{len(allocations)})...")
            
            try:
                result = self._analyze_single_portfolio_parallel(
                    user_input, allocation, target_success_rate
                )
                results[name] = result
                
                if show_progress:
                    status = "✅" if result.success_rate >= target_success_rate else "⚠️"
                    print(f"   {status} Result: Age {result.retirement_age}, {result.success_rate:.1%} success")
                    
            except Exception as e:
                if show_progress:
                    print(f"   ❌ Error: {str(e)}")
                
                # Create failed result
                result = SimulationResult(
                    portfolio_allocation=allocation,
                    retirement_age=95,
                    success_rate=0.0,
                    portfolio_values=np.zeros(6),
                    withdrawal_amounts=np.zeros(5),
                    final_portfolio_value=0.0
                )
                results[name] = result
        
        return results
    
    def get_memory_usage_estimate(self) -> Dict[str, float]:
        """
        Estimate memory usage for current configuration.
        
        Returns:
            Dictionary with memory usage estimates in MB
        """
        years_in_retirement = 40  # Typical case
        
        # Estimate memory per simulation
        bytes_per_simulation = (
            years_in_retirement * 8 +  # Portfolio trajectory (float64)
            years_in_retirement * 8 +  # Returns array (float64)
            8 * 4  # Various scalars
        )
        
        # Total memory for all simulations
        total_simulation_memory = self.num_simulations * bytes_per_simulation / 1024 / 1024
        
        # Batch memory (only one batch in memory at a time)
        batch_memory = self.batch_size * bytes_per_simulation / 1024 / 1024
        
        # Historical data memory
        historical_data_memory = len(self.available_years) * 8 * 2 / 1024 / 1024  # equity + bond
        
        return {
            'total_simulation_memory_mb': total_simulation_memory,
            'batch_memory_mb': batch_memory,
            'historical_data_mb': historical_data_memory,
            'estimated_peak_mb': batch_memory + historical_data_memory + 50  # 50MB overhead
        }