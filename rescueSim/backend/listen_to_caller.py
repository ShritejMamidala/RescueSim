import os
import openai
from google.cloud import texttospeech
import uuid

# Set up OpenAI and Google Cloud credentials
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this environment variable is set
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CLOUD_TTS")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
TEMP_AUDIO_DIR = os.path.join(BASE_DIR, "temp2")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)  # Ensure the directory exists

# Ensure the temp directory exists
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

def generate_gpt_response(formatted_log):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a victim in a 911 emergency scenario. Answer only as the victim. Do not include 'Victim:' in your response, do not provide any information the dispatcher has not asked for. keep your responses short and consise. very slowly escalate the situation. If the dispatcher hasn't asked anything, remain silent."},
            {"role": "user", "content": formatted_log}
        ]
    )
    gpt_output = response["choices"][0]["message"]["content"]
    print(f"GPT Output: {gpt_output}")  # Log the raw GPT response
    return gpt_output

def convert_text_to_audio(text):
    """
    Convert GPT's response text to audio using Google Cloud TTS.
    """
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3  # Generate MP3 for simplicity
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save the audio to a temporary file
    audio_filename = os.path.join(TEMP_AUDIO_DIR, f"{uuid.uuid4()}.mp3")
    with open(audio_filename, "wb") as out:
        out.write(response.audio_content)
    return audio_filename

def process_listen_to_caller(conversation_log, format_log_func):
    """
    Main function to handle the 'Listen to Caller' workflow.
    """
    # Format the conversation log using the provided function
    formatted_log = format_log_func(conversation_log)

    # Generate GPT response
    gpt_response = generate_gpt_response(formatted_log)

    # Convert GPT response to audio
    audio_path = convert_text_to_audio(gpt_response)

    return gpt_response, audio_path
