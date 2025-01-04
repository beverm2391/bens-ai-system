"""Deepgram API client."""

import os
from typing import Dict, Any, Union
from pathlib import Path
from deepgram import DeepgramClient as DG
from deepgram import PrerecordedOptions, FileSource

class DeepgramClient:
    """Client for Deepgram API interactions.
    
    Note on processing times:
        - Fast models (nova-2, base, enhanced): Max 10 minutes
        - Whisper model: Max 20 minutes
        Requests exceeding these limits will return 504 Gateway Timeout
    """
    
    MODEL_TIMEOUTS = {
        "whisper": 1200,  # 20 minutes
        "nova-2": 600,    # 10 minutes
        "base": 600,
        "enhanced": 600
    }
    
    def __init__(self):
        """Initialize client with API key from environment."""
        self.client = DG()
    
    def _get_timeout(self, model: str) -> int:
        """Get appropriate timeout for model."""
        return self.MODEL_TIMEOUTS.get(model, 600)  # Default 10 min
    
    def transcribe_url(self, url: str, model: str = "nova-2") -> Dict[str, Any]:
        """Transcribe audio from a URL.
        
        Args:
            url: URL of the audio file
            model: Model to use for transcription (default: nova-2)
            
        Returns:
            Dict containing transcription response
            
        Raises:
            TimeoutError: If processing exceeds model's time limit
            Exception: For other transcription failures
        """
        try:
            options = PrerecordedOptions(
                model=model,
                smart_format=True,
            )
            
            response = self.client.listen.rest.v("1").transcribe_url(
                {"url": url}, 
                options,
                timeout=self._get_timeout(model)
            )
            return response
            
        except Exception as e:
            if "504" in str(e):
                raise TimeoutError(f"Processing timeout exceeded for model {model}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def transcribe_file(self, file_path: Union[str, Path], model: str = "nova-2") -> Dict[str, Any]:
        """Transcribe audio from a local file.
        
        Args:
            file_path: Path to local audio file
            model: Model to use for transcription (default: nova-2)
            
        Returns:
            Dict containing transcription response
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            TimeoutError: If processing exceeds model's time limit
            Exception: For other transcription failures
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
                
            with open(file_path, "rb") as f:
                buffer_data = f.read()
            
            payload: FileSource = {
                "buffer": buffer_data,
            }
            
            options = PrerecordedOptions(
                model=model,
                smart_format=True,
            )
            
            response = self.client.listen.rest.v("1").transcribe_file(
                payload,
                options,
                timeout=self._get_timeout(model)
            )
            return response
            
        except Exception as e:
            if "504" in str(e):
                raise TimeoutError(f"Processing timeout exceeded for model {model}")
            raise Exception(f"Transcription failed: {str(e)}")

# Usage example:
# client = DeepgramClient()
# result = client.transcribe_url("https://example.com/audio.wav")
# result = client.transcribe_file("path/to/audio.mp3") 