from fastapi.staticfiles import StaticFiles
from start_simulation import get_random_scenario
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from record_audio import save_audio_file, transcribe_audio
from start_simulation import get_random_scenario
from reset_simulation import reset_conversation_log

app = FastAPI()

# Mount the frontend directory to serve static files
app.mount("/frontend", StaticFiles(directory=r"C:\Users\shrit\Desktop\Ml_Projects\911_Dispatch\911-dispatch\rescueSim\frontend"), name="frontend")
conversation_log = {"victim_responses": [], "dispatcher_responses": []}

def format_conversation_log(conversation_log):
    """Formats the conversation log in an alternating sequence of victim and dispatcher responses."""
    victim_responses = conversation_log["victim_responses"]
    dispatcher_responses = conversation_log["dispatcher_responses"]

    formatted_log = []
    for i in range(max(len(victim_responses), len(dispatcher_responses))):
        if i < len(victim_responses):
            formatted_log.append(f"Victim: {victim_responses[i]}")
        if i < len(dispatcher_responses):
            formatted_log.append(f"Dispatcher: {dispatcher_responses[i]}")

    return "\n".join(formatted_log)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI server!"}

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

@app.post("/record-audio")
async def record_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        audio_path = await save_audio_file(file)

        # Transcribe the audio
        transcription = transcribe_audio(audio_path)

        # Add transcription to the conversation log
        conversation_log["dispatcher_responses"].append(transcription)

        # Format the conversation log for readability
        formatted_log = format_conversation_log(conversation_log)
        print("Formatted Conversation Log:")
        print(formatted_log)

        # Return transcription to the frontend
        return {"transcription": transcription}
    except Exception as e:
        print(f"Error processing file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)