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
from src.simulator import MonteCarloSimulator
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
            self.cli.display_progress("Initializing components...")
            
            # Initialize data manager and load historical data
            self.cli.display_progress("Loading historical market data...")
            self.data_manager = HistoricalDataManager()
            self.data_manager.load_all_data()
            
            if not self.data_manager.validate_data():
                self.cli.display_error("Historical data validation failed", is_fatal=True)
            
            # Initialize portfolio manager
            self.cli.display_progress("Setting up portfolio allocations...")
            self.portfolio_manager = PortfolioManager(self.data_manager)
            
            # Initialize tax calculator
            self.cli.display_progress("Initializing UK tax calculator...")
            self.tax_calculator = UKTaxCalculator()
            
            # Initialize guard rails engine
            self.cli.display_progress("Setting up guard rails system...")
            self.guard_rails_engine = GuardRailsEngine()
            
            # Initialize Monte Carlo simulator
            self.cli.display_progress("Initializing Monte Carlo simulator...")
            self.simulator = MonteCarloSimulator(
                self.data_manager,
                self.portfolio_manager,
                self.tax_calculator,
                self.guard_rails_engine,
                self.num_simulations
            )
            
            # Initialize results analyzer
            self.cli.display_progress("Setting up results analyzer...")
            self.analyzer = ResultsAnalyzer()
            
            # Initialize chart generator
            self.cli.display_progress("Initializing chart generator...")
            self.chart_generator = ChartGenerator()
            
            self.cli.display_success("All components initialized successfully")
            
        except Exception as e:
            self.cli.display_error(f"Failed to initialize components: {str(e)}", is_fatal=True)
    
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
            if not self.simulator.validate_simulation_parameters(user_input):
                self.cli.display_error("Invalid simulation parameters", is_fatal=True)
            
            # Run comprehensive simulation
            portfolio_results = self.simulator.run_comprehensive_simulation(user_input, show_progress=True)
            
            # Analyze results
            self.cli.display_progress("Analyzing results...")
            results = self.analyzer.analyze_simulation_results(user_input, portfolio_results)
            
            # Validate results
            if not self.analyzer.validate_results(results):
                self.cli.display_error("Results validation failed", is_fatal=True)
            
            self.cli.display_success("Analysis completed successfully")
            return results
            
        except Exception as e:
            self.cli.display_error(f"Analysis failed: {str(e)}", is_fatal=True)
    
    def generate_charts(self, results: RetirementResults) -> Optional[Dict[str, str]]:
        """
        Generate charts for the retirement analysis.
        
        Args:
            results: Retirement analysis results
            
        Returns:
            Dictionary of generated chart files
        """
        try:
            if not self.chart_generator.validate_chart_data(results):
                self.cli.display_warning("Chart data validation failed - skipping chart generation")
                return None
            
            chart_files = self.chart_generator.generate_comprehensive_report_charts(results, show_progress=True)
            
            if chart_files:
                self.cli.display_success("Charts generated successfully")
                return chart_files
            else:
                self.cli.display_warning("No charts were generated")
                return None
                
        except Exception as e:
            self.cli.display_error(f"Chart generation failed: {str(e)}")
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