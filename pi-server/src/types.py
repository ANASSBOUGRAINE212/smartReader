"""
Shared type definitions for SmartReader Pi Server
These types mirror the TypeScript API contracts
"""

from typing import TypedDict, Literal, Optional
from datetime import datetime

Language = Literal['arabic', 'french', 'english', 'darija']
AudioOutput = Literal['pi-speaker', 'phone', 'bluetooth']
OCREngine = Literal['tesseract', 'cloud']
SpeechPitch = Literal['low', 'normal', 'high']
ReadingMode = Literal['continuous', 'paragraph', 'section']


class ScanResult(TypedDict):
    id: str
    text: str
    audioUrl: str
    timestamp: str
    language: Language
    paragraphCount: int


class TranslatedContent(TypedDict):
    targetLanguage: Language
    text: str
    audioUrl: str


class HistoryEntry(TypedDict):
    id: str
    title: str
    text: str
    audioUrl: str
    timestamp: str
    language: Language
    translated: Optional[TranslatedContent]


class HistoryListItem(TypedDict):
    id: str
    title: str
    timestamp: str


class Settings(TypedDict):
    language: Language
    speechRate: float  # 0.5 - 2.0
    speechPitch: SpeechPitch
    readingMode: ReadingMode
    audioOutput: AudioOutput
    ocrEngine: OCREngine


class TranslationRequest(TypedDict):
    text: str
    sourceLanguage: Language
    targetLanguage: Language


class TranslationResponse(TypedDict):
    translatedText: str
    audioUrl: str


class HealthResponse(TypedDict):
    status: Literal['ok']
    timestamp: str


class ErrorResponse(TypedDict):
    error: str
    message: str


class OCRResult(TypedDict):
    text: str
    confidence: float
    detected_language: str
    paragraph_count: int
