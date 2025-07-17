"""
Vercel serverless function handler for the Flask application.
"""
import os
import sys

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask application
app = create_app()

# Export the app for Vercel to use
# Vercel expects the variable to be named 'app' for Python runtimes
app = app