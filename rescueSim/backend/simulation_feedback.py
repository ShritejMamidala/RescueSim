import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure the API key is set

def analyze_performance(conversation_log):
    """
    Send the conversation log to GPT and return the feedback.
    """
    try:
        prompt = (
            "You are an expert evaluator for 911 dispatcher training. "
            "Rate the dispatcher's performance on a scale of 1-10 based on the following conversation log. "
            "Provide a one-sentence review and detailed constructive feedback. Use a professional and harsh tone.\n\n"
            "If no conversation log was provided. Say that"
            "This is an audio conversation translated into text so you can see it"
            f"Conversation Log:\n{conversation_log}\n\n"
            "Respond in the following JSON format:\n"
            "{ \"rating\": <int>, \"review\": \"<one-sentence review>\", \"feedback\": \"<detailed feedback>\" }"
        )
        
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 or a similar model
            messages=[
                {"role": "system", "content": "You are an expert evaluator."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse GPT's response
        feedback = response["choices"][0]["message"]["content"].strip()
        return feedback
    except Exception as e:
        print(f"Error in analyze_performance: {e}")
        return {"error": "Failed to analyze performance"}