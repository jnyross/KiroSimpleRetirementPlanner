"""
Command-line interface for the retirement calculator.

This module provides the CLI using Click framework for user input collection,
validation, and interaction with the retirement planning system.
"""

import click
import sys
from typing import Optional, Tuple
from .models import UserInput
from .data_validator import DataValidator


class RetirementCalculatorCLI:
    """Command-line interface for the retirement calculator."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.user_input: Optional[UserInput] = None
        
    def collect_user_input(self) -> UserInput:
        """
        Collect user input through interactive prompts.
        
        Returns:
            UserInput object with validated user data
        """
        click.echo("\\n=== Kiro Simple Retirement Planner ===")
        click.echo("Please provide your current financial information.\\n")
        
        # Collect current age
        current_age = self._prompt_for_age()
        
        # Collect current savings
        current_savings = self._prompt_for_current_savings()
        
        # Collect monthly savings
        monthly_savings = self._prompt_for_monthly_savings()
        
        # Collect desired annual income
        desired_income = self._prompt_for_desired_income()
        
        # Create and validate user input
        try:
            user_input = UserInput(
                current_age=current_age,
                current_savings=current_savings,
                monthly_savings=monthly_savings,
                desired_annual_income=desired_income
            )
            
            # Display summary for confirmation
            self._display_input_summary(user_input)
            
            if click.confirm("\\nDo you want to proceed with these values?"):
                return user_input
            else:
                click.echo("Please restart the application to enter new values.")
                sys.exit(0)
                
        except ValueError as e:
            click.echo(f"\\nError: {e}", err=True)
            sys.exit(1)
    
    def _prompt_for_age(self) -> int:
        """Prompt for current age with validation."""
        while True:
            try:
                age = click.prompt(
                    "What is your current age?",
                    type=int,
                    show_default=False
                )
                
                if 18 <= age <= 80:
                    return age
                elif age < 18:
                    click.echo("⚠️  Age must be at least 18 for retirement planning.")
                    click.echo("   This tool is designed for adults planning their retirement.")
                elif age > 80:
                    click.echo("⚠️  Age must be 80 or younger for meaningful retirement planning.")
                    click.echo("   Consider consulting a financial advisor for immediate retirement needs.")
                else:
                    click.echo("⚠️  Age must be between 18 and 80. Please try again.")
                    
            except click.Abort:
                click.echo("\\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid age as a whole number (e.g., 35).")
                click.echo("   Avoid letters, decimals, or special characters.")
    
    def _prompt_for_current_savings(self) -> float:
        """Prompt for current savings with validation."""
        while True:
            try:
                savings = click.prompt(
                    "What are your current savings (in £)?",
                    type=float,
                    show_default=False
                )
                
                if savings >= 0:
                    if savings == 0:
                        click.echo("💡 Starting with no savings is fine - your monthly contributions will build your retirement fund.")
                    elif savings > 10000000:  # 10 million
                        click.echo("⚠️  That's a very large amount. Please double-check your entry.")
                        if not click.confirm("Is this amount correct?"):
                            continue
                    return savings
                else:
                    click.echo("❌ Savings cannot be negative.")
                    click.echo("   Enter 0 if you have no current savings.")
                    
            except click.Abort:
                click.echo("\\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid monetary amount.")
                click.echo("   Examples: 50000, 50000.50, 0")
                click.echo("   Avoid commas, currency symbols, or letters.")
    
    def _prompt_for_monthly_savings(self) -> float:
        """Prompt for monthly savings with validation."""
        while True:
            try:
                savings = click.prompt(
                    "How much do you save per month (in £)?",
                    type=float,
                    show_default=False
                )
                
                if savings >= 0:
                    if savings == 0:
                        click.echo("⚠️  No monthly savings means retirement will depend entirely on current savings.")
                        click.echo("   Consider saving even a small amount monthly for better outcomes.")
                    elif savings < 100:
                        click.echo("💡 Small monthly savings can still make a big difference over time!")
                    elif savings > 50000:  # Very high monthly savings
                        click.echo("⚠️  That's a very high monthly savings amount. Please double-check your entry.")
                        if not click.confirm("Is this amount correct?"):
                            continue
                    return savings
                else:
                    click.echo("❌ Monthly savings cannot be negative.")
                    click.echo("   Enter 0 if you don't currently save monthly.")
                    
            except click.Abort:
                click.echo("\\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid monetary amount.")
                click.echo("   Examples: 1000, 1500.50, 0")
                click.echo("   Avoid commas, currency symbols, or letters.")
    
    def _prompt_for_desired_income(self) -> float:
        """Prompt for desired annual retirement income with validation."""
        while True:
            try:
                income = click.prompt(
                    "What annual income do you want in retirement (after-tax, in £)?",
                    type=float,
                    show_default=False
                )
                
                if income > 0:
                    if income < 10000:
                        click.echo("⚠️  That's a very low annual income. Consider if this covers your basic needs.")
                        click.echo("   Remember: this is after-tax income in today's purchasing power.")
                        if not click.confirm("Is this amount realistic for your retirement lifestyle?"):
                            continue
                    elif income > 200000:
                        click.echo("⚠️  That's a very high annual income. Please double-check your entry.")
                        click.echo("   Remember: this is after-tax income in today's purchasing power.")
                        if not click.confirm("Is this amount correct?"):
                            continue
                    elif 15000 <= income <= 50000:
                        click.echo("💡 This looks like a reasonable retirement income target.")
                    return income
                else:
                    click.echo("❌ Desired income must be positive.")
                    click.echo("   This represents your target annual spending in retirement.")
                    
            except click.Abort:
                click.echo("\\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid monetary amount.")
                click.echo("   Examples: 30000, 25000.50")
                click.echo("   Avoid commas, currency symbols, or letters.")
    
    def _display_input_summary(self, user_input: UserInput):
        """Display a summary of user input for confirmation."""
        click.echo("\\n=== Input Summary ===")
        click.echo(f"Current Age: {user_input.current_age}")
        click.echo(f"Current Savings: £{user_input.current_savings:,.2f}")
        click.echo(f"Monthly Savings: £{user_input.monthly_savings:,.2f}")
        click.echo(f"Desired Annual Income: £{user_input.desired_annual_income:,.2f}")
        
        # Calculate some helpful metrics
        annual_savings = user_input.monthly_savings * 12
        savings_rate = annual_savings / user_input.desired_annual_income * 100
        
        click.echo(f"\\nCalculated Metrics:")
        click.echo(f"Annual Savings: £{annual_savings:,.2f}")
        click.echo(f"Savings Rate: {savings_rate:.1f}% of desired retirement income")
    
    def display_progress(self, message: str, step: int = 0, total: int = 0):
        """
        Display progress information during calculations.
        
        Args:
            message: Progress message to display
            step: Current step number (optional)
            total: Total number of steps (optional)
        """
        if step > 0 and total > 0:
            progress = step / total * 100
            click.echo(f"[{progress:.1f}%] {message}")
        else:
            click.echo(f"⏳ {message}")
    
    def display_error(self, error_message: str, is_fatal: bool = False):
        """
        Display error message to user.
        
        Args:
            error_message: Error message to display
            is_fatal: Whether this is a fatal error that should exit
        """
        click.echo(f"❌ Error: {error_message}", err=True)
        
        if is_fatal:
            sys.exit(1)
    
    def display_warning(self, warning_message: str):
        """
        Display warning message to user.
        
        Args:
            warning_message: Warning message to display
        """
        click.echo(f"⚠️  Warning: {warning_message}")
    
    def display_success(self, success_message: str):
        """
        Display success message to user.
        
        Args:
            success_message: Success message to display
        """
        click.echo(f"✅ {success_message}")
    
    def prompt_for_details(self, message: str) -> bool:
        """
        Prompt user if they want to see detailed information.
        
        Args:
            message: Message to display with the prompt
            
        Returns:
            True if user wants details, False otherwise
        """
        return click.confirm(f"{message} Would you like to see detailed information?")
    
    def prompt_for_charts(self) -> bool:
        """
        Prompt user if they want to generate charts.
        
        Returns:
            True if user wants charts, False otherwise
        """
        return click.confirm("Would you like to generate charts showing your retirement projections?")
    
    def display_completion_message(self, chart_files: Optional[dict] = None):
        """
        Display completion message with information about generated files.
        
        Args:
            chart_files: Dictionary of generated chart files (optional)
        """
        click.echo("\\n=== Analysis Complete ===")
        
        if chart_files:
            click.echo("\\nGenerated files:")
            for chart_type, filepath in chart_files.items():
                if isinstance(filepath, list):
                    click.echo(f"  {chart_type}: {len(filepath)} chart files")
                else:
                    click.echo(f"  {chart_type}: {filepath}")
        
        click.echo("\\nThank you for using the Kiro Simple Retirement Planner!")
    
    def handle_keyboard_interrupt(self):
        """Handle keyboard interrupt (Ctrl+C) gracefully."""
        click.echo("\\n\\nOperation cancelled by user.")
        sys.exit(0)
    
    def validate_input_interactive(self, user_input: UserInput) -> bool:
        """
        Validate user input interactively with detailed feedback.
        
        Args:
            user_input: User input to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        issues = []
        
        # Check age
        if user_input.current_age < 18:
            issues.append("Age is too young for retirement planning")
        elif user_input.current_age > 80:
            issues.append("Age is too old for meaningful retirement planning")
        
        # Check savings rate
        annual_savings = user_input.monthly_savings * 12
        if annual_savings == 0:
            issues.append("No monthly savings - consider saving for retirement")
        elif annual_savings < user_input.desired_annual_income * 0.05:
            issues.append("Monthly savings appear low relative to desired income")
        
        # Check desired income
        if user_input.desired_annual_income < 10000:
            issues.append("Desired income seems very low - consider if this is realistic")
        elif user_input.desired_annual_income > 200000:
            issues.append("Desired income is very high - ensure this is realistic")
        
        # Display issues if any
        if issues:
            click.echo("\\n⚠️  Input validation warnings:")
            for issue in issues:
                click.echo(f"  - {issue}")
            
            return click.confirm("\\nDo you want to continue with these values?")
        
        return True


# Click command group
@click.group()
def cli():
    """Kiro Simple Retirement Planner - Plan your retirement with confidence."""
    pass


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--charts', '-c', is_flag=True, help='Generate charts automatically')
@click.option('--simulations', '-s', default=10000, help='Number of Monte Carlo simulations')
def calculate(verbose: bool, charts: bool, simulations: int):
    """Run the retirement calculation."""
    cli_handler = RetirementCalculatorCLI()
    
    try:
        # This would be implemented in the main application runner
        click.echo("This command will be implemented in the main application runner.")
        click.echo(f"Options: verbose={verbose}, charts={charts}, simulations={simulations}")
        
    except KeyboardInterrupt:
        cli_handler.handle_keyboard_interrupt()
    except Exception as e:
        cli_handler.display_error(f"Unexpected error: {str(e)}", is_fatal=True)


@cli.command()
@click.option('--data-dir', default='data', help='Directory containing data files')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation output')
def validate_data(data_dir: str, verbose: bool):
    """Validate historical data files for quality and consistency."""
    click.echo("🔍 Validating historical data files...")
    
    try:
        validator = DataValidator(data_dir)
        result = validator.validate_all_data_files()
        
        if result.is_valid:
            click.echo("✅ All data files passed validation!")
            
            if verbose:
                click.echo("\nValidation Details:")
                if result.info:
                    click.echo("Information:")
                    for info in result.info:
                        click.echo(f"  • {info}")
                
                if result.warnings:
                    click.echo("\nWarnings:")
                    for warning in result.warnings:
                        click.echo(f"  ⚠️  {warning}")
        else:
            click.echo("❌ Data validation failed!")
            click.echo("\nErrors:")
            for error in result.errors:
                click.echo(f"  • {error}")
            
            if result.warnings:
                click.echo("\nWarnings:")
                for warning in result.warnings:
                    click.echo(f"  ⚠️  {warning}")
            
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error during validation: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--data-dir', default='data', help='Directory containing data files')
def data_report(data_dir: str):
    """Generate a comprehensive data quality report."""
    click.echo("📊 Generating data quality report...")
    
    try:
        from .data_manager import HistoricalDataManager
        
        data_manager = HistoricalDataManager(data_dir)
        report_content = data_manager.get_data_quality_report()
        click.echo(report_content)
        
    except Exception as e:
        click.echo(f"❌ Error generating report: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("Kiro Simple Retirement Planner v1.0.0")


if __name__ == '__main__':
    cli()