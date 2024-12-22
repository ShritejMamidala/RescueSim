import google.cloud.speech as speech
import openai
import json
import os
from google.oauth2 import service_account

# Function to transcribe audio and generate a conversation log
def transcribe_audio(file_path, language="en-US"):
    # Initialize the client using the environment variable for the service account key
    credentials_path = os.getenv("GOOGLE_CLOUD_STT")
    if not credentials_path:
        raise EnvironmentError("The environment variable 'GOOGLE_CLOUD_STT' is not set.")

    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = speech.SpeechClient(credentials=credentials)

    with open(file_path, "rb") as audio_file:
        audio = speech.RecognitionAudio(content=audio_file.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code=language,
        diarization_config=speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=2,
            max_speaker_count=2
        )
    )

    response = client.recognize(config=config, audio=audio)

    conversation_log = {"caller": [], "dispatcher": []}
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            speaker_tag = word_info.speaker_tag
            if speaker_tag == 1:
                conversation_log["dispatcher"].append(word)
            elif speaker_tag == 2:
                conversation_log["caller"].append(word)

    # Consolidate words into coherent sentences
    conversation_log["dispatcher"] = [" ".join(conversation_log["dispatcher"])]
    conversation_log["caller"] = [" ".join(conversation_log["caller"])]

    return conversation_log

# Function to generate feedback using GPT
def get_feedback(conversation_log):
    openai.api_key = os.getenv("OPENAI_API_KEY")  # Use environment variable for OpenAI API key

    # Format the conversation log for GPT input
    formatted_log = "\n".join(
        [f"Dispatcher: {turn}" for turn in conversation_log["dispatcher"]] +
        [f"Caller: {turn}" for turn in conversation_log["caller"]]
    )

    # Send the formatted log to GPT
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert evaluating 911 dispatcher performance. Be incredibly harsh and critical."},
            {"role": "user", "content": f"Analyze this conversation:\n{formatted_log}"}
        ],
        max_tokens=500
    )

    return response["choices"][0]["message"]["content"]

# Main workflow
def main():
    mp3_file_path = r"C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\Record (online-voice-recorder.com) (1).mp3"  # Replace with the path to your MP3 file

    print("Transcribing audio...")
    conversation_log = transcribe_audio(mp3_file_path)

    print("Generating feedback...")
    feedback = get_feedback(conversation_log)

    print("\nConversation Log:")
    print(json.dumps(conversation_log, indent=4))

    print("\nFeedback:")
    print(feedback)

if __name__ == "__main__":
    main()
