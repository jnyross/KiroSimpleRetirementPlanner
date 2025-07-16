"""
Command-line interface for the retirement calculator.

This module provides the CLI using Click framework for user input collection,
validation, and interaction with the retirement planning system.
"""

import click
import sys
from typing import Optional, Tuple
from .models import UserInput


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
                else:
                    click.echo("Age must be between 18 and 80. Please try again.")
                    
            except click.Abort:
                click.echo("\\nOperation cancelled.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("Please enter a valid age (whole number).")
    
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
                    return savings
                else:
                    click.echo("Savings cannot be negative. Please try again.")
                    
            except click.Abort:
                click.echo("\\nOperation cancelled.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("Please enter a valid amount (e.g., 50000 or 50000.50).")
    
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
                    return savings
                else:
                    click.echo("Monthly savings cannot be negative. Please try again.")
                    
            except click.Abort:
                click.echo("\\nOperation cancelled.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("Please enter a valid amount (e.g., 1000 or 1000.50).")
    
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
                    return income
                else:
                    click.echo("Desired income must be positive. Please try again.")
                    
            except click.Abort:
                click.echo("\\nOperation cancelled.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("Please enter a valid amount (e.g., 30000 or 30000.50).")
    
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
def version():
    """Show version information."""
    click.echo("Kiro Simple Retirement Planner v1.0.0")


if __name__ == '__main__':
    cli()