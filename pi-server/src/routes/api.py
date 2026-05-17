"""
SmartReader Pi Server - API Routes
REST API endpoints for mobile app communication
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Audio directory path
AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'audio'))


@api_bp.route('/capture/upload', methods=['POST'])
def capture_upload():
    """
    Upload image from phone for OCR
    POST /api/capture/upload
    Body: multipart/form-data with 'image' file
    Returns: ScanResult
    """
    try:
        from ..services.ocr_service import OCRService
        from ..services.tts_service import TTSService
        from ..services.history_service import HistoryService
        from ..services.settings_service import SettingsService
        import uuid
        import numpy as np
        from PIL import Image
        import io
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'error': 'ValidationError',
                'message': 'No image file provided'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'error': 'ValidationError',
                'message': 'Empty filename'
            }), 400
        
        # Load settings
        settings_service = SettingsService()
        settings = settings_service.load_settings()
        
        # Read image from upload
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # Initialize services
        ocr_service = OCRService()
        tts_service = TTSService()
        history_service = HistoryService()
        
        # Extract text with OCR
        ocr_result = ocr_service.extract_text(image_array, engine=settings['ocrEngine'])
        
        if not ocr_result.text:
            return jsonify({
                'error': 'OCRError',
                'message': 'No text detected in image'
            }), 400
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Generate TTS audio
        audio_path = tts_service.synthesize(
            ocr_result.text,
            language=settings['language'],
            rate=settings['speechRate'],
            pitch=settings['speechPitch']
        )
        
        # Play audio on Pi speaker if configured, otherwise send URL to phone
        if audio_path and settings['audioOutput'] == 'pi-speaker':
            logger.info("Playing audio on Pi speaker")
            tts_service.play_audio(audio_path)
            # Don't send audio URL to phone if playing on Pi
            audio_path = None
        elif audio_path:
            logger.info(f"Audio will be played on: {settings['audioOutput']}")
        
        # Save to history
        history_service.save_scan(
            scan_id=scan_id,
            text=ocr_result.text,
            audio_path=audio_path,
            language=ocr_result.detected_language,
            paragraph_count=ocr_result.paragraph_count
        )
        
        # Return scan result
        audio_filename = os.path.basename(audio_path) if audio_path else None
        return jsonify({
            'id': scan_id,
            'text': ocr_result.text,
            'audioUrl': f'/api/audio/{audio_filename}' if audio_filename else None,
            'timestamp': datetime.now().isoformat(),
            'language': ocr_result.detected_language,
            'paragraphCount': ocr_result.paragraph_count
        }), 200
        
    except Exception as e:
        logger.exception("Upload scan error")
        return jsonify({'error': 'ScanError', 'message': str(e)}), 500


@api_bp.route('/capture', methods=['POST'])
def capture():
    """
    Trigger document scan using Pi camera with 10s preview
    POST /api/capture
    Returns: ScanResult
    """
    try:
        from ..services.camera_preview import get_preview_instance
        from ..services.ocr_service import OCRService
        from ..services.tts_service import TTSService
        from ..services.history_service import HistoryService
        from ..services.settings_service import SettingsService
        import uuid
        
        # Load current settings
        settings_service = SettingsService()
        settings = settings_service.load_settings()
        
        # Get settings from request or use saved settings
        request_data = request.get_json() if request.is_json else {}
        ocr_engine = request_data.get('ocrEngine', settings['ocrEngine'])
        language = request_data.get('language', settings['language'])
        speech_rate = request_data.get('speechRate', settings['speechRate'])
        speech_pitch = request_data.get('speechPitch', settings['speechPitch'])
        preview_duration = request_data.get('previewDuration', 10)  # Default 10 seconds
        
        # Initialize services
        preview = get_preview_instance()
        ocr_service = OCRService()
        tts_service = TTSService()
        history_service = HistoryService()
        
        # Capture image with preview
        logger.info(f"Starting capture with {preview_duration}s preview")
        image = preview.capture_with_preview(preview_duration=preview_duration)
        
        if image is None:
            return jsonify({
                'error': 'CaptureError',
                'message': 'Failed to capture image from camera'
            }), 500
        
        # Extract text with OCR (no preprocessing needed, preview already shows good image)
        ocr_result = ocr_service.extract_text(image, engine=ocr_engine)
        
        # Check if text was extracted
        if not ocr_result.text:
            return jsonify({
                'error': 'OCRError',
                'message': 'No text detected in image'
            }), 400
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Generate TTS audio
        audio_path = tts_service.synthesize(
            ocr_result.text,
            language=language,
            rate=speech_rate,
            pitch=speech_pitch
        )
        
        if audio_path is None:
            logger.warning("TTS synthesis failed, returning text only")
        else:
            # Play audio on Pi speaker if configured, otherwise send URL to phone
            if settings['audioOutput'] == 'pi-speaker':
                logger.info("Playing audio on Pi speaker")
                tts_service.play_audio(audio_path)
                # Don't send audio URL to phone if playing on Pi
                audio_path = None
            else:
                logger.info(f"Audio will be played on: {settings['audioOutput']}")
        
        # Save to history
        history_service.save_scan(
            scan_id=scan_id,
            text=ocr_result.text,
            audio_path=audio_path,
            language=ocr_result.detected_language,
            paragraph_count=ocr_result.paragraph_count
        )
        
        # TODO: Task 6 - Stream audio via WebSocket
        
        # Return scan result
        audio_filename = os.path.basename(audio_path) if audio_path else None
        return jsonify({
            'id': scan_id,
            'text': ocr_result.text,
            'audioUrl': f'/api/audio/{audio_filename}' if audio_filename else None,
            'timestamp': datetime.now().isoformat(),
            'language': ocr_result.detected_language,
            'paragraphCount': ocr_result.paragraph_count
        }), 200
        
    except Exception as e:
        logger.exception("Scan error")
        return jsonify({'error': 'ScanError', 'message': str(e)}), 500


@api_bp.route('/history', methods=['GET'])
def get_history():
    """
    Get all history entries
    GET /api/history
    Returns: List[HistoryListItem]
    """
    try:
        from ..services.history_service import HistoryService
        
        history_service = HistoryService()
        history = history_service.get_all()
        
        return jsonify(history), 200
    except Exception as e:
        logger.exception("History retrieval error")
        return jsonify({'error': 'HistoryError', 'message': str(e)}), 500


@api_bp.route('/history', methods=['DELETE'])
def clear_all_history():
    """
    Clear all history entries and delete all audio files
    DELETE /api/history
    Returns: Success response
    """
    try:
        from ..services.history_service import HistoryService
        
        history_service = HistoryService()
        count = history_service.clear_all()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {count} entries',
            'count': count
        }), 200
    except Exception as e:
        logger.exception("Clear all history error")
        return jsonify({'error': 'HistoryError', 'message': str(e)}), 500


@api_bp.route('/history/<entry_id>', methods=['GET'])
def get_history_entry(entry_id: str):
    """
    Get specific history entry
    GET /api/history/<id>
    Returns: HistoryEntry
    """
    try:
        from ..services.history_service import HistoryService
        
        history_service = HistoryService()
        entry = history_service.get_by_id(entry_id)
        
        if entry is None:
            return jsonify({'error': 'NotFound', 'message': 'Entry not found'}), 404
        
        return jsonify(entry), 200
    except Exception as e:
        logger.exception("History entry retrieval error")
        return jsonify({'error': 'HistoryError', 'message': str(e)}), 500


@api_bp.route('/history/<entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id: str):
    """
    Delete history entry
    DELETE /api/history/<id>
    Returns: Success response
    """
    try:
        from ..services.history_service import HistoryService
        
        history_service = HistoryService()
        success = history_service.delete(entry_id)
        
        if not success:
            return jsonify({'error': 'NotFound', 'message': 'Entry not found'}), 404
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.exception("History deletion error")
        return jsonify({'error': 'HistoryError', 'message': str(e)}), 500


@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """
    Get current settings
    GET /api/settings
    Returns: Settings
    """
    try:
        from ..services.settings_service import SettingsService
        
        settings_service = SettingsService()
        settings = settings_service.load_settings()
        
        return jsonify(settings), 200
    except Exception as e:
        logger.exception("Settings retrieval error")
        return jsonify({'error': 'SettingsError', 'message': str(e)}), 500


@api_bp.route('/settings', methods=['POST'])
def update_settings():
    """
    Update settings
    POST /api/settings
    Body: Partial<Settings>
    Returns: Settings
    """
    try:
        from ..services.settings_service import SettingsService
        
        settings_update = request.get_json()
        
        if not settings_update:
            return jsonify({'error': 'ValidationError', 'message': 'Request body required'}), 400
        
        settings_service = SettingsService()
        updated_settings = settings_service.save_settings(settings_update)
        
        return jsonify(updated_settings), 200
    except Exception as e:
        logger.exception("Settings update error")
        return jsonify({'error': 'SettingsError', 'message': str(e)}), 500


@api_bp.route('/stop', methods=['POST'])
def stop_playback():
    """
    Stop audio playback
    POST /api/stop
    Returns: Success response
    """
    try:
        # TODO: Implement in Task 6 (Audio playback control)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': 'PlaybackError', 'message': str(e)}), 500


@api_bp.route('/translate', methods=['POST'])
def translate():
    """
    Translate text
    POST /api/translate
    Body: TranslationRequest
    Returns: TranslationResponse
    """
    try:
        from ..services.translation_service import TranslationService
        from ..services.tts_service import TTSService
        import uuid
        
        translation_request = request.get_json()
        
        # Validate request
        if not translation_request:
            return jsonify({'error': 'ValidationError', 'message': 'Request body required'}), 400
        
        text = translation_request.get('text')
        source_language = translation_request.get('sourceLanguage')
        target_language = translation_request.get('targetLanguage')
        
        if not text or not source_language or not target_language:
            return jsonify({
                'error': 'ValidationError',
                'message': 'text, sourceLanguage, and targetLanguage are required'
            }), 400
        
        # Initialize services
        translation_service = TranslationService()
        tts_service = TTSService()
        
        # Translate text
        translated_text = translation_service.translate(
            text,
            source_language,
            target_language
        )
        
        if translated_text is None:
            return jsonify({
                'error': 'TranslationError',
                'message': 'Translation failed'
            }), 500
        
        # Generate TTS for translated text
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = tts_service.synthesize(
            translated_text,
            language=target_language,
            rate=1.0,
            pitch='normal'
        )
        
        if audio_path is None:
            # Translation succeeded but TTS failed
            return jsonify({
                'translatedText': translated_text,
                'audioUrl': None
            }), 200
        
        # Return translation result
        audio_filename = os.path.basename(audio_path) if audio_path else None
        return jsonify({
            'translatedText': translated_text,
            'audioUrl': f'/api/audio/{audio_filename}' if audio_filename else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'TranslationError', 'message': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    GET /api/health
    Returns: HealthResponse
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200


@api_bp.route('/camera/preview', methods=['GET'])
def camera_preview():
    """
    Get camera preview image
    GET /api/camera/preview
    Returns: JPEG image
    """
    try:
        from ..services.capture_service import CaptureService
        import cv2
        
        capture_service = CaptureService()
        image = capture_service.capture_image()
        
        if image is None:
            return jsonify({'error': 'CameraError', 'message': 'Failed to capture image'}), 500
        
        # Encode image as JPEG
        success, buffer = cv2.imencode('.jpg', image)
        if not success:
            return jsonify({'error': 'EncodingError', 'message': 'Failed to encode image'}), 500
        
        # Return image
        from flask import Response
        return Response(buffer.tobytes(), mimetype='image/jpeg')
        
    except Exception as e:
        logger.exception("Camera preview error")
        return jsonify({'error': 'CameraError', 'message': str(e)}), 500


@api_bp.route('/camera/view', methods=['GET'])
def camera_view():
    """
    Serve camera preview HTML page
    GET /api/camera/view
    Returns: HTML page
    """
    try:
        html_path = os.path.join(os.path.dirname(__file__), '..', '..', 'camera_view.html')
        return send_file(html_path)
    except Exception as e:
        logger.exception("Camera view error")
        return jsonify({'error': 'FileError', 'message': str(e)}), 500


@api_bp.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename: str):
    """
    Serve audio files
    GET /api/audio/<filename>
    Returns: Audio file (MP3)
    """
    try:
        # Sanitize filename to prevent directory traversal
        filename = os.path.basename(filename)
        
        # Ensure audio directory exists
        if not os.path.exists(AUDIO_DIR):
            logger.error(f"Audio directory not found: {AUDIO_DIR}")
            return jsonify({'error': 'NotFound', 'message': 'Audio directory not found'}), 404
        
        # Construct absolute file path
        file_path = os.path.abspath(os.path.join(AUDIO_DIR, filename))
        
        # Verify the file is within AUDIO_DIR (security check)
        if not file_path.startswith(os.path.abspath(AUDIO_DIR)):
            logger.error(f"Invalid file path: {file_path}")
            return jsonify({'error': 'Forbidden', 'message': 'Invalid file path'}), 403
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return jsonify({'error': 'NotFound', 'message': f'Audio file not found: {filename}'}), 404
        
        # Serve the file
        logger.info(f"Serving audio file: {file_path}")
        return send_file(file_path, mimetype='audio/mpeg', as_attachment=False)
        
    except Exception as e:
        logger.exception("Audio serving error")
        return jsonify({'error': 'FileError', 'message': str(e)}), 500


@api_bp.route('/camera/preview/start', methods=['POST'])
def start_camera_preview():
    """
    Start camera preview window on Pi
    POST /api/camera/preview/start
    Returns: Success message
    """
    try:
        from ..services.camera_preview import start_camera_preview as start_preview
        
        start_preview()
        
        return jsonify({
            'status': 'success',
            'message': 'Camera preview started'
        }), 200
        
    except Exception as e:
        logger.exception("Failed to start camera preview")
        return jsonify({
            'error': 'PreviewError',
            'message': str(e)
        }), 500


@api_bp.route('/camera/preview/stop', methods=['POST'])
def stop_camera_preview():
    """
    Stop camera preview window on Pi
    POST /api/camera/preview/stop
    Returns: Success message
    """
    try:
        from ..services.camera_preview import stop_camera_preview as stop_preview
        
        stop_preview()
        
        return jsonify({
            'status': 'success',
            'message': 'Camera preview stopped'
        }), 200
        
    except Exception as e:
        logger.exception("Failed to stop camera preview")
        return jsonify({
            'error': 'PreviewError',
            'message': str(e)
        }), 500


@api_bp.route('/camera/preview/status', methods=['GET'])
def camera_preview_status():
    """
    Get camera preview status
    GET /api/camera/preview/status
    Returns: Preview status
    """
    try:
        from ..services.camera_preview import is_preview_running
        
        return jsonify({
            'running': is_preview_running()
        }), 200
        
    except Exception as e:
        logger.exception("Failed to get preview status")
        return jsonify({
            'error': 'PreviewError',
            'message': str(e)
        }), 500
