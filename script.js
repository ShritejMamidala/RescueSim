// JavaScript for Interactivity

// Selection Screen
const toggleButtons = document.querySelectorAll('.toggle-button');
const startButton = document.querySelector('.start-button');
const selectionScreen = document.querySelector('.selection-screen');

// Main Container
const mainContainer = document.querySelector('.main-container');
const promptCounter = document.querySelector('.prompt-counter');

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
    selectionScreen.style.display = 'none'; // Hide selection screen
    mainContainer.classList.remove('hidden'); // Show main container
    promptCounter.classList.remove('hidden'); // Show prompt counter
});

// End Simulation Button
const endSimulationButton = document.querySelector('.clear-history');

endSimulationButton.addEventListener('click', () => {
    alert('Simulation ended. Thank you!');
    location.reload(); // Reloads the page to go back to the selection screen
});
