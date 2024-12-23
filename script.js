// JavaScript for Interactivity

// Selection Screen
const toggleButtons = document.querySelectorAll('.toggle-button');
const startButton = document.querySelector('.start-button');
const selectionScreen = document.querySelector('.selection-screen');

// Main Chat Window
const mainChatWindow = document.getElementById('main-chat-window');
const modeTitle = document.getElementById('mode-title');
const recordButton = document.getElementById('record-button');
const listenToCallerButton = document.getElementById('listen-to-caller-button');
const captionsContainer = document.getElementById('captions-container');

// Audio variables
let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioURL;

// Handle Toggle Buttons
toggleButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const group = button.dataset.group;

        // Deselect other buttons in the same group
        toggleButtons.forEach((btn) => {
            if (btn.dataset.group === group) {
                btn.classList.remove('active');
            }
        });

        // Toggle the clicked button
        button.classList.toggle('active');
    });
});

// Handle Start Button
startButton.addEventListener('click', () => {
    const isSpeechToSpeech = document
        .querySelector('.speech-to-speech-button')
        .classList.contains('active');

    const isTextToText = document
        .querySelector('.text-to-text-button')
        .classList.contains('active');

    selectionScreen.style.display = 'none';
    mainChatWindow.classList.remove('hidden');

    if (isSpeechToSpeech) {
        modeTitle.textContent = 'Speech to Speech Mode';
        recordButton.classList.remove('hidden');
        listenToCallerButton.classList.remove('hidden');
        captionsContainer.classList.remove('hidden');
    } else if (isTextToText) {
        modeTitle.textContent = 'Text to Text Mode';
        recordButton.classList.add('hidden');
        listenToCallerButton.classList.add('hidden');
        captionsContainer.classList.add('hidden');
    }
});

// Record Button
recordButton.addEventListener('click', async () => {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };

        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioURL = URL.createObjectURL(audioBlob);
        };

        mediaRecorder.start();
        recordButton.textContent = 'Stop Recording';
    } else {
        mediaRecorder.stop();
        recordButton.textContent = 'Record Audio';
    }
});

// End Simulation Button
const endSimulationButton = document.querySelector('.clear-history');

endSimulationButton.addEventListener('click', () => {
    alert('Simulation ended. Thank you!');
    location.reload(); // Reloads the page to go back to the selection screen
});
