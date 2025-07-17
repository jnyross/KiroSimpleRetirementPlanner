"""
Vercel serverless function handler for the Flask application.
"""

from app import create_app

# Create the Flask application
app = create_app()

# This is the serverless function handler that Vercel will call
handler = app