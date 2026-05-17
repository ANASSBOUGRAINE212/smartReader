"""
SmartReader Pi Server - Main Flask Application
"""

from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

def create_app():
    """Application factory for Flask app"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'smartreader-secret-key'
    
    # Enable CORS for mobile app access
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize SocketIO with gevent (works better with Python 3.13)
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*",
        async_mode='gevent',
        logger=False,
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    
    # Register API blueprint
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register WebSocket events
    from .routes.websocket import register_websocket_events
    register_websocket_events(socketio)
    
    # Register Blind Assistant WebSocket events
    from .routes.blind_assistant import register_blind_assistant_events
    register_blind_assistant_events(socketio)
    
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    # Run on all interfaces, port 5000
    print('Starting SmartReader Pi Server on http://0.0.0.0:5000')
    print('WebSocket available at ws://0.0.0.0:5000/ws/audio')
    print('Blind Assistant available at ws://0.0.0.0:5000/ws/blind-assistant')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
