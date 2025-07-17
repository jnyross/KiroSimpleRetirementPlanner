"""
Vercel serverless function handler for the Flask application.
"""
import os
import sys

# Add the parent directory to the Python path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from app import create_app
    
    # Create the Flask application
    app = create_app()
    
    # Vercel expects a WSGI application
    # The Flask app object is already a WSGI application
    
except Exception as e:
    # If there's an import error, create a simple error response
    def app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        error_message = f"Import error: {str(e)}\nPython path: {sys.path}\nWorking dir: {os.getcwd()}"
        return [error_message.encode('utf-8')]