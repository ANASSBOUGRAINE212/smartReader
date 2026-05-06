"""
SmartReader Pi Server - Main Flask Application
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

def create_app():
    """Application factory for Flask app"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'smartreader-secret-key'
    
    # Enable CORS for mobile app access
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize SocketIO for audio streaming
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register API blueprint
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register WebSocket events
    from .routes.websocket import register_websocket_events
    register_websocket_events(socketio)
    
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    # Run on all interfaces, port 5000
    print('Starting SmartReader Pi Server on http://0.0.0.0:5000')
    print('WebSocket available at ws://0.0.0.0:5000/ws/audio')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
