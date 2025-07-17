#!/usr/bin/env python3
"""
Retirement Calculator - Main Entry Point

A command-line retirement prediction tool that uses Monte Carlo simulation
with historical market data to calculate retirement feasibility.
"""

import sys
import os
from typing import Optional, Dict

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models import UserInput, RetirementResults
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager
from src.tax_calculator import UKTaxCalculator
from src.guard_rails import GuardRailsEngine
from src.simulator import create_simulator
from src.analyzer import ResultsAnalyzer
from src.charts import ChartGenerator
from src.cli import RetirementCalculatorCLI


class RetirementCalculatorApp:
    """Main application class that orchestrates all components."""
    
    def __init__(self, num_simulations: int = 10000):
        """
        Initialize the retirement calculator application.
        
        Args:
            num_simulations: Number of Monte Carlo simulations to run
        """
        self.num_simulations = num_simulations
        self.cli = RetirementCalculatorCLI()
        
        # Initialize components
        self.data_manager = None
        self.portfolio_manager = None
        self.tax_calculator = None
        self.guard_rails_engine = None
        self.simulator = None
        self.analyzer = None
        self.chart_generator = None
        
    def initialize_components(self):
        """Initialize all system components."""
        try:
            self.cli.display_progress("🔧 Initializing retirement calculator components...")
            
            # Initialize data manager and load historical data
            self.cli.display_progress("📊 Loading historical market data...")
            try:
                self.data_manager = HistoricalDataManager()
                self.data_manager.load_all_data()
                
                if not self.data_manager.validate_data():
                    self.cli.display_error(
                        "Historical data validation failed. Please check your data files in the 'data/' directory.",
                        is_fatal=True
                    )
                
                self.cli.display_success("Historical data loaded and validated successfully")
                
            except FileNotFoundError as e:
                # Show data diagnostics to help with troubleshooting
                diagnostics = self.data_manager.get_data_diagnostics()
                self.cli.display_error(
                    f"Required data files are missing:\n{str(e)}\n\n"
                    f"{diagnostics}\n\n"
                    f"Please ensure you have the following files in the 'data/' directory:\n"
                    f"  - global_equity_returns.csv (columns: year, return)\n"
                    f"  - global_bond_returns.csv (columns: year, return)\n"
                    f"  - uk_inflation_rates.csv (columns: year, inflation_rate)",
                    is_fatal=True
                )
            except ValueError as e:
                # Show data diagnostics to help with troubleshooting
                diagnostics = self.data_manager.get_data_diagnostics()
                self.cli.display_error(
                    f"Data file format error:\n{str(e)}\n\n"
                    f"{diagnostics}\n\n"
                    f"Please check your CSV files for correct format and content.",
                    is_fatal=True
                )
            
            # Initialize portfolio manager
            self.cli.display_progress("📈 Setting up portfolio allocations...")
            try:
                self.portfolio_manager = PortfolioManager(self.data_manager)
                num_allocations = len(self.portfolio_manager.get_all_allocations())
                self.cli.display_success(f"Portfolio allocations configured ({num_allocations} different strategies)")
            except Exception as e:
                self.cli.display_error(f"Failed to initialize portfolio manager: {str(e)}", is_fatal=True)
            
            # Initialize tax calculator
            self.cli.display_progress("💰 Initializing UK tax calculator...")
            try:
                self.tax_calculator = UKTaxCalculator()
                self.cli.display_success("UK tax calculator ready (current tax bands loaded)")
            except Exception as e:
                self.cli.display_error(f"Failed to initialize tax calculator: {str(e)}", is_fatal=True)
            
            # Initialize guard rails engine
            self.cli.display_progress("🛡️  Setting up guard rails system...")
            try:
                self.guard_rails_engine = GuardRailsEngine()
                self.cli.display_success("Guard rails system configured (dynamic spending adjustments)")
            except Exception as e:
                self.cli.display_error(f"Failed to initialize guard rails engine: {str(e)}", is_fatal=True)
            
            # Initialize Monte Carlo simulator (optimized version)
            self.cli.display_progress("🎲 Initializing Monte Carlo simulator...")
            try:
                # Check if any allocations are dynamic
                has_dynamic_allocations = any(
                    allocation.is_dynamic 
                    for allocation in self.portfolio_manager.get_all_allocations().values()
                )
                
                # Use regular simulator if we have dynamic allocations
                use_optimized = not has_dynamic_allocations
                
                self.simulator = create_simulator(
                    self.data_manager,
                    self.portfolio_manager,
                    self.tax_calculator,
                    self.guard_rails_engine,
                    self.num_simulations,
                    use_optimized=use_optimized,
                    batch_size=min(1000, self.num_simulations),
                    use_parallel=True
                )
                
                # Check if optimized simulator is being used
                if hasattr(self.simulator, 'get_memory_usage_estimate'):
                    memory_estimate = self.simulator.get_memory_usage_estimate()
                    self.cli.display_success(
                        f"Optimized Monte Carlo simulator ready ({self.num_simulations:,} simulations per portfolio)\n"
                        f"  Estimated peak memory usage: {memory_estimate['estimated_peak_mb']:.1f} MB"
                    )
                else:
                    if has_dynamic_allocations:
                        self.cli.display_success(
                            f"Monte Carlo simulator ready ({self.num_simulations:,} simulations per portfolio)\n"
                            f"  Using standard simulator for dynamic allocations"
                        )
                    else:
                        self.cli.display_success(f"Monte Carlo simulator ready ({self.num_simulations:,} simulations per portfolio)")
                    
            except Exception as e:
                self.cli.display_error(f"Failed to initialize Monte Carlo simulator: {str(e)}", is_fatal=True)
            
            # Initialize results analyzer
            self.cli.display_progress("📊 Setting up results analyzer...")
            try:
                self.analyzer = ResultsAnalyzer()
                self.cli.display_success("Results analyzer ready")
            except Exception as e:
                self.cli.display_error(f"Failed to initialize results analyzer: {str(e)}", is_fatal=True)
            
            # Initialize chart generator
            self.cli.display_progress("📈 Initializing chart generator...")
            try:
                self.chart_generator = ChartGenerator()
                self.cli.display_success("Chart generator ready (charts will be saved to 'charts/' directory)")
            except Exception as e:
                self.cli.display_error(f"Failed to initialize chart generator: {str(e)}", is_fatal=True)
            
            self.cli.display_success("🎉 All components initialized successfully! Ready to analyze your retirement plan.")
            
        except KeyboardInterrupt:
            self.cli.handle_keyboard_interrupt()
        except Exception as e:
            self.cli.display_error(
                f"Unexpected error during initialization:\n{str(e)}\n\n"
                f"Please check your installation and data files, then try again.",
                is_fatal=True
            )
    
    def run_analysis(self, user_input: UserInput) -> RetirementResults:
        """
        Run the complete retirement analysis.
        
        Args:
            user_input: User input parameters
            
        Returns:
            Complete retirement analysis results
        """
        try:
            # Validate simulation parameters
            self.cli.display_progress("🔍 Validating simulation parameters...")
            if not self.simulator.validate_simulation_parameters(user_input):
                self.cli.display_error(
                    "Invalid simulation parameters detected.\n"
                    "Please check your input values and try again.",
                    is_fatal=True
                )
            
            self.cli.display_success("Simulation parameters validated successfully")
            
            # Estimate analysis time
            estimated_time = (self.num_simulations * 6) / 1000  # Rough estimate: 6 portfolios, ~1000 sims per second
            if estimated_time > 60:
                self.cli.display_progress(f"⏱️  Estimated analysis time: {estimated_time/60:.1f} minutes")
            else:
                self.cli.display_progress(f"⏱️  Estimated analysis time: {estimated_time:.0f} seconds")
            
            # Run comprehensive simulation with enhanced error handling
            self.cli.display_progress("🎲 Starting Monte Carlo simulation analysis...")
            try:
                portfolio_results = self.simulator.run_comprehensive_simulation(user_input, show_progress=True)
                
                if not portfolio_results:
                    self.cli.display_error(
                        "No simulation results were generated.\n"
                        "This may indicate a problem with the historical data or simulation parameters.",
                        is_fatal=True
                    )
                
                self.cli.display_success(f"Monte Carlo simulation completed ({len(portfolio_results)} portfolios analyzed)")
                
            except MemoryError:
                self.cli.display_error(
                    f"Insufficient memory to run {self.num_simulations:,} simulations.\n"
                    f"Try reducing the number of simulations using the --simulations parameter.\n"
                    f"Example: python main.py --simulations 5000",
                    is_fatal=True
                )
            except KeyboardInterrupt:
                self.cli.display_error("Analysis cancelled by user", is_fatal=True)
            except Exception as e:
                self.cli.display_error(
                    f"Simulation failed with error:\n{str(e)}\n\n"
                    f"This may be due to insufficient historical data or calculation errors.\n"
                    f"Please check your data files and try again.",
                    is_fatal=True
                )
            
            # Analyze results
            self.cli.display_progress("📊 Analyzing simulation results...")
            try:
                results = self.analyzer.analyze_simulation_results(user_input, portfolio_results)
                
                if not results:
                    self.cli.display_error("Failed to analyze simulation results", is_fatal=True)
                
                self.cli.display_success("Results analysis completed")
                
            except Exception as e:
                self.cli.display_error(
                    f"Results analysis failed:\n{str(e)}\n\n"
                    f"The simulation completed but results could not be processed.",
                    is_fatal=True
                )
            
            # Validate results
            self.cli.display_progress("✅ Validating analysis results...")
            if not self.analyzer.validate_results(results):
                self.cli.display_error(
                    "Results validation failed.\n"
                    "The analysis produced invalid or inconsistent results.\n"
                    "Please try running the analysis again.",
                    is_fatal=True
                )
            
            self.cli.display_success("🎉 Analysis completed successfully! Results are ready.")
            return results
            
        except KeyboardInterrupt:
            self.cli.handle_keyboard_interrupt()
        except MemoryError:
            self.cli.display_error(
                f"Insufficient memory to complete analysis.\n"
                f"Try reducing simulations: python main.py --simulations 5000",
                is_fatal=True
            )
        except Exception as e:
            self.cli.display_error(
                f"Unexpected error during analysis:\n{str(e)}\n\n"
                f"Please check your input and data files, then try again.\n"
                f"If the problem persists, try reducing the number of simulations.",
                is_fatal=True
            )
    
    def generate_charts(self, results: RetirementResults) -> Optional[Dict[str, str]]:
        """
        Generate charts for the retirement analysis.
        
        Args:
            results: Retirement analysis results
            
        Returns:
            Dictionary of generated chart files
        """
        try:
            self.cli.display_progress("📊 Preparing to generate charts...")
            
            # Validate chart data
            if not self.chart_generator.validate_chart_data(results):
                self.cli.display_warning(
                    "Chart data validation failed - insufficient data for visualization.\n"
                    "Charts will be skipped, but your analysis results are still valid."
                )
                return None
            
            self.cli.display_success("Chart data validated successfully")
            
            # Generate charts with enhanced error handling
            try:
                chart_files = self.chart_generator.generate_comprehensive_report_charts(results, show_progress=True)
                
                if chart_files:
                    total_charts = sum(len(files) if isinstance(files, list) else 1 for files in chart_files.values())
                    self.cli.display_success(f"📈 Charts generated successfully! Created {total_charts} chart files.")
                    
                    # Display chart location
                    chart_dir = self.chart_generator.get_output_directory()
                    self.cli.display_progress(f"Chart files saved to: {chart_dir}")
                    
                    # Display individual chart files
                    for chart_type, filepath in chart_files.items():
                        if isinstance(filepath, list):
                            self.cli.display_progress(f"  {chart_type}: {len(filepath)} files")
                        else:
                            filename = os.path.basename(filepath)
                            self.cli.display_progress(f"  {chart_type}: {filename}")
                    
                    return chart_files
                else:
                    self.cli.display_warning("No charts were generated - this may indicate a data processing issue")
                    return None
                    
            except ImportError as e:
                self.cli.display_error(
                    f"Chart generation requires additional libraries:\n{str(e)}\n\n"
                    f"Please install missing dependencies:\n"
                    f"  pip install matplotlib\n"
                    f"Charts will be skipped, but your analysis results are still available."
                )
                return None
            except PermissionError:
                self.cli.display_error(
                    "Cannot write chart files - permission denied.\n"
                    "Please check write permissions for the 'charts/' directory.\n"
                    "Charts will be skipped, but your analysis results are still available."
                )
                return None
            except OSError as e:
                self.cli.display_error(
                    f"File system error during chart generation:\n{str(e)}\n\n"
                    "This may be due to insufficient disk space or file system issues.\n"
                    "Charts will be skipped, but your analysis results are still available."
                )
                return None
                
        except KeyboardInterrupt:
            self.cli.display_warning("Chart generation cancelled by user")
            return None
        except Exception as e:
            self.cli.display_error(
                f"Unexpected error during chart generation:\n{str(e)}\n\n"
                f"Charts will be skipped, but your analysis results are still available."
            )
            return None
    
    def display_results(self, results: RetirementResults):
        """
        Display the retirement analysis results.
        
        Args:
            results: Retirement analysis results
        """
        print("\\n" + "="*60)
        print("RETIREMENT ANALYSIS RESULTS")
        print("="*60)
        
        # Display user input summary
        print(f"\\nUser Profile:")
        print(f"  Current Age: {results.user_input.current_age}")
        print(f"  Current Savings: £{results.user_input.current_savings:,.2f}")
        print(f"  Monthly Savings: £{results.user_input.monthly_savings:,.2f}")
        print(f"  Desired Annual Income: £{results.user_input.desired_annual_income:,.2f}")
        
        # Display recommendation
        print(f"\\nRECOMMENDATION:")
        print(f"  Best Portfolio: {results.recommended_portfolio.name}")
        print(f"  Recommended Retirement Age: {results.recommended_retirement_age}")
        
        # Display portfolio comparison
        print(f"\\nPORTFOLIO COMPARISON:")
        print(f"{'Portfolio':<25} {'Retirement Age':<15} {'Success Rate':<15} {'Median End Wealth':<20}")
        print("-" * 75)
        
        for result in results.portfolio_results:
            success_rate = f"{result.success_rate:.1%}"
            
            # Get median end wealth at age 100 from percentile data
            median_end_wealth = "N/A"
            if (result.portfolio_allocation.name in results.percentile_data and 
                "50th" in results.percentile_data[result.portfolio_allocation.name]):
                percentile_50 = results.percentile_data[result.portfolio_allocation.name]["50th"]
                if len(percentile_50) > 0:
                    median_end_wealth = f"£{percentile_50[-1]:,.0f}"
            
            print(f"{result.portfolio_allocation.name:<25} {result.retirement_age:<15} {success_rate:<15} {median_end_wealth:<20}")
        
        # Display analysis insights
        failure_analysis = self.analyzer.calculate_failure_analysis(
            {result.portfolio_allocation.name: result for result in results.portfolio_results}
        )
        
        comparison = self.analyzer.compare_portfolios(
            {result.portfolio_allocation.name: result for result in results.portfolio_results}
        )
        
        print(f"\\nKEY INSIGHTS:")
        print(f"  Earliest Possible Retirement: Age {comparison.get('earliest_retirement_age', 'N/A')}")
        print(f"  Best Success Rate: {comparison.get('best_success_rate', 0):.1%}")
        print(f"  Average Success Rate: {comparison.get('average_success_rate', 0):.1%}")
        
        # Calculate and display withdrawal rate context
        recommended_result = None
        for result in results.portfolio_results:
            if result.portfolio_allocation.name == results.recommended_portfolio.name:
                recommended_result = result
                break
        
        if recommended_result:
            # Calculate withdrawal rate for recommended portfolio
            gross_withdrawal = self.tax_calculator.calculate_gross_needed(results.user_input.desired_annual_income)
            portfolio_value = recommended_result.portfolio_values[0] if len(recommended_result.portfolio_values) > 0 else 0
            if portfolio_value > 0:
                withdrawal_rate = gross_withdrawal / portfolio_value
                print(f"  Withdrawal Rate: {withdrawal_rate:.1%} (£{gross_withdrawal:,.0f} from £{portfolio_value:,.0f})")
                if withdrawal_rate < 0.04:
                    print(f"  Note: Low withdrawal rate means portfolio may grow during retirement")
        
        # Display improvement suggestions
        suggestions = self.analyzer.generate_improvement_suggestions(
            results.user_input,
            {result.portfolio_allocation.name: result for result in results.portfolio_results}
        )
        
        if suggestions:
            print(f"\\nIMPROVEMENT SUGGESTIONS:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        # Display retirement readiness score
        recommended_result = None
        for result in results.portfolio_results:
            if result.portfolio_allocation.name == results.recommended_portfolio.name:
                recommended_result = result
                break
        
        if recommended_result:
            readiness_score = self.analyzer.calculate_retirement_readiness_score(
                results.user_input, recommended_result
            )
            print(f"\\nRETIREMENT READINESS SCORE: {readiness_score:.1f}/100")
    
    def run(self, generate_charts: bool = False):
        """
        Run the complete retirement calculator application.
        
        Args:
            generate_charts: Whether to generate charts
        """
        try:
            # Initialize components
            self.initialize_components()
            
            # Collect user input
            user_input = self.cli.collect_user_input()
            
            # Validate input interactively
            if not self.cli.validate_input_interactive(user_input):
                self.cli.display_error("Invalid input provided", is_fatal=True)
            
            # Run analysis
            results = self.run_analysis(user_input)
            
            # Display results
            self.display_results(results)
            
            # Generate charts if requested
            chart_files = None
            if generate_charts or self.cli.prompt_for_charts():
                chart_files = self.generate_charts(results)
            
            # Display completion message
            self.cli.display_completion_message(chart_files)
            
        except KeyboardInterrupt:
            self.cli.handle_keyboard_interrupt()
        except Exception as e:
            self.cli.display_error(f"Application error: {str(e)}", is_fatal=True)


def main():
    """Main entry point for the retirement calculator application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Kiro Simple Retirement Planner - Plan your retirement with confidence"
    )
    parser.add_argument(
        "--simulations", "-s", 
        type=int, 
        default=10000,
        help="Number of Monte Carlo simulations to run (default: 10000)"
    )
    parser.add_argument(
        "--charts", "-c",
        action="store_true",
        help="Generate charts automatically"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Create and run the application
    app = RetirementCalculatorApp(num_simulations=args.simulations)
    app.run(generate_charts=args.charts)


if __name__ == "__main__":
    main()