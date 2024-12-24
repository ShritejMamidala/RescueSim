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
from feedback import process_audio_feedback
import json
from simulation_feedback import analyze_performance
from feedback_test import analyze_text_file


class DispatcherRequest(BaseModel):
    dispatcher_message: str

app = FastAPI()

# Mount the frontend directory to serve static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")  # Adjust the path relative to the script

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

TEMP_FEEDBACK_DIR  = os.path.join(BASE_DIR, "temp2")

# Ensure the directory exists
os.makedirs(TEMP_FEEDBACK_DIR , exist_ok=True)

TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp3")
os.makedirs(TEMP_FOLDER, exist_ok=True)

conversation_log = {"victim_responses": [], "dispatcher_responses": []}

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
    
@app.post("/generate-feedback")
async def generate_feedback():
    print("DEBUG: /generate-feedback endpoint hit")  # Log for debugging

    try:
        # Format the conversation log
        formatted_log = format_conversation_log(conversation_log)

        # Get feedback from the GPT model
        feedback_str = analyze_performance(formatted_log)

        # Log the raw feedback string
        print("Raw Feedback String:", feedback_str)

        # Parse the feedback string into JSON
        feedback = json.loads(feedback_str)

        # Log the parsed feedback object
        print("Parsed Feedback Object:", feedback)

        # Return the feedback along with the formatted conversation log
        return {
            "feedback": feedback,
            "conversation_log": formatted_log
        }
    except json.JSONDecodeError as e:
        print(f"Error decoding feedback JSON: {e}")
        raise HTTPException(status_code=500, detail="Invalid JSON format in feedback response")
    except Exception as e:
        print(f"Error in generate_feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate feedback")
    

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    """
    API endpoint to process an uploaded audio file.
    - Accepts: audio file (.mp3, .wav, .flac, .ogg, .m4a).
    - Returns: formatted conversation log and feedback.
    """
    # Ensure the temp_feedback directory exists
    try:
        os.makedirs(TEMP_FEEDBACK_DIR, exist_ok=True)
        print(f"Directory {TEMP_FEEDBACK_DIR} is ready.")  # Debug log
    except OSError as e:
        print(f"Error creating directory {TEMP_FEEDBACK_DIR}: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Failed to create temporary storage directory: {str(e)}")

    # Save the file to the temp_feedback folder
    temp_file_path = os.path.join(TEMP_FEEDBACK_DIR, file.filename)
    try:
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
            print(f"File saved: {temp_file_path}, size: {len(content)} bytes")  # Debug log
    except Exception as e:
        print(f"Error saving file: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Process the file and generate feedback
    try:
        conversation_log, feedback = process_audio_feedback(temp_file_path)
        print(f"Processing completed for file: {temp_file_path}")  # Debug log
    except ValueError as ve:
        print(f"Validation error for file {temp_file_path}: {ve}")  # Debug log
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error processing file {temp_file_path}: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Temporary file deleted: {temp_file_path}")  # Debug log
            except OSError as e:
                print(f"Failed to delete temporary file {temp_file_path}: {e}")  # Debug log

    # Return the formatted conversation log and feedback
    return JSONResponse(
        content={
            "conversation_log": conversation_log or "No conversation log available.",
            "feedback": feedback or "No feedback available."
        },
        status_code=200
    )

@app.post("/process-text-file")
async def process_text_file(file: UploadFile = File(...)):
    """
    API endpoint to process a text file uploaded by the user.
    It sends the file's content to GPT for both formatting and feedback generation.
    """
    try:
        # Save the uploaded file temporarily
        file_path = os.path.join(TEMP_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Decode the file content to a string
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Analyze the text file
        formatted_log, feedback = analyze_text_file(text)

        # Optionally clear the temp folder
        clear_temp_folder(TEMP_FOLDER)

        return JSONResponse(content={"conversation_log": formatted_log, "feedback": feedback})
    except Exception as e:
        print(f"Error processing text file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process text file")