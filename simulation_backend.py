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

import openai
import os
import json
import random
from google.cloud import texttospeech

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
        audio_encoding=texttospeech.AudioEncoding.MP3
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

# Example Usage
if __name__ == "__main__":
    conversation_log, audio_file_path = on_button_click()
    print("Conversation Log:")
    print(conversation_log)
    print(f"Generated audio file at: {audio_file_path}")
