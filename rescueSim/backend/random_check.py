import os

# Check if the environment variables are set
openai_api_key = os.getenv("OPENAI_API_KEY")
google_cred_path = os.getenv("GOOGLE_CLOUD_TTS")

# Check OPENAI_API_KEY
if openai_api_key:
    print("OPENAI_API_KEY is set.")
else:
    print("Warning: OPENAI_API_KEY is not set.")

# Check GOOGLE_CLOUD_TTS
if google_cred_path:
    print("GOOGLE_CLOUD_TTS is set.")
else:
    print("Warning: GOOGLE_CLOUD_TTS is not set.")
