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
        
        # Collect target success rate
        target_success_rate = self._prompt_for_success_rate()
        
        # New v1.1.0: Ask about advanced features
        click.echo("\n=== Advanced Options (v1.1.0) ===")
        use_advanced = click.confirm("Would you like to configure advanced retirement features?", default=False)
        
        if use_advanced:
            cash_buffer_years = self._prompt_for_cash_buffer()
            state_pension_age, state_pension_amount = self._prompt_for_state_pension()
            spending_phases = self._prompt_for_spending_phases(current_age)
        else:
            # Use defaults
            cash_buffer_years = 2.0
            state_pension_age = 67
            state_pension_amount = 9110.0
            spending_phases = [(75, 0.75)]
        
        # Create and validate user input
        try:
            user_input = UserInput(
                current_age=current_age,
                current_savings=current_savings,
                monthly_savings=monthly_savings,
                desired_annual_income=desired_income,
                target_success_rate=target_success_rate,
                cash_buffer_years=cash_buffer_years,
                state_pension_age=state_pension_age,
                state_pension_amount=state_pension_amount,
                spending_phases=spending_phases
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
    
    def _prompt_for_success_rate(self) -> float:
        """Prompt for target success rate with validation."""
        while True:
            try:
                click.echo("\n💡 Success rate is the probability your money will last until age 100.")
                click.echo("   Common choices: 99% (very conservative), 95% (conservative), 90% (moderate), 85% (aggressive)")
                
                rate = click.prompt(
                    "What success rate do you want to target? (50-100%)",
                    type=float,
                    default=95.0,  # Updated default from 99% to 95% in v1.1.0
                    show_default=True
                )
                
                # Accept both percentage (e.g., 95) and decimal (e.g., 0.95) formats
                if rate > 1:
                    rate = rate / 100.0
                
                if 0.5 <= rate <= 1.0:
                    if rate >= 0.99:
                        click.echo("✅ Very conservative choice - prioritizing security over early retirement")
                    elif rate >= 0.95:
                        click.echo("✅ Conservative choice - good balance of security and flexibility")
                    elif rate >= 0.90:
                        click.echo("✅ Moderate choice - accepting some risk for earlier retirement")
                    elif rate >= 0.85:
                        click.echo("✅ Aggressive choice - prioritizing early retirement over security")
                    else:
                        click.echo("⚠️  Very aggressive choice - significant risk of running out of money")
                        if not click.confirm("Are you sure about this success rate?"):
                            continue
                    
                    return rate
                else:
                    click.echo("❌ Success rate must be between 50% and 100%")
                    
            except click.Abort:
                click.echo("\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid percentage (e.g., 95 or 0.95)")
    
    def _prompt_for_cash_buffer(self) -> float:
        """Prompt for cash buffer years (v1.1.0)."""
        while True:
            try:
                click.echo("\n💡 Cash buffer: Emergency fund held outside your investment portfolio")
                click.echo("   This covers spending during market downturns without selling investments")
                
                years = click.prompt(
                    "How many years of spending would you like in your cash buffer? (0-5)",
                    type=float,
                    default=2.0,
                    show_default=True
                )
                
                if 0 <= years <= 5:
                    if years == 0:
                        click.echo("⚠️  No cash buffer means you'll need to sell investments in down markets")
                    elif years >= 3:
                        click.echo("✅ Conservative cash buffer - good protection against market volatility")
                    else:
                        click.echo("✅ Standard cash buffer - balanced approach")
                    return years
                else:
                    click.echo("❌ Cash buffer must be between 0 and 5 years")
                    
            except click.Abort:
                click.echo("\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid number (e.g., 2 or 2.5)")
    
    def _prompt_for_state_pension(self) -> Tuple[int, float]:
        """Prompt for state pension details (v1.1.0)."""
        # State pension age
        while True:
            try:
                click.echo("\n💡 UK State Pension reduces the amount you need to withdraw from your portfolio")
                
                age = click.prompt(
                    "At what age will you receive state pension?",
                    type=int,
                    default=67,
                    show_default=True
                )
                
                if 60 <= age <= 75:
                    break
                else:
                    click.echo("❌ State pension age must be between 60 and 75")
                    
            except click.Abort:
                click.echo("\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid age (e.g., 67)")
        
        # State pension amount
        while True:
            try:
                amount = click.prompt(
                    "What annual state pension do you expect? (£)",
                    type=float,
                    default=9110.0,
                    show_default=True
                )
                
                if 0 <= amount <= 20000:
                    if amount == 0:
                        click.echo("⚠️  No state pension means higher portfolio withdrawals needed")
                    elif amount < 5000:
                        click.echo("💡 Partial state pension included")
                    else:
                        click.echo("✅ Full state pension included")
                    return age, amount
                else:
                    click.echo("❌ State pension must be between £0 and £20,000")
                    
            except click.Abort:
                click.echo("\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter a valid amount (e.g., 9110)")
    
    def _prompt_for_spending_phases(self, current_age: int) -> list:
        """Prompt for spending phase configuration (v1.1.0)."""
        click.echo("\n💡 Spending phases: Most retirees spend less as they age (travel less, etc.)")
        
        use_phases = click.confirm("Would you like to model reduced spending in later retirement?", default=True)
        
        if not use_phases:
            return []
        
        phases = []
        while True:
            try:
                age = click.prompt(
                    "At what age would spending reduce?",
                    type=int,
                    default=75,
                    show_default=True
                )
                
                if current_age < age <= 100:
                    multiplier = click.prompt(
                        "What percentage of original spending? (e.g., 75 for 75%)",
                        type=float,
                        default=75.0,
                        show_default=True
                    )
                    
                    if 10 <= multiplier <= 100:
                        phases.append((age, multiplier / 100.0))
                        click.echo(f"✅ Spending will reduce to {multiplier:.0f}% at age {age}")
                        
                        if not click.confirm("Add another spending phase?", default=False):
                            break
                    else:
                        click.echo("❌ Spending percentage must be between 10% and 100%")
                else:
                    click.echo(f"❌ Age must be between {current_age + 1} and 100")
                    
            except click.Abort:
                click.echo("\n👋 Operation cancelled by user.")
                sys.exit(0)
            except (ValueError, TypeError):
                click.echo("❌ Please enter valid values")
        
        return sorted(phases, key=lambda x: x[0])  # Sort by age
    
    def _display_input_summary(self, user_input: UserInput):
        """Display a summary of user input for confirmation."""
        click.echo("\\n=== Input Summary ===")
        click.echo(f"Current Age: {user_input.current_age}")
        click.echo(f"Current Savings: £{user_input.current_savings:,.2f}")
        click.echo(f"Monthly Savings: £{user_input.monthly_savings:,.2f}")
        click.echo(f"Desired Annual Income: £{user_input.desired_annual_income:,.2f}")
        click.echo(f"Target Success Rate: {user_input.target_success_rate:.1%}")
        
        # Calculate some helpful metrics
        annual_savings = user_input.monthly_savings * 12
        savings_rate = annual_savings / user_input.desired_annual_income * 100
        
        click.echo(f"\\nCalculated Metrics:")
        click.echo(f"Annual Savings: £{annual_savings:,.2f}")
        click.echo(f"Savings Rate: {savings_rate:.1f}% of desired retirement income")
        
        # Show advanced settings if not using defaults
        if (user_input.cash_buffer_years != 2.0 or 
            user_input.state_pension_age != 67 or 
            user_input.state_pension_amount != 9110.0 or
            len(user_input.spending_phases) > 0):
            click.echo(f"\\nAdvanced Settings (v1.1.0):")
            click.echo(f"Cash Buffer: {user_input.cash_buffer_years:.1f} years")
            click.echo(f"State Pension: £{user_input.state_pension_amount:,.0f} at age {user_input.state_pension_age}")
            
            if user_input.spending_phases:
                click.echo("Spending Phases:")
                for age, multiplier in user_input.spending_phases:
                    click.echo(f"  - Age {age}: {multiplier:.0%} of original spending")
    
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