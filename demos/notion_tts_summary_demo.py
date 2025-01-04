import asyncio
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from src.clients.notion_client_wrapper import NotionClient
from src.clients.deepgram_client import AsyncDeepgramClient
from src.clients.openai_client import OpenAIClient

load_dotenv()

NOTION_ROOT_PAGE_ID = os.getenv("NOTION_ROOT_PAGE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not NOTION_ROOT_PAGE_ID:
    raise ValueError("NOTION_ROOT_PAGE_ID not set")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set")

async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Deepgram."""
    print(f"\nDEBUG: Attempting to transcribe file: {audio_path}")
    print(f"DEBUG: File size: {os.path.getsize(audio_path)} bytes")
    
    client = AsyncDeepgramClient()
    
    print("DEBUG: Sending request to Deepgram...")
    response = await client.transcribe_file(
        audio_path,
        model="nova-2"  # Using nova-2 model with default options from client
    )
    
    print(f"DEBUG: Raw Deepgram response: {response}")
    
    # More detailed response parsing with logging
    results = response.get('results', {})
    print(f"DEBUG: Results section: {results}")
    
    channels = results.get('channels', [{}])
    print(f"DEBUG: Channels section: {channels}")
    
    alternatives = channels[0].get('alternatives', [{}])
    print(f"DEBUG: Alternatives section: {alternatives}")
    
    transcript = alternatives[0].get('transcript', '')
    print(f"DEBUG: Final transcript: {transcript}")
    
    if not transcript:
        print("DEBUG: WARNING - Got empty transcript!")
        print(f"DEBUG: Full response metadata: {response.get('metadata', {})}")
    
    return transcript

async def get_summary(transcript: str) -> str:
    """Get a concise summary using GPT-4."""
    client = OpenAIClient(api_key=OPENAI_API_KEY, model="gpt-4o")
    
    prompt = """Below is a transcript. Convert this transcript into a concise (not verbose) bulleted list of points.
    Example Transcript:
    "Hello, my name is John Doe. I am a software engineer at Google. I have been working at Google for 5 years. I am a father of 2 children. I love to play basketball."
    Example Summary:
    - John Doe is a software engineer at Google.
    - He has been working at Google for 5 years.
    - He is a father of 2 children.
    - He loves to play basketball.
    """
    
    system = "You output a bulleted list of key points from the provided transcript. Do not include any other text. Keep your bullets concise but include bullets for every point mentioned in the transcript."
    
    summary = ""
    async for chunk in client.stream(
        prompt=transcript,
        system=system,
        temperature=0,
        max_tokens=4096
    ):
        summary += chunk
    
    return summary

async def create_notion_summary(title: str, summary: str) -> None:
    """Create a Notion page with the summary."""
    client = NotionClient()
    
    # Create the page with content
    page = await client.create_page(
        title=title,
        children=[{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": summary}
                }]
            }
        }]
    )
    
    print(f"Created summary page with ID: {page['id']}")
    return page

async def main():
    # Audio file path
    audio_path = "tests/fixtures/deepgram/long_audio.mp3"
    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    print("Starting transcription...")
    transcript = await transcribe_audio(audio_path)
    
    if not transcript:
        print("No transcript generated - stopping here")
        return
    
    print("Generating summary...")
    summary = await get_summary(transcript)
    
    print("Creating Notion page...")
    title = f"Audio Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    await create_notion_summary(title, summary)
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main()) 