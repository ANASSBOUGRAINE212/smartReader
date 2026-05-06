"""
SmartReader Pi Server - History Service
Manages document history persistence and retrieval
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Service for managing reading history
    Stores scan results with metadata and audio files
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize history service
        
        Args:
            data_dir: Directory for storing history data
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '../../data')
        
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, 'history.json')
        self.audio_dir = os.path.join(os.path.dirname(__file__), '../../audio')
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # Initialize history file if it doesn't exist
        if not os.path.exists(self.history_file):
            self._save_history([])
    
    def save_scan(
        self,
        scan_id: str,
        text: str,
        audio_path: Optional[str],
        language: str,
        paragraph_count: int,
        translated: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save scan to history
        
        Args:
            scan_id: Unique scan identifier
            text: Extracted text
            audio_path: Path to audio file
            language: Document language
            paragraph_count: Number of paragraphs
            translated: Optional translation data
            
        Returns:
            Scan ID
        """
        try:
            # Generate title (first 6 words)
            title = self._generate_title(text)
            
            # Create history entry
            entry = {
                'id': scan_id,
                'title': title,
                'text': text,
                'audioUrl': f'/audio/{os.path.basename(audio_path)}' if audio_path else None,
                'timestamp': datetime.now().isoformat(),
                'language': language,
                'paragraphCount': paragraph_count
            }
            
            # Add translation if provided
            if translated:
                entry['translated'] = translated
            
            # Load existing history
            history = self._load_history()
            
            # Add new entry at the beginning
            history.insert(0, entry)
            
            # Save updated history
            self._save_history(history)
            
            logger.info(f"Scan saved to history: {scan_id}")
            return scan_id
            
        except Exception as e:
            logger.error(f"Failed to save scan to history: {e}")
            raise
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all history entries (list view with id, title, timestamp)
        
        Returns:
            List of history entries
        """
        try:
            history = self._load_history()
            
            # Return simplified list for history view
            return [
                {
                    'id': entry['id'],
                    'title': entry['title'],
                    'timestamp': entry['timestamp']
                }
                for entry in history
            ]
            
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []
    
    def get_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific history entry by ID
        
        Args:
            entry_id: Entry identifier
            
        Returns:
            Full history entry or None if not found
        """
        try:
            history = self._load_history()
            
            for entry in history:
                if entry['id'] == entry_id:
                    return entry
            
            logger.warning(f"History entry not found: {entry_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get history entry: {e}")
            return None
    
    def delete(self, entry_id: str) -> bool:
        """
        Delete history entry and associated audio file
        
        Args:
            entry_id: Entry identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            history = self._load_history()
            
            # Find entry
            entry_to_delete = None
            for i, entry in enumerate(history):
                if entry['id'] == entry_id:
                    entry_to_delete = entry
                    del history[i]
                    break
            
            if entry_to_delete is None:
                logger.warning(f"History entry not found for deletion: {entry_id}")
                return False
            
            # Delete audio file if it exists
            if entry_to_delete.get('audioUrl'):
                audio_filename = os.path.basename(entry_to_delete['audioUrl'])
                audio_path = os.path.join(self.audio_dir, audio_filename)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    logger.info(f"Deleted audio file: {audio_path}")
            
            # Delete translated audio if it exists
            if entry_to_delete.get('translated', {}).get('audioUrl'):
                audio_filename = os.path.basename(entry_to_delete['translated']['audioUrl'])
                audio_path = os.path.join(self.audio_dir, audio_filename)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    logger.info(f"Deleted translated audio file: {audio_path}")
            
            # Save updated history
            self._save_history(history)
            
            logger.info(f"History entry deleted: {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete history entry: {e}")
            return False
    
    def _generate_title(self, text: str) -> str:
        """
        Generate title from text (first 6 words)
        
        Args:
            text: Full text
            
        Returns:
            Title string
        """
        if not text or not text.strip():
            return "Untitled"
        
        # Split into words
        words = text.strip().split()
        
        # Take first 6 words
        title_words = words[:6]
        
        # Join and add ellipsis if there are more words
        title = ' '.join(title_words)
        if len(words) > 6:
            title += '...'
        
        return title
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Load history from file
        
        Returns:
            List of history entries
        """
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history file: {e}")
            return []
    
    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """
        Save history to file
        
        Args:
            history: List of history entries
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history file: {e}")
            raise
