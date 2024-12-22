import os
from google.cloud import speech

def transcribe_audio_to_text(audio_file_path):
    print(f"Transcribing audio file: {audio_file_path}")
    service_account_key_path = os.getenv("GOOGLE_CLOUD_STT")

    if not service_account_key_path:
        print("Error: GOOGLE_CLOUD_STT environment variable is not set.")
        return ""

    # Initialize the Speech-to-Text client
    client = speech.SpeechClient.from_service_account_file(service_account_key_path)

    try:
        # Read the audio file
        with open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {audio_file_path}.")
        return ""

    # Configure RecognitionAudio and RecognitionConfig
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=48000,  
        language_code="en-US"
)

    try:
        # Perform the transcription request
        response = client.recognize(config=config, audio=audio)
        print("\n=== Debugging: STT Raw Response ===")
        print(response)

        if not response.results:
            print("No transcription results returned. The audio might be unclear or empty.")
            return ""

        # Extract and return the transcription
        transcript = " ".join(result.alternatives[0].transcript for result in response.results)
        print(f"\n=== Transcription: {transcript} ===")
        return transcript

    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

# Main Test Block
if __name__ == "__main__":
    # Path to your audio file
    audio_file_path = r"C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\Record (online-voice-recorder.com) (1).mp3"

    # Call the transcription function
    transcription = transcribe_audio_to_text(audio_file_path)

    # Output the result
    if transcription:
        print("\n=== Transcription Output ===")
        print(transcription)

        # Save transcription to a file
        try:
            with open("transcription_output.txt", "w") as f:
                f.write(transcription)
            print("\nTranscription saved to 'transcription_output.txt'")
        except Exception as file_error:
            print(f"Error saving transcription to file: {file_error}")
    else:
        print("Transcription failed or returned no results.")
