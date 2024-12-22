from google.cloud import texttospeech

def test_google_cloud_tts():
    # Use the new service account key file
    service_account_key_path = "C:/Users/shrit/Desktop/Ml_Projects/911_Dispatch/911-dispatch/kinetic-song-445422-d9-432bb8515a50.json"

    try:
        # Initialize the Text-to-Speech client using the service account key file
        client = texttospeech.TextToSpeechClient.from_service_account_file(service_account_key_path)
        print("Google Cloud Text-to-Speech client initialized successfully!")

        # Text input for testing
        text = "This is a test of Google Cloud Text-to-Speech."

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
        audio_file_path = "test_output.mp3"
        with open(audio_file_path, "wb") as out:
            out.write(response.audio_content)
        print("Audio content written to file: test_output.mp3")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_google_cloud_tts()