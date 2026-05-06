"""
SmartReader Pi Server - WebSocket Routes
WebSocket endpoints for real-time audio streaming
"""

from flask_socketio import emit, disconnect
from typing import Dict, Set

# Track connected clients
connected_clients: Set[str] = set()


def register_websocket_events(socketio):
    """Register WebSocket event handlers"""
    
    @socketio.on('connect', namespace='/ws/audio')
    def handle_connect():
        """Handle client connection"""
        client_id = request.sid if 'request' in dir() else 'unknown'
        connected_clients.add(client_id)
        print(f'Client connected: {client_id}')
        emit('connected', {'message': 'Connected to audio stream'})
    
    @socketio.on('disconnect', namespace='/ws/audio')
    def handle_disconnect():
        """Handle client disconnection"""
        client_id = request.sid if 'request' in dir() else 'unknown'
        if client_id in connected_clients:
            connected_clients.remove(client_id)
        print(f'Client disconnected: {client_id}')
    
    @socketio.on('request_audio', namespace='/ws/audio')
    def handle_audio_request(data):
        """Handle audio stream request from client"""
        scan_id = data.get('scanId')
        print(f'Audio requested for scan: {scan_id}')
        # TODO: Implement in Task 6 (stream audio chunks)
        emit('audio_chunk', {'data': b'', 'complete': True})


def stream_audio_to_clients(socketio, audio_data: bytes, client_id: str = None):
    """
    Stream audio chunks to connected clients
    
    Args:
        socketio: SocketIO instance
        audio_data: Audio data to stream
        client_id: Specific client ID, or None to broadcast to all
    """
    chunk_size = 4096  # 4KB chunks
    
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        is_complete = (i + chunk_size) >= len(audio_data)
        
        if client_id:
            socketio.emit(
                'audio_chunk',
                {'data': chunk, 'complete': is_complete},
                namespace='/ws/audio',
                room=client_id
            )
        else:
            socketio.emit(
                'audio_chunk',
                {'data': chunk, 'complete': is_complete},
                namespace='/ws/audio'
            )


def stop_audio_stream(socketio, client_id: str = None):
    """
    Stop audio streaming
    
    Args:
        socketio: SocketIO instance
        client_id: Specific client ID, or None to broadcast to all
    """
    if client_id:
        socketio.emit(
            'audio_stopped',
            {'message': 'Audio playback stopped'},
            namespace='/ws/audio',
            room=client_id
        )
    else:
        socketio.emit(
            'audio_stopped',
            {'message': 'Audio playback stopped'},
            namespace='/ws/audio'
        )
