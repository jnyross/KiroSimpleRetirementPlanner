"""
Chart generation system for retirement planning visualization.

This module creates time series charts showing portfolio value projections
with percentile ranges using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import os
from tqdm import tqdm
from .models import RetirementResults, SimulationResult


class ChartGenerator:
    """Generates charts for retirement planning analysis."""
    
    def __init__(self, output_directory: str = "charts"):
        """
        Initialize the chart generator.
        
        Args:
            output_directory: Directory to save chart files
        """
        # Create a timestamped subdirectory for this analysis run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_directory = os.path.join(output_directory, f"analysis_{timestamp}")
        self._ensure_output_directory()
        
        # Set up matplotlib style
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
    
    def get_output_directory(self) -> str:
        """Get the current output directory path."""
        return self.output_directory
    
    def generate_portfolio_comparison_chart(self, results: RetirementResults) -> str:
        """
        Generate a chart comparing all portfolio allocations.
        
        Args:
            results: Retirement analysis results
            
        Returns:
            Path to the generated chart file
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Extract data for plotting
        portfolio_names = []
        success_rates = []
        retirement_ages = []
        
        for result in results.portfolio_results:
            portfolio_names.append(result.portfolio_allocation.name)
            success_rates.append(result.success_rate * 100)  # Convert to percentage
            retirement_ages.append(result.retirement_age)
        
        # Plot 1: Success Rates
        bars1 = ax1.bar(portfolio_names, success_rates, color='steelblue', alpha=0.7)
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_title('Retirement Success Rates by Portfolio Allocation')
        ax1.set_ylim(0, 100)
        
        # Add confidence threshold line
        ax1.axhline(y=99, color='red', linestyle='--', alpha=0.7, label='99% Confidence Threshold')
        ax1.legend()
        
        # Add value labels on bars
        for bar, rate in zip(bars1, success_rates):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        # Plot 2: Retirement Ages
        bars2 = ax2.bar(portfolio_names, retirement_ages, color='darkgreen', alpha=0.7)
        ax2.set_ylabel('Retirement Age')
        ax2.set_title('Earliest Retirement Age by Portfolio Allocation')
        ax2.set_xlabel('Portfolio Allocation')
        
        # Add value labels on bars
        for bar, age in zip(bars2, retirement_ages):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{age}', ha='center', va='bottom')
        
        # Rotate x-axis labels for better readability
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save chart
        filename = "portfolio_comparison.png"
        filepath = os.path.join(self.output_directory, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_percentile_chart(self, results: RetirementResults, 
                                portfolio_name: str) -> str:
        """
        Generate a percentile chart for a specific portfolio.
        
        Args:
            results: Retirement analysis results
            portfolio_name: Name of the portfolio to chart
            
        Returns:
            Path to the generated chart file
        """
        if portfolio_name not in results.percentile_data:
            raise ValueError(f"Portfolio '{portfolio_name}' not found in results")
        
        percentile_data = results.percentile_data[portfolio_name]
        
        # Find the corresponding result for this portfolio
        portfolio_result = None
        for result in results.portfolio_results:
            if result.portfolio_allocation.name == portfolio_name:
                portfolio_result = result
                break
        
        if portfolio_result is None:
            raise ValueError(f"Portfolio result not found for '{portfolio_name}'")
        
        # Create time axis (years from retirement to age 100)
        years_in_retirement = 100 - portfolio_result.retirement_age
        years = np.arange(0, years_in_retirement + 1)
        ages = np.arange(portfolio_result.retirement_age, 101)
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot percentile ranges
        p10 = percentile_data["10th"]
        p50 = percentile_data["50th"]
        p90 = percentile_data["90th"]
        
        # Fill areas between percentiles
        ax.fill_between(ages, p10, p90, alpha=0.3, color='lightblue', 
                       label='10th-90th Percentile Range')
        ax.fill_between(ages, p10, p50, alpha=0.5, color='steelblue', 
                       label='10th-50th Percentile Range')
        
        # Plot median line
        ax.plot(ages, p50, color='darkblue', linewidth=2, label='Median (50th Percentile)')
        
        # Add zero line
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Portfolio Depleted')
        
        # Formatting
        ax.set_xlabel('Age')
        ax.set_ylabel('Portfolio Value (£)')
        
        # Determine if portfolio grows or shrinks
        trend_note = ""
        if len(p50) > 1:
            if p50[-1] > p50[0]:
                trend_note = " (Portfolio grows during retirement)"
            else:
                trend_note = " (Portfolio declines during retirement)"
        
        ax.set_title(f'Portfolio Value Projections - {portfolio_name}\\n'
                    f'Retirement Age: {portfolio_result.retirement_age}, '
                    f'Success Rate: {portfolio_result.success_rate:.1%}{trend_note}')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        safe_name = portfolio_name.replace('/', '_').replace(' ', '_')
        filename = f"percentiles_{safe_name}.png"
        filepath = os.path.join(self.output_directory, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_all_percentile_charts(self, results: RetirementResults) -> List[str]:
        """
        Generate percentile charts for all portfolios.
        
        Args:
            results: Retirement analysis results
            
        Returns:
            List of paths to generated chart files
        """
        chart_files = []
        
        for portfolio_name in results.percentile_data.keys():
            try:
                filepath = self.generate_percentile_chart(results, portfolio_name)
                chart_files.append(filepath)
            except Exception as e:
                print(f"Warning: Could not generate chart for {portfolio_name}: {e}")
        
        return chart_files
    
    def generate_savings_projection_chart(self, results: RetirementResults) -> str:
        """
        Generate a chart showing savings accumulation before retirement.
        
        Args:
            results: Retirement analysis results
            
        Returns:
            Path to the generated chart file
        """
        user_input = results.user_input
        recommended_age = results.recommended_retirement_age
        
        # Calculate savings accumulation
        years_to_retirement = recommended_age - user_input.current_age
        ages = np.arange(user_input.current_age, recommended_age + 1)
        
        # Simple accumulation model (without market returns for simplicity)
        savings_values = []
        current_savings = user_input.current_savings
        annual_savings = user_input.monthly_savings * 12
        
        for year in range(years_to_retirement + 1):
            if year == 0:
                savings_values.append(current_savings)
            else:
                # Add annual savings and assume 5% real growth
                current_savings += annual_savings
                current_savings *= 1.05  # 5% real growth assumption
                savings_values.append(current_savings)
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(ages, savings_values, color='darkgreen', linewidth=3, marker='o', 
                markersize=4, label='Projected Savings')
        
        # Add current position marker
        ax.scatter(user_input.current_age, user_input.current_savings, 
                  color='red', s=100, zorder=5, label='Current Position')
        
        # Add retirement marker
        ax.scatter(recommended_age, savings_values[-1], 
                  color='blue', s=100, zorder=5, label='Retirement Target')
        
        # Formatting
        ax.set_xlabel('Age')
        ax.set_ylabel('Portfolio Value (£)')
        ax.set_title(f'Savings Accumulation Projection\\n'
                    f'Monthly Savings: £{user_input.monthly_savings:,.0f}, '
                    f'Target Retirement: Age {recommended_age}')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
        
        # Add legend and grid
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        filename = "savings_projection.png"
        filepath = os.path.join(self.output_directory, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_comprehensive_report_charts(self, results: RetirementResults, 
                                           show_progress: bool = True) -> Dict[str, str]:
        """
        Generate all charts for a comprehensive retirement report.
        
        Args:
            results: Retirement analysis results
            show_progress: Whether to show progress bar
            
        Returns:
            Dictionary mapping chart types to file paths
        """
        chart_files = {}
        
        # Define chart generation tasks
        chart_tasks = [
            ("Portfolio Comparison", lambda: self.generate_portfolio_comparison_chart(results)),
            ("Savings Projection", lambda: self.generate_savings_projection_chart(results)),
            ("Recommended Portfolio Percentiles", lambda: self.generate_percentile_chart(
                results, results.recommended_portfolio.name)),
            ("All Portfolio Percentiles", lambda: self.generate_all_percentile_charts(results))
        ]
        
        # Create progress bar for chart generation
        progress_bar = tqdm(
            chart_tasks,
            desc="Generating charts",
            unit="chart",
            disable=not show_progress,
            leave=True
        )
        
        try:
            for task_name, task_func in progress_bar:
                progress_bar.set_description(f"Generating {task_name}")
                
                if task_name == "Portfolio Comparison":
                    chart_files['portfolio_comparison'] = task_func()
                elif task_name == "Savings Projection":
                    chart_files['savings_projection'] = task_func()
                elif task_name == "Recommended Portfolio Percentiles":
                    chart_files['recommended_percentiles'] = task_func()
                elif task_name == "All Portfolio Percentiles":
                    all_percentile_files = task_func()
                    chart_files['all_percentiles'] = all_percentile_files
                    
                progress_bar.set_postfix(completed=f"{len([f for f in chart_files.values() if f])}")
            
            if show_progress:
                total_charts = len(chart_files.get('all_percentiles', [])) + 3  # 3 main charts + percentile charts
                print(f"✅ Chart generation complete! Generated {total_charts} chart files.")
            
        except Exception as e:
            if show_progress:
                print(f"❌ Error generating charts: {e}")
            else:
                print(f"Error generating charts: {e}")
        
        return chart_files
    
    def create_chart_summary(self, chart_files: Dict[str, str]) -> str:
        """
        Create a summary of generated charts.
        
        Args:
            chart_files: Dictionary of chart types to file paths
            
        Returns:
            Summary text of generated charts
        """
        summary_lines = ["Generated Charts:"]
        
        for chart_type, filepath in chart_files.items():
            if isinstance(filepath, list):
                summary_lines.append(f"  {chart_type}: {len(filepath)} files")
            else:
                filename = os.path.basename(filepath)
                summary_lines.append(f"  {chart_type}: {filename}")
        
        return "\\n".join(summary_lines)
    
    def cleanup_old_charts(self, max_age_days: int = 30):
        """
        Clean up old chart files.
        
        Args:
            max_age_days: Maximum age of chart files to keep
        """
        if not os.path.exists(self.output_directory):
            return
        
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        for filename in os.listdir(self.output_directory):
            filepath = os.path.join(self.output_directory, filename)
            
            if os.path.isfile(filepath) and filename.endswith('.png'):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_time:
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        print(f"Warning: Could not remove old chart file {filename}: {e}")
    
    def validate_chart_data(self, results: RetirementResults) -> bool:
        """
        Validate that results contain sufficient data for chart generation.
        
        Args:
            results: Retirement analysis results
            
        Returns:
            True if data is valid for charting, False otherwise
        """
        try:
            # Check basic structure
            if not results.portfolio_results:
                return False
            
            # Check percentile data
            if not results.percentile_data:
                return False
            
            # Check that each portfolio has valid data
            for result in results.portfolio_results:
                if result.portfolio_values is None or len(result.portfolio_values) == 0:
                    return False
            
            return True
            
        except Exception:
            return False