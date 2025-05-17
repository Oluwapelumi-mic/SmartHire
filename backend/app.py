from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from api.routes import api_bp
from models.db import init_db

# Load environment variables
load_dotenv()

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///smarthire.db'),
        ML_MODEL_PATH=os.environ.get('ML_MODEL_PATH', '../ml/models/trained/'),
    )
    
    # Enable CORS
    CORS(app)
    
    # Initialize the database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {"status": "SmartHire API is running"}
    
    return app

# For development server
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)