# Simulation Backend

"""
Workflow:

1. Button Click Initialization:
   - The simulation starts when a button is clicked. (To be handled later, likely via a JavaScript frontend.)

2. Conversation Log Creation:
   - A conversation log is initialized to track all AI prompts and dispatcher responses.

3. Simulation Setup:
   - GPT (victim) generates a text-based simulation prompt, from a predefined file containing 30+ scenarios, which is fed into the GPT API.

4. Text-to-Speech Conversion:
   - The GPT-generated prompt is sent to Google Cloud TTS to generate audio output (AI voice).

5. AI Voice Playback:
   - The generated audio (AI voice) is played back to the dispatcher.

6. Speech-to-Text Conversion:
   - The dispatcher speaks their response, which is captured and converted into text using OpenAI Whisper STT (Speech-to-Text).

7. Log the Interaction:
   - The AI’s prompt and the dispatcher’s response are logged in the conversation log.

8. Repeat the Cycle:
   - The updated conversation log is sent back to GPT to generate the next prompt.
   - The cycle repeats for up to 10 turns or until the dispatcher manually ends the simulation.

9. Feedback Generation:
   - After the simulation ends, GPT analyzes the entire conversation log and provides detailed, harsh feedback to the dispatcher based on evidence-based protocols.
"""

""

import openai
import os
import json
import random
from google.cloud import texttospeech
from google.cloud import speech
import wave

# Set the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    exit(1)

# Step 1: Button Click Initialization
# This would normally be handled by your frontend. For now, simulate the click event:
def on_button_click():
    print("Simulation started...")
    conversation_log = initialize_conversation_log()
    gpt_response = generate_initial_prompt(conversation_log)
    audio_file_path = generate_audio_from_text(gpt_response)
    conversation_log.append({"caller": gpt_response, "dispatcher": ""})
    return conversation_log, audio_file_path

# Step 2: Conversation Log Creation
def initialize_conversation_log():
    # Load predefined scenarios from simulation_examples.json
    with open("911-dispatch/simulation_examples.json", "r") as file:
        predefined_scenarios = json.load(file)

    # Pick a random scenario
    selected_scenario = random.choice(predefined_scenarios)
    initial_scenario = selected_scenario["prompt"]
    print(f"Selected Scenario: {initial_scenario}")

    # Initialize the log with the initial scenario
    return [{"caller": initial_scenario, "dispatcher": ""}]

# Step 3: Simulation Setup (Generate GPT Prompt)
def generate_initial_prompt(conversation_log):
    # Use OpenAI GPT to repeat the initial scenario
    initial_scenario = conversation_log[0]["caller"]
    prompt = (
        "You are simulating a 911 caller. The following is the initial emergency situation. Repeat it as if you are the caller:\n" +
        f"{initial_scenario}"
    )

    # GPT API call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a 911 caller in a simulated emergency training."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract GPT's response
    gpt_response = response["choices"][0]["message"]["content"]
    print(f"GPT Response: {gpt_response}")
    return gpt_response

# Step 4: Text-to-Speech Conversion
def generate_audio_from_text(text):
    # Use environment variable for the service account key file
    service_account_key_path = os.getenv("GOOGLE_CLOUD_TTS")

    if not service_account_key_path:
        print("Error: GOOGLE_CLOUD_TTS environment variable is not set.")
        exit(1)

    # Initialize the Text-to-Speech client using the service account key file
    client = texttospeech.TextToSpeechClient.from_service_account_file(service_account_key_path)
    print("Google Cloud Text-to-Speech client initialized successfully!")

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.2  # Set speaking rate to 1.2 for faster speech
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, 
        voice=voice, 
        audio_config=audio_config
    )

    # Save the audio to a file
    audio_file_path = "TTS_output.mp3"
    with open(audio_file_path, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to file {audio_file_path}")

    return audio_file_path

# Step 6: Speech-to-Text Conversion
def transcribe_audio_to_text(audio_file_path):
    print(f"Transcribing audio file: {audio_file_path}")
    service_account_key_path = os.getenv("GOOGLE_CLOUD_STT")

    if not service_account_key_path:
        print("Error: GOOGLE_CLOUD_STT environment variable is not set.")
        exit(1)

    client = speech.SpeechClient.from_service_account_file(service_account_key_path)

    # Read audio file
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=48000,  # Match the audio file's sample rate
        language_code="en-US"
)

    # Perform the speech-to-text request
    response = client.recognize(config=config, audio=audio)

    transcript = " ".join(result.alternatives[0].transcript for result in response.results)
    print(f"Transcription: {transcript}")
    return transcript


# Step 7: Log the Interaction
def log_interaction(conversation_log, dispatcher_response):
    print("Logging interaction...")
    conversation_log[-1]["dispatcher"] = dispatcher_response
    print(f"Updated Conversation Log: {conversation_log}")

# Step 8: Repeat the Cycle
def generate_next_prompt(conversation_log):
    print("Generating next prompt...")
    updated_prompt = (
        "Based on the dispatcher’s response, continue the simulation. Update the caller’s information accordingly:\n" +
        f"Conversation Log: {conversation_log}"
    )

    # GPT API call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a 911 caller in a simulated emergency training, you are the victim"},
            {"role": "user", "content": updated_prompt}
        ]
    )

    # Extract GPT's response
    next_prompt = response["choices"][0]["message"]["content"]
    print(f"Next GPT Prompt: {next_prompt}")
    return next_prompt

# Example Usage
if __name__ == "__main__":
    # Initialize the simulation
    conversation_log, _ = on_button_click()  # Start simulation with initial scenario

    # Simulate multiple turns (3 for this example)
    for turn in range(3):
        print(f"\n=== Turn {turn + 1} ===")

        # Path to the dispatcher audio file (replace with actual file for dispatcher response)
        audio_file_path = r"C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\Record (online-voice-recorder.com) (1).mp3"

        # Perform Speech-to-Text on the dispatcher's audio
        dispatcher_response = transcribe_audio_to_text(audio_file_path)

        # Check if transcription was empty
        if dispatcher_response.strip() == "":
            print("No transcription returned for the dispatcher response. Skipping this turn.")
            continue

        # Log the interaction (caller and dispatcher)
        log_interaction(conversation_log, dispatcher_response)

        # Generate the next GPT prompt based on the updated conversation log
        next_prompt = generate_next_prompt(conversation_log)

        # Append the next GPT prompt to the conversation log for the caller
        conversation_log.append({"caller": next_prompt, "dispatcher": ""})

        # Generate a new TTS file for the latest GPT prompt
        audio_file_for_turn = f"TTS_output_turn_{turn + 1}.mp3"
        audio_file_path = generate_audio_from_text(next_prompt)
        print(f"Audio generated for Turn {turn + 1}: {audio_file_for_turn}")

        # Display the full conversation log
        print("\n=== Full Conversation Log ===")
        print(json.dumps(conversation_log, indent=4))