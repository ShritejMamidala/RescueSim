import random
import json

# Path to the scenarios JSON file
SCENARIOS_FILE_PATH = r"C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\911-dispatch\rescueSim\backend\data\scenarios.json"

def get_random_scenario():
    # Load scenarios from the JSON file
    with open(SCENARIOS_FILE_PATH, "r") as file:
        scenarios = json.load(file)
    
    # Select a random scenario
    scenario = random.choice(scenarios)
    
    return scenario["prompt"]