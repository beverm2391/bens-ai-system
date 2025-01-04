# main.py (python example)

import os
import logging
from deepgram.utils import verboselogs

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
)

AUDIO_URL = {
    "url": "https://dpgr.am/bueller.wav"
}

def main():
    try:
        # STEP 1 Create a Deepgram client using the DEEPGRAM_API_KEY from your environment variables
        deepgram: DeepgramClient = DeepgramClient()

        # STEP 2 Call the transcribe_url method on the rest class
        options: PrerecordedOptions = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )
        response = deepgram.listen.rest.v("1").transcribe_url(AUDIO_URL, options)
        print(f"response: {response}\n\n")

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    main()