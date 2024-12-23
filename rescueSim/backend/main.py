from fastapi.staticfiles import StaticFiles
import os
from start_simulation import get_random_scenario
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from record_audio import save_audio_file, transcribe_audio
from start_simulation import get_random_scenario
from reset_simulation import reset_conversation_log
from listen_to_caller import process_listen_to_caller
import shutil
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from text_to_text import get_victim_response
from pydantic import BaseModel

class DispatcherRequest(BaseModel):
    dispatcher_message: str

app = FastAPI()

# Mount the frontend directory to serve static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")  # Adjust the path relative to the script

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

conversation_log = {"victim_responses": [], "dispatcher_responses": []}

def format_conversation_log(conversation_log):
    try:
        victim_responses = conversation_log["victim_responses"]
        dispatcher_responses = conversation_log["dispatcher_responses"]

        formatted_log = []
        for i in range(max(len(victim_responses), len(dispatcher_responses))):
            if i < len(victim_responses):
                formatted_log.append(f"Victim: {victim_responses[i]}")
            if i < len(dispatcher_responses):
                formatted_log.append(f"Dispatcher: {dispatcher_responses[i]}")
        log = "\n".join(formatted_log)
        print(f"Formatted Log:\n{log}")  # Debug log formatting
        return log
    except Exception as e:
        print(f"Error in formatting conversation log: {e}")
        raise

def clear_temp_folder(folder_path: str):
    """
    Clears all files and subfolders within the specified folder.
    """
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")


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
    temp_folder_path = "./temp2"  # Adjust the path as needed
    clear_temp_folder(temp_folder_path)

    return {"status": "success", "message": "Simulation reset and temp folder cleared."}

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

@app.post("/listen-to-caller")
async def listen_to_caller():
    """
    Endpoint to handle the 'Listen to Caller' request.
    """
    try:
        # Process the conversation log and get the GPT response and audio file
        gpt_response, audio_path = process_listen_to_caller(conversation_log, format_conversation_log)

        # Update the conversation log with the victim's response
        conversation_log["victim_responses"].append(gpt_response)

        # Return the GPT response text and audio URL to the frontend
        return {"text": gpt_response, "audio_url": f"/audio/{os.path.basename(audio_path)}"}
    except Exception as e:
        print(f"Error in listen-to-caller: {e}")
        return JSONResponse(content={"error": "Failed to process Listen to Caller request."}, status_code=500)

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve the audio file generated by Google Cloud TTS.
    """
    audio_path = f"./temp2/{filename}"
    if not os.path.exists(audio_path):
        return JSONResponse(content={"error": "Audio file not found."}, status_code=404)
    return FileResponse(audio_path)




@app.post("/text-to-text")
async def text_to_text_endpoint(request: DispatcherRequest):
    """
    API endpoint for Text-to-Text mode.
    """
    try:
        dispatcher_message = request.dispatcher_message
        print(f"Received dispatcher_message: {dispatcher_message}")  # Debug log

        # Add dispatcher message to conversation log
        conversation_log["dispatcher_responses"].append(dispatcher_message)
        print(f"Updated dispatcher_responses: {conversation_log['dispatcher_responses']}")  # Debug log

        # Format the conversation log
        formatted_log = format_conversation_log(conversation_log)
        print(f"Formatted conversation log: {formatted_log}")  # Debug log

        # Get GPT response
        victim_response = get_victim_response(formatted_log)
        print(f"GPT response: {victim_response}")  # Debug log

        # Update victim responses
        conversation_log["victim_responses"].append(victim_response)
        print(f"Updated victim_responses: {conversation_log['victim_responses']}")  # Debug log

        return JSONResponse(content={"victim_response": victim_response}, status_code=200)
    except Exception as e:
        print(f"Error in text-to-text endpoint: {e}")  # Detailed error log
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")