import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_victim_response(formatted_log: str) -> str:
    """
    Sends the formatted conversation log to GPT and retrieves the victim's response.
    """
    try:
        # Call GPT to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a victim in a 911 emergency scenario. "
                        "Answer only as the victim. Do not include 'Victim:' in your response. "
                        "Do not provide any information the dispatcher has not asked for. "
                        "Keep responses short and concise. Escalate the situation very slowly. "
                        "If the dispatcher hasn't asked anything, remain silent."
                    ),
                },
                {"role": "user", "content": formatted_log},
            ],
        )
        # Extract the GPT response content
        victim_response = response["choices"][0]["message"]["content"].strip()
        return victim_response

    except Exception as e:
        print(f"Error generating GPT response: {e}")
        raise RuntimeError("Failed to generate victim response from GPT.")

