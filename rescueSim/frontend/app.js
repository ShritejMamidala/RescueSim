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

    // Function to reset the simulation
    async function resetSimulation() {
        try {
            const response = await fetch("/reset-simulation", { method: "POST" });
            const data = await response.json();
            console.log(data.message); // Optional: Log the success message
        } catch (error) {
            console.error("Error resetting simulation:", error);
        }
    }

    // End Simulation Button
    if (endSimulationButton) {
        endSimulationButton.addEventListener("click", async () => {
            await resetSimulation(); // Reset the conversation log
            window.location.href = "index.html"; // Redirect to the main page
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
            const prompt = await API.startSimulation(); // Fetch the scenario prompt from the backend
            localStorage.setItem("simulationPrompt", prompt); // Save the prompt in localStorage
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

    // Text-to-Text Input Logic
    if (userInput) {
        userInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && userInput.value.trim()) {
                const userMessage = document.createElement("div");
                userMessage.textContent = userInput.value;
                userMessage.classList.add("user-message");
                mainTextbox.appendChild(userMessage);
                userInput.value = "";
                mainTextbox.scrollTop = mainTextbox.scrollHeight;
            }
        });
    }

    // Speech-to-Speech Button Logic
    if (recordAudioButton) {
        recordAudioButton.addEventListener("click", () => {
            console.log("Audio recording started...");
        });
    }

    if (listenToCallerButton) {
        listenToCallerButton.addEventListener("click", () => {
            console.log("Listening to caller...");
        });
    }

    // Populate the textbox with the simulation prompt
    if (mainTextbox) {
        populateMainTextbox();
    }
});
