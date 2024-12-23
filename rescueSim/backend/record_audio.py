import os
import aiofiles
from google.cloud import speech

# Path for temporarily storing audio files
TEMP_AUDIO_PATH = r"C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\911-dispatch\rescueSim\backend\temp\recording.webm"

# Explicitly set credentials using the GOOGLE_CLOUD_STT environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CLOUD_STT")

# Google Cloud STT Client Initialization
client = speech.SpeechClient()

async def save_audio_file(file):
    """Save the uploaded audio file temporarily."""
    try:
        async with aiofiles.open(TEMP_AUDIO_PATH, "wb") as out_file:
            while content := await file.read(1024):  # Read the file in chunks
                await out_file.write(content)
        print(f"Audio file saved to: {TEMP_AUDIO_PATH}")
        return TEMP_AUDIO_PATH
    except Exception as e:
        print(f"Error saving file: {e}")
        raise

def transcribe_audio(audio_path):
    """Transcribe the audio file using Google Cloud STT."""
    try:
        with open(audio_path, "rb") as audio_file:
            audio_content = audio_file.read()
        print(f"Audio file size: {len(audio_content)} bytes")
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,  # Set to WebM (Opus)
            sample_rate_hertz=48000,  # Ensure this matches the recording settings
            language_code="en-US",
        )

        response = client.recognize(config=config, audio=audio)
        print(f"STT Response: {response}")
        transcription = " ".join(result.alternatives[0].transcript for result in response.results)
        print(f"Transcription: {transcription}")
        return transcription
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise