import API from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
    const endSimulationButton = document.getElementById("end-simulation-button");
    const startSimulationButton = document.getElementById("start-simulation");
    const simulationOptions = document.getElementById("simulation-options");
    const textToTextButton = document.getElementById("text-to-text");
    const speechToSpeechButton = document.getElementById("speech-to-speech");
    const mainTextbox = document.getElementById("main-textbox");
    const userInput = document.getElementById("user-input");
    const recordAudioButton = document.getElementById("record-audio");
    const listenToCallerButton = document.getElementById("listen-to-caller");

    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false; // Tracks recording state

    // End Simulation Button
    if (endSimulationButton) {
        endSimulationButton.addEventListener("click", async () => {
            try {
                await API.resetSimulation(); // Call API to reset simulation
                window.location.href = "index.html"; // Redirect to the main page
            } catch (error) {
                console.error("Failed to reset simulation:", error);
            }
        });
    }

    // Simulation Start Buttons
    if (startSimulationButton && simulationOptions) {
        startSimulationButton.addEventListener("click", () => {
            simulationOptions.classList.toggle("hidden");
        });
    }

    // Navigate and Start Simulation
    async function startSimulationAndNavigate(mode) {
        try {
            const prompt = await API.startSimulation(); // Fetch scenario prompt from API
            localStorage.setItem("simulationPrompt", prompt); // Save prompt in localStorage
            if (mode === "text") {
                window.location.href = "text-to-text.html";
            } else if (mode === "speech") {
                window.location.href = "speech-to-speech.html";
            }
        } catch (error) {
            console.error("Error starting simulation:", error);
        }
    }

    if (textToTextButton) {
        textToTextButton.addEventListener("click", () => startSimulationAndNavigate("text"));
    }

    if (speechToSpeechButton) {
        speechToSpeechButton.addEventListener("click", () => startSimulationAndNavigate("speech"));
    }

    // Populate Main Textbox
    function populateMainTextbox() {
        const prompt = localStorage.getItem("simulationPrompt");
        if (mainTextbox && prompt) {
            if (mainTextbox.tagName === "TEXTAREA") {
                mainTextbox.value = prompt; // For Speech-to-Speech Mode
            } else {
                mainTextbox.textContent = prompt; // For Text-to-Text Mode
            }
        }
    }

    // Start Recording Function
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mimeType = MediaRecorder.isTypeSupported("audio/webm")
                ? "audio/webm"
                : ""; // Fallback to default

            mediaRecorder = new MediaRecorder(stream, { mimeType });

            audioChunks = []; // Reset audio chunks

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                console.log("Recorded Blob Type:", audioBlob.type); // Should log "audio/webm"
                try {
                    const transcription = await API.uploadAudio(audioBlob); // Upload audio as WebM
                    displayTranscription(transcription); // Display transcription in the textbox
                } catch (error) {
                    console.error("Error uploading audio:", error);
                }

                // Toggle buttons after recording ends
                recordAudioButton.classList.add("hidden");
                listenToCallerButton.classList.remove("hidden");
            };

            mediaRecorder.start();
            console.log("Recording started...");
        } catch (error) {
            console.error("Error starting recording:", error);
        }
    }

    // Stop Recording Function
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
            console.log("Recording stopped...");
        }
    }

    // Display Transcription on UI
    function displayTranscription(transcription) {
        if (mainTextbox) {
            // Add a newline only if there is already content in the textbox
            const separator = mainTextbox.value.trim() !== "" ? "\n\n" : "";
            mainTextbox.value += `${separator}Dispatcher: ${transcription}`;
            mainTextbox.scrollTop = mainTextbox.scrollHeight; // Scroll to the latest entry
        }
        console.log("Transcription added to main textbox:", transcription);
    }

    // Record Audio Button Logic
    if (recordAudioButton) {
        recordAudioButton.addEventListener("click", () => {
            if (!isRecording) {
                startRecording();
                recordAudioButton.textContent = "Stop Recording";
            } else {
                stopRecording();
                recordAudioButton.textContent = "Record Audio";
            }
            isRecording = !isRecording;
        });
    }

    // Speech-to-Speech Button Logic: Listen to Caller
    if (listenToCallerButton) {
        listenToCallerButton.addEventListener("click", async () => {
            // Hide "Listen to Caller" and show "Record Audio"
            listenToCallerButton.classList.add("hidden");
            recordAudioButton.classList.remove("hidden");

            try {
                // Fetch GPT response and audio from the backend
                const { text, audio_url } = await API.listenToCaller();

                // Append the GPT response to the main textbox
                if (mainTextbox) {
                    mainTextbox.value += `\n\nVictim: ${text}`; // Add victim response with spacing
                    mainTextbox.scrollTop = mainTextbox.scrollHeight; // Auto-scroll to latest entry
                }

                // Play the audio file
                const audio = new Audio(audio_url);
                audio.play();
            } catch (error) {
                console.error("Error handling 'Listen to Caller':", error);
                alert("Failed to retrieve the victim's response. Please try again.");

                // Revert button visibility on error
                listenToCallerButton.classList.remove("hidden");
                recordAudioButton.classList.add("hidden");
            }
        });
    }

    // Populate the textbox with the simulation prompt
    if (mainTextbox) {
        populateMainTextbox();
    }
});
