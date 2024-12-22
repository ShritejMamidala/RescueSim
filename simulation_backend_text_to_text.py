import openai
import random
import json
import os
# Load the scenarios from the provided JSON file
with open(r'C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\911-dispatch\simulation_examples.json', 'r') as file:
    scenarios = json.load(file)

# Function to pick a random scenario
def get_random_scenario():
    return random.choice(scenarios)

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize conversation log
conversation_log = {
    "caller": [],
    "dispatcher": []
}

# Select a random scenario
scenario = get_random_scenario()
initial_prompt = scenario["prompt"]
conversation_log["caller"].append(initial_prompt)

# Display the initial scenario to the dispatcher
print("Caller: ", initial_prompt)

# Simulation loop
for turn in range(10):
    # Dispatcher response
    dispatcher_response = input("Dispatcher: ")
    conversation_log["dispatcher"].append(dispatcher_response)

    # Add the dispatcher's response to the GPT prompt
    gpt_prompt = "\n".join([
        f"Caller: {entry}" for entry in conversation_log["caller"]
    ] + [
        f"Dispatcher: {entry}" for entry in conversation_log["dispatcher"]
    ])

    # Get GPT response
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a distressed caller providing information to a 911 dispatcher. Only respond as the caller, and limit your response to one concise sentence."},
            {"role": "user", "content": gpt_prompt}
        ],
        max_tokens=50
    )

    caller_response = gpt_response["choices"][0]["message"]["content"].strip()

    # Enforce single-line response
    caller_response = caller_response.split("\n")[0]

    # Log GPT response
    conversation_log["caller"].append(caller_response)

    # Display GPT response
    print("Caller: ", caller_response)

    # Ensure dispatcher has the opportunity to reply before the next caller response
    print("")

    # Check for end of simulation
    if turn == 9 or dispatcher_response.lower() == "end":
        print("Simulation ended.")
        break

# Output the conversation log
print("\nConversation Log:")
print(json.dumps(conversation_log, indent=4))
