"""
Basic functional tests for the retirement calculator web application.
Tests the main calculation endpoints and form validation.
"""

import pytest
import json
from app import create_app
from src.models import UserInput


@pytest.fixture
def app():
    """Create test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_index_page_loads(client):
    """Test that the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Calculate Your Retirement' in response.data
    assert b'Target Success Rate' in response.data


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'retirement-calculator-web'


def test_portfolios_endpoint(client):
    """Test the portfolios endpoint."""
    response = client.get('/portfolios')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'portfolios' in data
    assert len(data['portfolios']) > 0


def test_calculation_endpoint_valid_input(client):
    """Test the calculation endpoint with valid input."""
    test_data = {
        'current_age': 35,
        'current_savings': 50000,
        'monthly_savings': 1000,
        'desired_annual_income': 30000,
        'target_success_rate': 95
    }
    
    response = client.post('/calculate', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'results' in data
    assert 'user_input' in data
    assert 'charts' in data
    assert len(data['results']) > 0


def test_calculation_endpoint_invalid_input(client):
    """Test the calculation endpoint with invalid input."""
    test_data = {
        'current_age': 150,  # Invalid age
        'current_savings': -1000,  # Invalid savings
        'monthly_savings': 1000,
        'desired_annual_income': 30000,
        'target_success_rate': 95
    }
    
    response = client.post('/calculate', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data


def test_calculation_endpoint_missing_fields(client):
    """Test the calculation endpoint with missing required fields."""
    test_data = {
        'current_age': 35,
        # Missing required fields
    }
    
    response = client.post('/calculate', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False


def test_user_input_model():
    """Test the UserInput model validation."""
    # Valid input
    user_input = UserInput(
        current_age=35,
        current_savings=50000,
        monthly_savings=1000,
        desired_annual_income=30000,
        target_success_rate=0.95
    )
    assert user_input.current_age == 35
    assert user_input.target_success_rate == 0.95
    
    # Test invalid input
    with pytest.raises(ValueError):
        UserInput(
            current_age=150,  # Invalid age
            current_savings=50000,
            monthly_savings=1000,
            desired_annual_income=30000,
            target_success_rate=0.95
        )


def test_quick_test_endpoint(client):
    """Test the quick test endpoint."""
    response = client.post('/api/quick-test')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'calculation_time' in data
    assert 'recommended_portfolio' in data


def test_deployment_status(client):
    """Test the deployment status endpoint."""
    response = client.get('/deployment-status')
    assert response.status_code == 200
    # Should return HTML page
    assert b'Deployment Status' in response.data or response.content_type == 'text/html'


def test_form_validation_javascript_structure(client):
    """Test that the form validation JavaScript is included."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'form-validation.js' in response.data or b'FormValidator' in response.data


def test_results_handler_javascript_structure(client):
    """Test that the results handler JavaScript is included."""
    response = client.get('/')
    assert response.status_code == 200
    # The JavaScript should be loaded via the base template
    assert b'results-handler.js' in response.data or b'ResultsHandler' in response.data


def test_progress_bar_html_structure(client):
    """Test that the progress bar HTML is included."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'progress-container' in response.data
    assert b'progress-bar' in response.data


def test_notification_system_html_structure(client):
    """Test that the notification system HTML is included."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'notification-container' in response.data
    assert b'notification-title' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])