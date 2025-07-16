"""
Monte Carlo simulation engine for retirement planning.

This module implements the core Monte Carlo simulation logic using bootstrap
sampling from historical returns, integrating guard rails and tax calculations.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
from .models import UserInput, PortfolioAllocation, SimulationResult, GuardRailsThresholds
from .data_manager import HistoricalDataManager
from .portfolio_manager import PortfolioManager
from .tax_calculator import UKTaxCalculator
from .guard_rails import GuardRailsEngine

# Import optimized simulator
try:
    from .simulator_optimized import OptimizedMonteCarloSimulator
    OPTIMIZED_AVAILABLE = True
except ImportError:
    OPTIMIZED_AVAILABLE = False


class MonteCarloSimulator:
    """Monte Carlo simulation engine for retirement planning."""
    
    def __init__(self, data_manager: HistoricalDataManager, 
                 portfolio_manager: PortfolioManager,
                 tax_calculator: UKTaxCalculator,
                 guard_rails_engine: GuardRailsEngine,
                 num_simulations: int = 10000):
        """
        Initialize the Monte Carlo simulator.
        
        Args:
            data_manager: Historical data manager
            portfolio_manager: Portfolio manager
            tax_calculator: UK tax calculator
            guard_rails_engine: Guard rails engine
            num_simulations: Number of simulations to run
        """
        self.data_manager = data_manager
        self.portfolio_manager = portfolio_manager
        self.tax_calculator = tax_calculator
        self.guard_rails_engine = guard_rails_engine
        self.num_simulations = num_simulations
        
    def run_single_simulation(self, user_input: UserInput, 
                            allocation: PortfolioAllocation,
                            retirement_age: int) -> Tuple[bool, float, np.ndarray]:
        """
        Run a single Monte Carlo simulation scenario.
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            retirement_age: Age at retirement
            
        Returns:
            Tuple of (success, final_portfolio_value, portfolio_values_over_time)
        """
        # Calculate retirement parameters
        years_to_retirement = retirement_age - user_input.current_age
        years_in_retirement = 100 - retirement_age
        
        # Calculate portfolio value at retirement
        portfolio_value = self._calculate_portfolio_at_retirement(
            user_input, allocation, years_to_retirement
        )
        
        # Calculate required gross withdrawal for desired net income
        gross_withdrawal = self.tax_calculator.calculate_gross_needed(
            user_input.desired_annual_income
        )
        
        # Get available years for bootstrap sampling
        equity_years = set(self.data_manager.equity_returns.index)
        bond_years = set(self.data_manager.bond_returns.index)
        available_years = list(equity_years & bond_years)
        
        # Bootstrap sample years for the entire retirement period
        sampled_years = np.random.choice(available_years, size=years_in_retirement, replace=True)
        
        # Simulate retirement with guard rails
        portfolio_values = np.zeros(years_in_retirement + 1)
        portfolio_values[0] = portfolio_value
        
        for year in range(years_in_retirement):
            # Start with current portfolio value
            current_value = portfolio_values[year]
            current_age = retirement_age + year
            
            # Apply market return first
            if current_value > 0:
                # Get allocation for current age (handles dynamic allocations)
                equity_pct, bond_pct, cash_pct = allocation.get_allocation_for_age(current_age, retirement_age)
                
                # Get returns for the sampled year
                sampled_year = sampled_years[year]
                equity_return = self.data_manager.equity_returns[sampled_year]
                bond_return = self.data_manager.bond_returns[sampled_year]
                
                # Calculate portfolio return with current allocation
                portfolio_return = (
                    equity_pct * equity_return +
                    bond_pct * bond_return +
                    cash_pct * 0.0  # Cash returns 0% real return
                )
                
                current_value *= (1 + portfolio_return)
            
            # Calculate withdrawal with guard rails (based on post-return value)
            withdrawal, _ = self.guard_rails_engine.calculate_withdrawal_adjustment(
                current_value, portfolio_value, gross_withdrawal
            )
            
            # Apply withdrawal after market return
            portfolio_values[year + 1] = max(0, current_value - withdrawal)
                
            # Check if portfolio depleted
            if portfolio_values[year + 1] <= 0:
                return False, 0.0, portfolio_values
        
        # Success if portfolio has money at age 100
        success = portfolio_values[-1] > 0
        return success, portfolio_values[-1], portfolio_values
    
    def _calculate_portfolio_at_retirement(self, user_input: UserInput,
                                         allocation: PortfolioAllocation,
                                         years_to_retirement: int) -> float:
        """
        Calculate portfolio value at retirement.
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            years_to_retirement: Years until retirement
            
        Returns:
            Portfolio value at retirement
        """
        if years_to_retirement <= 0:
            return user_input.current_savings
        
        # Calculate portfolio growth with monthly contributions
        portfolio_value = user_input.current_savings
        annual_contribution = user_input.monthly_savings * 12
        retirement_age = user_input.current_age + years_to_retirement
        
        # Get available years for bootstrap sampling
        if self.data_manager.equity_returns is None or self.data_manager.bond_returns is None:
            raise ValueError("Historical data not loaded")
        
        equity_years = set(self.data_manager.equity_returns.index)
        bond_years = set(self.data_manager.bond_returns.index)
        available_years = list(equity_years & bond_years)
        
        # Bootstrap sample years for the entire accumulation period
        sampled_years = np.random.choice(available_years, size=years_to_retirement, replace=True)
        
        for year_idx in range(years_to_retirement):
            current_age = user_input.current_age + year_idx
            
            # Apply annual contribution (assume at beginning of year)
            portfolio_value += annual_contribution
            
            # Get allocation for current age (handles dynamic allocations)
            equity_pct, bond_pct, cash_pct = allocation.get_allocation_for_age(current_age, retirement_age)
            
            # Get returns for the sampled year
            sampled_year = sampled_years[year_idx]
            equity_return = self.data_manager.equity_returns[sampled_year]
            bond_return = self.data_manager.bond_returns[sampled_year]
            
            # Calculate portfolio return with current allocation
            portfolio_return = (
                equity_pct * equity_return +
                bond_pct * bond_return +
                cash_pct * 0.0  # Cash returns 0% real return
            )
            
            # Apply market return
            portfolio_value *= (1 + portfolio_return)
        
        return portfolio_value
    
    def run_simulation_for_retirement_age(self, user_input: UserInput,
                                        allocation: PortfolioAllocation,
                                        retirement_age: int,
                                        show_progress: bool = True) -> SimulationResult:
        """
        Run Monte Carlo simulation for a specific retirement age.
        
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
        
        successes = 0
        final_values = []
        all_portfolio_values = []
        
        # Create progress bar for simulations
        desc = f"Simulating {allocation.name} (Age {retirement_age})"
        progress_bar = tqdm(
            range(self.num_simulations),
            desc=desc,
            unit="sim",
            disable=not show_progress,
            leave=False
        )
        
        for _ in progress_bar:
            success, final_value, portfolio_values = self.run_single_simulation(
                user_input, allocation, retirement_age
            )
            
            if success:
                successes += 1
            
            final_values.append(final_value)
            all_portfolio_values.append(portfolio_values)
            
            # Update progress bar with current success rate
            current_success_rate = successes / (len(final_values)) * 100
            progress_bar.set_postfix(success_rate=f"{current_success_rate:.1f}%")
        
        # Calculate success rate
        success_rate = successes / self.num_simulations
        
        # Calculate average portfolio values over time
        years_in_retirement = 100 - retirement_age
        avg_portfolio_values = np.zeros(years_in_retirement + 1)
        
        for year in range(years_in_retirement + 1):
            year_values = [sim_values[year] if year < len(sim_values) else 0 
                          for sim_values in all_portfolio_values]
            avg_portfolio_values[year] = np.mean(year_values)
        
        # Calculate percentiles for this simulation
        percentile_data = {}
        for percentile in [10, 50, 90]:
            percentile_values = np.zeros(years_in_retirement + 1)
            
            for year in range(years_in_retirement + 1):
                year_values = [sim_values[year] if year < len(sim_values) else 0
                              for sim_values in all_portfolio_values]
                percentile_values[year] = np.percentile(year_values, percentile)
            
            percentile_data[f"{percentile}th"] = percentile_values
        
        # Calculate withdrawal amounts (using average case)
        gross_withdrawal = self.tax_calculator.calculate_gross_needed(
            user_input.desired_annual_income
        )
        withdrawal_amounts = np.full(years_in_retirement, gross_withdrawal)
        
        # Store percentile data in the result (we'll need to update SimulationResult model)
        result = SimulationResult(
            portfolio_allocation=allocation,
            retirement_age=retirement_age,
            success_rate=success_rate,
            portfolio_values=avg_portfolio_values,
            withdrawal_amounts=withdrawal_amounts,
            final_portfolio_value=np.mean(final_values)
        )
        
        # Add percentile data as a custom attribute
        result.percentile_data = percentile_data
        
        return result
    
    def find_optimal_retirement_age(self, user_input: UserInput,
                                  allocation: PortfolioAllocation,
                                  target_success_rate: float = 0.99,
                                  show_progress: bool = True) -> Optional[int]:
        """
        Find optimal retirement age for target success rate.
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            target_success_rate: Target success rate (default: 99%)
            show_progress: Whether to show progress bar
            
        Returns:
            Optimal retirement age or None if not achievable
        """
        min_age = user_input.current_age + 1
        max_age = 95  # Maximum reasonable retirement age
        
        # Binary search for optimal retirement age
        left, right = min_age, max_age
        best_age = None
        
        if show_progress:
            print(f"🔍 Finding optimal retirement age for {allocation.name}...")
        
        while left <= right:
            mid_age = (left + right) // 2
            
            # Run simulation for this age (disable individual progress for binary search)
            result = self.run_simulation_for_retirement_age(
                user_input, allocation, mid_age, show_progress=False
            )
            
            if show_progress:
                print(f"   Age {mid_age}: {result.success_rate:.1%} success rate", end="")
            
            if result.success_rate >= target_success_rate:
                best_age = mid_age
                right = mid_age - 1  # Try earlier retirement
                if show_progress:
                    print(" ✓ (target achieved)")
            else:
                left = mid_age + 1   # Need to retire later
                if show_progress:
                    print(" ✗ (below target)")
        
        if show_progress and best_age:
            print(f"✅ Optimal retirement age found: {best_age}")
        elif show_progress:
            print("❌ Target success rate not achievable")
        
        return best_age
    
    def run_comprehensive_simulation(self, user_input: UserInput,
                                   target_success_rate: float = 0.99,
                                   show_progress: bool = True) -> Dict[str, SimulationResult]:
        """
        Run comprehensive simulation for all portfolio allocations.
        
        Args:
            user_input: User input parameters
            target_success_rate: Target success rate
            show_progress: Whether to show progress bar
            
        Returns:
            Dictionary mapping portfolio names to simulation results
        """
        results = {}
        allocations = self.portfolio_manager.get_all_allocations()
        
        if show_progress:
            print(f"\n🚀 Starting comprehensive retirement analysis...")
            print(f"   Target success rate: {target_success_rate:.1%}")
            print(f"   Simulations per portfolio: {self.num_simulations:,}")
            print(f"   Portfolio allocations to test: {len(allocations)}")
            
            # Estimate total time
            total_simulations = len(allocations) * self.num_simulations * 2  # Rough estimate including age finding
            estimated_minutes = total_simulations / 60000  # Assume ~1000 sims per second
            if estimated_minutes > 1:
                print(f"   Estimated total time: {estimated_minutes:.1f} minutes")
            else:
                print(f"   Estimated total time: {estimated_minutes * 60:.0f} seconds")
            print()
        
        # Create progress bar for overall portfolio analysis
        portfolio_progress = tqdm(
            allocations.items(),
            desc="🎯 Analyzing portfolios",
            unit="portfolio",
            disable=not show_progress,
            leave=True,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {postfix}]"
        )
        
        successful_count = 0
        
        for portfolio_num, (name, allocation) in enumerate(portfolio_progress, 1):
            portfolio_progress.set_description(f"🎯 Analyzing {name} ({portfolio_num}/{len(allocations)})")
            
            try:
                # Find optimal retirement age for this allocation
                if show_progress:
                    print(f"\n  🔍 Finding optimal retirement age for {name}...")
                
                optimal_age = self.find_optimal_retirement_age(
                    user_input, allocation, target_success_rate, show_progress=False
                )
                
                if optimal_age is not None:
                    if show_progress:
                        print(f"  ✅ Optimal age found: {optimal_age}")
                        print(f"  🎲 Running {self.num_simulations:,} simulations...")
                    
                    # Run full simulation for optimal age
                    result = self.run_simulation_for_retirement_age(
                        user_input, allocation, optimal_age, show_progress=show_progress
                    )
                    results[name] = result
                    
                    if result.success_rate >= target_success_rate:
                        successful_count += 1
                        status_emoji = "✅"
                    else:
                        status_emoji = "⚠️"
                    
                    # Update progress bar with result
                    portfolio_progress.set_postfix_str(
                        f"{status_emoji} Age: {optimal_age}, Success: {result.success_rate:.1%}"
                    )
                    
                    if show_progress:
                        print(f"  {status_emoji} Result: {result.success_rate:.1%} success rate at age {optimal_age}")
                    
                else:
                    if show_progress:
                        print(f"  ❌ No viable retirement age found (target not achievable)")
                    
                    # Create result indicating retirement not achievable
                    result = SimulationResult(
                        portfolio_allocation=allocation,
                        retirement_age=95,  # Max age
                        success_rate=0.0,
                        portfolio_values=np.zeros(6),
                        withdrawal_amounts=np.zeros(5),
                        final_portfolio_value=0.0
                    )
                    results[name] = result
                    
                    # Update progress bar with failure
                    portfolio_progress.set_postfix_str("❌ Target not achievable")
                
            except KeyboardInterrupt:
                if show_progress:
                    print(f"\n⚠️  Analysis interrupted by user during {name}")
                raise
            except Exception as e:
                if show_progress:
                    print(f"\n❌ Error analyzing {name}: {str(e)}")
                # Create a failed result
                result = SimulationResult(
                    portfolio_allocation=allocation,
                    retirement_age=95,
                    success_rate=0.0,
                    portfolio_values=np.zeros(6),
                    withdrawal_amounts=np.zeros(5),
                    final_portfolio_value=0.0
                )
                results[name] = result
                portfolio_progress.set_postfix_str("❌ Analysis failed")
        
        if show_progress:
            print(f"\n🎉 Comprehensive analysis complete!")
            print(f"   📊 Portfolios analyzed: {len(results)}")
            print(f"   ✅ Portfolios meeting {target_success_rate:.0%} target: {successful_count}/{len(results)}")
            
            if successful_count > 0:
                # Find the best performing portfolio
                best_portfolio = max(
                    [(name, result) for name, result in results.items() if result.success_rate >= target_success_rate],
                    key=lambda x: x[1].success_rate,
                    default=(None, None)
                )
                if best_portfolio[0]:
                    print(f"   🏆 Best portfolio: {best_portfolio[0]} (Age {best_portfolio[1].retirement_age})")
            else:
                print(f"   ⚠️  No portfolios achieved the {target_success_rate:.0%} success rate target")
                print(f"   💡 Consider increasing savings or reducing desired income")
            print()
        
        return results
    
    def calculate_percentiles(self, user_input: UserInput,
                            allocation: PortfolioAllocation,
                            retirement_age: int,
                            percentiles: List[float] = [10, 50, 90],
                            show_progress: bool = True) -> Dict[str, np.ndarray]:
        """
        Calculate percentile trajectories for portfolio values.
        
        Args:
            user_input: User input parameters
            allocation: Portfolio allocation
            retirement_age: Age at retirement
            percentiles: List of percentiles to calculate
            show_progress: Whether to show progress bar
            
        Returns:
            Dictionary mapping percentile names to value arrays
        """
        years_in_retirement = 100 - retirement_age
        all_portfolio_values = []
        
        # Create progress bar for percentile calculations
        desc = f"Calculating percentiles for {allocation.name}"
        progress_bar = tqdm(
            range(self.num_simulations),
            desc=desc,
            unit="sim",
            disable=not show_progress,
            leave=False
        )
        
        # Run simulations and collect portfolio trajectories
        for _ in progress_bar:
            _, _, portfolio_values = self.run_single_simulation(
                user_input, allocation, retirement_age
            )
            all_portfolio_values.append(portfolio_values)
        
        # Calculate percentiles for each year
        percentile_data = {}
        for percentile in percentiles:
            percentile_values = np.zeros(years_in_retirement + 1)
            
            for year in range(years_in_retirement + 1):
                year_values = [sim_values[year] if year < len(sim_values) else 0
                              for sim_values in all_portfolio_values]
                percentile_values[year] = np.percentile(year_values, percentile)
            
            percentile_data[f"{percentile}th"] = percentile_values
        
        return percentile_data
    
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


def create_simulator(data_manager: HistoricalDataManager,
                    portfolio_manager: PortfolioManager,
                    tax_calculator: UKTaxCalculator,
                    guard_rails_engine: GuardRailsEngine,
                    num_simulations: int = 10000,
                    use_optimized: bool = True,
                    batch_size: int = 1000,
                    use_parallel: bool = True) -> MonteCarloSimulator:
    """
    Factory function to create the appropriate simulator.
    
    Args:
        data_manager: Historical data manager
        portfolio_manager: Portfolio manager
        tax_calculator: UK tax calculator
        guard_rails_engine: Guard rails engine
        num_simulations: Number of simulations to run
        use_optimized: Whether to use optimized simulator if available
        batch_size: Batch size for memory management (optimized only)
        use_parallel: Whether to use parallel processing (optimized only)
        
    Returns:
        Appropriate simulator instance
    """
    if use_optimized and OPTIMIZED_AVAILABLE:
        return OptimizedMonteCarloSimulator(
            data_manager, portfolio_manager, tax_calculator, guard_rails_engine,
            num_simulations, batch_size, use_parallel
        )
    else:
        if use_optimized and not OPTIMIZED_AVAILABLE:
            print("⚠️  Optimized simulator not available, falling back to standard simulator")
        
        return MonteCarloSimulator(
            data_manager, portfolio_manager, tax_calculator, guard_rails_engine,
            num_simulations
        )