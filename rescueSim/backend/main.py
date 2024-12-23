from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from start_simulation import get_random_scenario
from reset_simulation import reset_conversation_log


app = FastAPI()

# Mount the frontend directory to serve static files
app.mount("/frontend", StaticFiles(directory=r"C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\911-dispatch\rescueSim\frontend"), name="frontend")
conversation_log = {"victim_responses": [], "dispatcher_responses": []}

@app.post("/start-simulation")
async def start_simulation():
    # Fetch a random scenario using start_simulation.py
    prompt = get_random_scenario()
    
    # Update the global conversation log
    conversation_log["victim_responses"].append(prompt)
    
    # Return the selected prompt with proper encoding
    return JSONResponse(content={"prompt": prompt}, media_type="application/json; charset=utf-8")

@app.post("/reset-simulation")
async def reset_simulation():
    global conversation_log
    # Reset the global conversation log
    conversation_log = reset_conversation_log(conversation_log)
    return {"status": "success", "message": "Conversation log cleared."}

