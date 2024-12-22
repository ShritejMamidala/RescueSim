// JavaScript for Interactivity

// Clear History Button Functionality
const clearHistoryButton = document.querySelector('.clear-history');
const messageBox = document.querySelector('.message-box');

if (clearHistoryButton) {
    clearHistoryButton.addEventListener('click', () => {
        messageBox.innerHTML = ''; // Clears all messages
    });
}

// Simulated Audio Play Functionality
const playAudioLinks = document.querySelectorAll('.play-audio');

playAudioLinks.forEach(link => {
    link.addEventListener('click', () => {
        alert('Playing audio...'); // Replace with real audio playback functionality
    });
});
