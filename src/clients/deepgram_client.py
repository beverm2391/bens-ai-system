"""Deepgram API client facade."""

import os
import asyncio
import mimetypes
from pathlib import Path
from typing import Dict, Any, Union, Optional
from dotenv import load_dotenv
import aiofiles
import httpx
from deepgram.utils import verboselogs
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    PrerecordedOptions,
    FileSource,
)

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY not set")

class AsyncDeepgramClient:
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB in bytes
    MODEL_TIMEOUTS = {
        "whisper": 1200,  # 20 minutes
        "nova-2": 600,    # 10 minutes
        "base": 600,
        "enhanced": 600
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise Exception("DEEPGRAM_API_KEY not set")
        
        config = DeepgramClientOptions(verbose=verboselogs.SPAM)
        self.client = DeepgramClient(self.api_key, config)

    async def transcribe_file(
        self,
        file_path: Union[str, Path],
        model: str = "nova-2"
    ) -> Dict[str, Any]:
        # Validate file size
        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_FILE_SIZE:
            raise Exception(f"File size {file_size} bytes exceeds maximum of {self.MAX_FILE_SIZE} bytes (2GB)")

        # Get appropriate timeout for model
        timeout = self.MODEL_TIMEOUTS.get(model, 600)

        # Get mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'audio/mpeg' if str(file_path).endswith('.mp3') else 'audio/wav'
        
        print(f"DEBUG: Using mime type: {mime_type}")

        async with aiofiles.open(file_path, "rb") as audio_file:
            data = await audio_file.read()

        payload: FileSource = {
            "buffer": data,
            "mimetype": mime_type
        }
        
        try:
            response = await self.client.listen.asyncrest.v("1").transcribe_file(
                payload,
                options=PrerecordedOptions(
                    model=model,
                    smart_format=True,
                    diarize=True,
                    punctuate=True,
                    utterances=True
                ),
                timeout=httpx.Timeout(timeout, connect=10.0)
            )
            return response.to_dict()
        except httpx.TimeoutException as e:
            raise Exception(f"Request timed out after {timeout} seconds. RAW: {str(e)}")
        except Exception as e:
            if "429" in str(e):
                raise Exception(f"Rate limit exceeded. Check concurrent request limits for your plan. RAW: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")

    async def transcribe_url(
        self,
        url: str,
        model: str = "nova-2"
    ) -> Dict[str, Any]:
        payload = {"url": url}
        options = PrerecordedOptions(
            model=model,
            smart_format=True,
            diarize=True,
            punctuate=True,
            utterances=True
        )

        timeout = self.MODEL_TIMEOUTS.get(model, 600)

        try:
            response = await self.client.listen.asyncrest.v("1").transcribe_url(
                payload,
                options,
                timeout=httpx.Timeout(timeout, connect=10.0)
            )
            return response.to_dict()
        except httpx.TimeoutException as e:
            raise Exception(f"Request timed out after {timeout} seconds. RAW: {str(e)}")
        except Exception as e:
            if "429" in str(e):
                raise Exception(f"Rate limit exceeded. Check concurrent request limits for your plan. RAW: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
