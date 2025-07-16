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
        
        # Generate bootstrap returns for retirement period
        retirement_returns = self.portfolio_manager.generate_bootstrap_returns(
            allocation, years_in_retirement, 1
        )[0]
        
        # Simulate retirement with guard rails
        portfolio_values = np.zeros(years_in_retirement + 1)
        portfolio_values[0] = portfolio_value
        
        for year in range(years_in_retirement):
            # Start with current portfolio value
            current_value = portfolio_values[year]
            
            # Apply market return first
            if current_value > 0:
                current_value *= (1 + retirement_returns[year])
            
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
        
        # Generate bootstrap returns for accumulation period
        accumulation_returns = self.portfolio_manager.generate_bootstrap_returns(
            allocation, years_to_retirement, 1
        )[0]
        
        # Calculate portfolio growth with monthly contributions
        portfolio_value = user_input.current_savings
        annual_contribution = user_input.monthly_savings * 12
        
        for year in range(years_to_retirement):
            # Apply annual contribution (assume at beginning of year)
            portfolio_value += annual_contribution
            
            # Apply market return
            portfolio_value *= (1 + accumulation_returns[year])
        
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
            print()
        
        # Create progress bar for overall portfolio analysis
        portfolio_progress = tqdm(
            allocations.items(),
            desc="Analyzing portfolios",
            unit="portfolio",
            disable=not show_progress,
            leave=True
        )
        
        for name, allocation in portfolio_progress:
            portfolio_progress.set_description(f"Analyzing {name}")
            
            # Find optimal retirement age for this allocation
            optimal_age = self.find_optimal_retirement_age(
                user_input, allocation, target_success_rate, show_progress=False
            )
            
            if optimal_age is not None:
                # Run full simulation for optimal age
                result = self.run_simulation_for_retirement_age(
                    user_input, allocation, optimal_age, show_progress=True
                )
                results[name] = result
                
                # Update progress bar with result
                portfolio_progress.set_postfix(
                    age=optimal_age,
                    success=f"{result.success_rate:.1%}"
                )
            else:
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
                portfolio_progress.set_postfix(
                    age="N/A",
                    success="0.0%"
                )
        
        if show_progress:
            print(f"\n✅ Comprehensive analysis complete!")
            print(f"   Portfolios analyzed: {len(results)}")
            successful_portfolios = sum(1 for r in results.values() if r.success_rate >= target_success_rate)
            print(f"   Portfolios meeting target: {successful_portfolios}/{len(results)}")
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