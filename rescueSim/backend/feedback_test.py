import openai
import os

# Set the OpenAI API key from the environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    print("OPENAI_API_KEY is not set.")
else:
    print("OPENAI_API_KEY is set.")

def format_conversation_log(text):
    """
    Send the raw conversation log to GPT for formatting.
    The response should be a clean, organized version of the log.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a formatting assistant. The user has provided a raw log of a conversation. "
                        "Your job is to clean, organize, and format it for clarity. "
                        "Keep the content logically structured and retain all the information."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        formatted_log = response.choices[0].message.content.strip()
        return formatted_log
    except Exception as e:
        print(f"Error formatting conversation log: {e}")
        raise RuntimeError("Failed to format conversation log")


def analyze_text_file(text):
    """
    Analyze the text file content using GPT and return both a formatted conversation log and feedback.
    """
    try:
        # First, format the conversation log
        formatted_log = format_conversation_log(text)

        # Next, get feedback about the conversation
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a feedback generator for a 911 dispatch simulation.",
                },
                {"role": "user", "content": text},
            ],
        )
        feedback = response.choices[0].message.content.strip()

        return formatted_log, feedback
    except Exception as e:
        print(f"Error analyzing text file: {e}")
        raise RuntimeError("Failed to process text file")
