"""
Flask web application for the retirement calculator.
Uses application factory pattern for better deployment and testing.
Optimized for Vercel deployment.
"""

from flask import Flask
import os


def create_app():
    """
    Application factory pattern for better testing and deployment.
    Creates and configures the Flask application instance.
    """
    app = Flask(__name__)
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        TESTING=False,
        # Vercel-specific configuration
        ENV=os.environ.get('FLASK_ENV', 'development'),
        DEBUG=os.environ.get('FLASK_ENV') != 'production'
    )
    
    # Register calculator routes blueprint
    from routes import calculator_routes
    app.register_blueprint(calculator_routes)
    
    return app


# For Vercel deployment - create app instance at module level
app = create_app()


if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)