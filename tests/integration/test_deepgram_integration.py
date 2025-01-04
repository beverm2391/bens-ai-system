"""Integration tests for Deepgram client."""

import pytest
from pathlib import Path
from src.clients.deepgram_client import DeepgramClient

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "deepgram"

def test_transcribe_url():
    """Test transcription of a sample audio URL."""
    client = DeepgramClient()
    
    # Using Deepgram's sample audio file
    url = "https://dpgr.am/bueller.wav"
    
    response = client.transcribe_url(url)
    
    # Just verify we got a response
    assert response is not None
    # Convert to dict to check basic structure
    response_dict = response.to_dict()
    assert isinstance(response_dict, dict)

def test_transcribe_local_file():
    """Test transcription of a local audio file."""
    client = DeepgramClient()

    # Using local test audio file
    audio_path = FIXTURES_DIR / "short_audio.wav"
    
    # Skip if test file doesn't exist yet
    if not audio_path.exists():
        pytest.skip("Test audio file not found. Please add short_audio.wav to test fixtures.")
    
    response = client.transcribe_file(audio_path)
    
    # Just verify we got a response
    assert response is not None
    # Convert to dict to check basic structure
    response_dict = response.to_dict()
    assert isinstance(response_dict, dict) 