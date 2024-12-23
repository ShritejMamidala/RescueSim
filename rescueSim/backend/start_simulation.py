import random
import json
import os 

# Path to the scenarios JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
SCENARIOS_FILE_PATH = os.path.join(BASE_DIR, "data", "scenarios.json")

def get_random_scenario():
    # Load scenarios from the JSON file
    with open(SCENARIOS_FILE_PATH, "r") as file:
        scenarios = json.load(file)
    
    # Select a random scenario
    scenario = random.choice(scenarios)
    
    return scenario["prompt"]