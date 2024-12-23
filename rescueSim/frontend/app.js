// JavaScript for Interactivity

// Selection Screen
const startSimulationButton = document.getElementById("start-simulation");
const simulationOptions = document.getElementById("simulation-options");
const textToTextButton = document.getElementById("text-to-text");
const speechToSpeechButton = document.getElementById("speech-to-speech");

// Handle Start Simulation Button
startSimulationButton.addEventListener("click", () => {
    // Toggle visibility of Text-to-Text and Speech-to-Speech buttons
    if (simulationOptions.classList.contains("hidden")) {
        simulationOptions.classList.remove("hidden");
    } else {
        simulationOptions.classList.add("hidden");
    }
});

// Handle Text-to-Text Navigation
textToTextButton.addEventListener("click", () => {
    window.location.href = "text-to-text.html"; // Navigate to Text-to-Text page
});

// Handle Speech-to-Speech Navigation
speechToSpeechButton.addEventListener("click", () => {
    window.location.href = "speech-to-speech.html"; // Navigate to Speech-to-Speech page
});

document.getElementById("end-simulation-button").addEventListener("click", () => {
    window.location.href = "index.html"; // Redirect to the first page
});

