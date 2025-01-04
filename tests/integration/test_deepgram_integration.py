"""Integration tests for Deepgram client."""

import pytest
from pathlib import Path
from src.clients.deepgram_client import AsyncDeepgramClient

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "deepgram"

@pytest.mark.asyncio
async def test_transcribe_url():
    """Test transcription of a sample audio URL."""
    client = AsyncDeepgramClient()
    
    # Using Deepgram's sample audio file
    url = "https://dpgr.am/bueller.wav"
    
    response = await client.transcribe_url(url)
    
    assert response is not None
    assert isinstance(response, dict)
    assert "results" in response

@pytest.mark.asyncio
async def test_transcribe_local_file():
    """Test transcription of a local audio file."""
    client = AsyncDeepgramClient()

    # Using local test audio file
    audio_path = FIXTURES_DIR / "short_audio.wav"
    
    # Skip if test file doesn't exist yet
    if not audio_path.exists():
        pytest.skip("Test audio file not found. Please add short_audio.wav to test fixtures.")
    
    response = await client.transcribe_file(audio_path)
    
    assert response is not None
    assert isinstance(response, dict)
    assert "results" in response 