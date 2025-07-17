"""
Web routes for the retirement calculator Flask application.

This module provides Flask blueprint routes that integrate the existing CLI
calculation engine with web endpoints, including progress tracking and
loading states for calculations.
"""

from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.exceptions import BadRequest
import traceback
import time
import uuid
import os
import sys
import flask
from datetime import datetime
from typing import Dict, Any, Optional

# Import existing CLI modules
from src.models import UserInput
from src.data_manager import HistoricalDataManager
from src.portfolio_manager import PortfolioManager
from src.tax_calculator import UKTaxCalculator
from src.guard_rails import GuardRailsEngine
from src.simulator import MonteCarloSimulator
from forms import CalculatorForm
from chart_generator import generate_all_charts, create_mobile_optimized_config, create_desktop_config


# Create blueprint for calculator routes
calculator_routes = Blueprint('calculator', __name__)

# Global instances for reuse (initialized on first request)
_data_manager = None
_portfolio_manager = None
_tax_calculator = None
_guard_rails_engine = None
_simulator = None
_calculation_progress = {}  # Store calculation progress by session ID


def get_calculation_engine():
    """
    Get or initialize the calculation engine components.
    
    Returns:
        Tuple of (data_manager, portfolio_manager, tax_calculator, guard_rails_engine, simulator)
    """
    global _data_manager, _portfolio_manager, _tax_calculator, _guard_rails_engine, _simulator
    
    if _data_manager is None:
        try:
            # Initialize data manager and load historical data
            _data_manager = HistoricalDataManager()
            _data_manager.load_all_data(validate_quality=False)  # Skip validation for web performance
            
            # Initialize other components
            _portfolio_manager = PortfolioManager(_data_manager)
            _tax_calculator = UKTaxCalculator()
            _guard_rails_engine = GuardRailsEngine()
            
            # Initialize simulator with reduced simulations for web performance
            _simulator = MonteCarloSimulator(
                _data_manager, 
                _portfolio_manager, 
                _tax_calculator, 
                _guard_rails_engine,
                num_simulations=2000  # Further reduced for faster web response (still statistically valid)
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize calculation engine: {str(e)}")
    
    return _data_manager, _portfolio_manager, _tax_calculator, _guard_rails_engine, _simulator


@calculator_routes.route('/')
def index():
    """
    Main calculator page with input form.
    
    Returns:
        Rendered HTML template with calculator form
    """
    form = CalculatorForm()
    return render_template('index.html', form=form)


@calculator_routes.route('/calculate', methods=['POST'])
def calculate():
    """
    Main calculation endpoint that processes user input and returns results.
    
    Accepts form data, validates it, runs Monte Carlo simulation using existing
    CLI modules, and returns JSON response with results and charts data.
    
    Returns:
        JSON response with calculation results or error information
    """
    try:
        # Parse form data
        if request.is_json:
            form_data = request.get_json()
            form = CalculatorForm(data=form_data)
        else:
            form = CalculatorForm(request.form)
        
        # Validate form data
        if not form.validate():
            return jsonify({
                'success': False,
                'error': 'Invalid input data',
                'errors': form.get_validation_errors()
            }), 400
        
        # Convert to UserInput model
        user_input = form.to_user_input()
        
        # Generate calculation session ID for progress tracking
        calc_id = str(uuid.uuid4())
        session['calc_id'] = calc_id
        
        # Initialize progress tracking
        _calculation_progress[calc_id] = {
            'status': 'starting',
            'progress': 0,
            'current_portfolio': None,
            'total_portfolios': 0,
            'start_time': time.time()
        }
        
        # Get calculation engine
        data_manager, portfolio_manager, tax_calculator, guard_rails_engine, simulator = get_calculation_engine()
        
        # Get all portfolio allocations
        allocations = portfolio_manager.get_all_allocations()
        total_portfolios = len(allocations)
        
        _calculation_progress[calc_id].update({
            'total_portfolios': total_portfolios,
            'status': 'running'
        })
        
        # Run calculations for each portfolio
        results = []
        portfolio_names = list(allocations.keys())
        
        for i, (name, allocation) in enumerate(allocations.items()):
            # Update progress
            _calculation_progress[calc_id].update({
                'progress': int((i / total_portfolios) * 100),
                'current_portfolio': name,
                'status': 'calculating'
            })
            
            try:
                # Find optimal retirement age for this portfolio
                optimal_age = simulator.find_optimal_retirement_age(
                    user_input, 
                    allocation, 
                    target_success_rate=0.99,  # 99% confidence as per requirements
                    show_progress=False
                )
                
                if optimal_age is not None:
                    # Run full simulation for optimal age
                    result = simulator.run_simulation_for_retirement_age(
                        user_input, 
                        allocation, 
                        optimal_age, 
                        show_progress=False
                    )
                    
                    # Convert result to JSON-serializable format
                    result_data = {
                        'portfolio_name': name,
                        'portfolio_allocation': {
                            'name': allocation.name,
                            'equity_percentage': allocation.equity_percentage,
                            'bond_percentage': allocation.bond_percentage,
                            'cash_percentage': allocation.cash_percentage
                        },
                        'retirement_age': result.retirement_age,
                        'success_rate': result.success_rate,
                        'final_portfolio_value': result.final_portfolio_value,
                        'percentile_data': {
                            k: v.tolist() if hasattr(v, 'tolist') else v 
                            for k, v in (result.percentile_data or {}).items()
                        }
                    }
                    
                    results.append(result_data)
                else:
                    # Portfolio cannot achieve target success rate
                    result_data = {
                        'portfolio_name': name,
                        'portfolio_allocation': {
                            'name': allocation.name,
                            'equity_percentage': allocation.equity_percentage,
                            'bond_percentage': allocation.bond_percentage,
                            'cash_percentage': allocation.cash_percentage
                        },
                        'retirement_age': None,
                        'success_rate': 0.0,
                        'final_portfolio_value': 0.0,
                        'percentile_data': {}
                    }
                    
                    results.append(result_data)
                    
            except Exception as e:
                # Handle individual portfolio calculation errors
                print(f"Error calculating {name}: {str(e)}")
                result_data = {
                    'portfolio_name': name,
                    'portfolio_allocation': {
                        'name': allocation.name,
                        'equity_percentage': allocation.equity_percentage,
                        'bond_percentage': allocation.bond_percentage,
                        'cash_percentage': allocation.cash_percentage
                    },
                    'retirement_age': None,
                    'success_rate': 0.0,
                    'final_portfolio_value': 0.0,
                    'percentile_data': {},
                    'error': str(e)
                }
                
                results.append(result_data)
        
        # Find recommended portfolio (earliest retirement with 99% confidence)
        successful_results = [r for r in results if r['success_rate'] >= 0.99 and r['retirement_age'] is not None]
        
        if successful_results:
            recommended = min(successful_results, key=lambda x: x['retirement_age'])
            recommended_portfolio = recommended['portfolio_name']
            recommended_age = recommended['retirement_age']
        else:
            # No portfolio achieves 99% confidence
            recommended_portfolio = None
            recommended_age = None
        
        # Generate charts for web display
        _calculation_progress[calc_id].update({
            'status': 'generating_charts',
            'progress': 95,
            'current_portfolio': 'Generating charts...'
        })
        
        try:
            # Detect mobile device from user agent (simple detection)
            user_agent = request.headers.get('User-Agent', '').lower()
            is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad'])
            
            # Use appropriate chart configuration
            chart_config = create_mobile_optimized_config() if is_mobile else create_desktop_config()
            
            # Generate all charts
            charts_data = generate_all_charts(results, chart_config)
            
        except Exception as e:
            print(f"Error generating charts: {str(e)}")
            # Continue without charts if generation fails
            charts_data = {
                'portfolio_charts': {},
                'comparison_chart': None,
                'success_rate_chart': None,
                'retirement_age_chart': None,
                'selector_data': {'options': [], 'default': None},
                'chart_count': 0,
                'has_successful_portfolios': len(successful_results) > 0,
                'error': 'Chart generation failed'
            }
        
        # Update progress to complete
        calculation_time = time.time() - _calculation_progress[calc_id]['start_time']
        _calculation_progress[calc_id].update({
            'status': 'complete',
            'progress': 100,
            'calculation_time': calculation_time
        })
        
        # Prepare response
        response_data = {
            'success': True,
            'calculation_id': calc_id,
            'user_input': {
                'current_age': user_input.current_age,
                'current_savings': user_input.current_savings,
                'monthly_savings': user_input.monthly_savings,
                'desired_annual_income': user_input.desired_annual_income
            },
            'results': results,
            'recommended_portfolio': recommended_portfolio,
            'recommended_age': recommended_age,
            'calculation_time': calculation_time,
            'total_portfolios': total_portfolios,
            'charts': charts_data
        }
        
        return jsonify(response_data)
        
    except ValueError as e:
        # Handle validation errors
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(e)
        }), 400
        
    except RuntimeError as e:
        # Handle calculation engine initialization errors
        return jsonify({
            'success': False,
            'error': 'System error',
            'message': str(e)
        }), 500
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error in calculate endpoint: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during calculation'
        }), 500


@calculator_routes.route('/progress/<calc_id>')
def get_progress(calc_id):
    """
    Get calculation progress for a specific calculation ID.
    
    Args:
        calc_id: Calculation session ID
        
    Returns:
        JSON response with current progress information
    """
    try:
        if calc_id not in _calculation_progress:
            return jsonify({
                'success': False,
                'error': 'Calculation not found'
            }), 404
        
        progress_data = _calculation_progress[calc_id].copy()
        
        # Add elapsed time
        if 'start_time' in progress_data:
            progress_data['elapsed_time'] = time.time() - progress_data['start_time']
        
        return jsonify({
            'success': True,
            'progress': progress_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error retrieving progress',
            'message': str(e)
        }), 500


@calculator_routes.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and deployment verification.
    
    Returns:
        JSON response with system health status
    """
    try:
        # Test calculation engine initialization
        get_calculation_engine()
        
        return jsonify({
            'status': 'healthy',
            'service': 'retirement-calculator-web',
            'calculation_engine': 'ready',
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'retirement-calculator-web',
            'error': str(e),
            'timestamp': time.time()
        }), 500


@calculator_routes.route('/deployment-status')
def deployment_status():
    """
    Deployment status page for monitoring and debugging.
    
    Returns:
        Rendered template with deployment status information
    """
    try:
        # Get environment information
        env_info = {
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'python_version': sys.version.split()[0],
            'flask_version': flask.__version__
        }
        
        # Get calculation engine information
        try:
            data_manager, portfolio_manager, tax_calc, guard_rails, simulator = get_calculation_engine()
            data_files_count = len(os.listdir('data')) if os.path.exists('data') else 0
            portfolio_count = len(portfolio_manager.get_all_allocations()) if portfolio_manager else 0
            
            engine_info = {
                'data_files_count': data_files_count,
                'portfolio_count': portfolio_count,
                'last_test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            }
        except Exception as e:
            engine_info = {
                'data_files_count': 0,
                'portfolio_count': 0,
                'last_test_time': f'Error: {str(e)}'
            }
        
        # Get system information
        system_info = {
            'memory_usage': 'N/A',  # psutil not available in Vercel
            'uptime': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'region': os.environ.get('VERCEL_REGION', 'local')
        }
        
        # Get deployment information
        deployment_info = {
            'deployment_id': os.environ.get('VERCEL_DEPLOYMENT_ID', 'dev-local'),
            'build_time': os.environ.get('VERCEL_BUILD_TIME', 'N/A'),
            'git_commit': os.environ.get('VERCEL_GIT_COMMIT_SHA', 'N/A')[:8] if os.environ.get('VERCEL_GIT_COMMIT_SHA') else 'N/A',
            'version': '1.0.0'
        }
        
        return render_template('deployment-status.html',
                             env_info=env_info,
                             engine_info=engine_info,
                             system_info=system_info,
                             deployment_info=deployment_info)
        
    except Exception as e:
        return jsonify({
            'error': 'Error loading deployment status',
            'message': str(e)
        }), 500


@calculator_routes.route('/api/quick-test', methods=['POST'])
def quick_test():
    """
    Quick test endpoint for deployment verification.
    
    Returns:
        JSON response with test results
    """
    try:
        # Get test data from request
        data = request.get_json()
        if not data:
            data = {
                'current_age': 35,
                'current_savings': 50000,
                'monthly_savings': 500,
                'desired_annual_income': 40000
            }
        
        # Run quick calculation
        start_time = time.time()
        
        # Create user input
        user_input = UserInput(
            current_age=data['current_age'],
            current_savings=data['current_savings'],
            monthly_savings=data['monthly_savings'],
            desired_annual_income=data['desired_annual_income']
        )
        
        # Get calculation components
        data_manager, portfolio_manager, tax_calculator, guard_rails_engine, simulator = get_calculation_engine()
        
        # Run simulation for one portfolio only (for speed)
        allocations = portfolio_manager.get_all_allocations()
        test_allocation = allocations[0]  # Use first allocation for quick test
        
        # Run simulation
        simulation_results = simulator.run_simulation(
            user_input=user_input,
            portfolio_allocation=test_allocation,
            tax_calculator=tax_calculator,
            guard_rails_engine=guard_rails_engine,
            num_simulations=100  # Reduced for speed
        )
        
        calculation_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'calculation_time': round(calculation_time, 2),
            'recommended_portfolio': test_allocation.name,
            'recommended_age': simulation_results.retirement_age,
            'total_portfolios': len(allocations),
            'test_success_rate': simulation_results.success_rate
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'calculation_time': 0
        }), 500


@calculator_routes.route('/portfolios')
def get_portfolios():
    """
    Get available portfolio allocations information.
    
    Returns:
        JSON response with portfolio allocation details
    """
    try:
        data_manager, portfolio_manager, _, _, _ = get_calculation_engine()
        allocations = portfolio_manager.get_all_allocations()
        
        portfolio_info = []
        for name, allocation in allocations.items():
            portfolio_info.append({
                'name': name,
                'equity_percentage': allocation.equity_percentage,
                'bond_percentage': allocation.bond_percentage,
                'cash_percentage': allocation.cash_percentage,
                'is_dynamic': getattr(allocation, 'is_dynamic', False)
            })
        
        return jsonify({
            'success': True,
            'portfolios': portfolio_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error retrieving portfolios',
            'message': str(e)
        }), 500


@calculator_routes.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': 'Invalid request data'
    }), 400


@calculator_routes.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404


@calculator_routes.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


def cleanup_old_progress():
    """
    Clean up old calculation progress entries to prevent memory leaks.
    Should be called periodically or on application startup.
    """
    current_time = time.time()
    old_entries = []
    
    for calc_id, progress in _calculation_progress.items():
        # Remove entries older than 1 hour
        if current_time - progress.get('start_time', current_time) > 3600:
            old_entries.append(calc_id)
    
    for calc_id in old_entries:
        del _calculation_progress[calc_id]