// API Utility Functions

const API = {
    /**
     * Start the simulation by calling the backend API.
     * @returns {Promise<string>} - The simulation prompt returned by the backend.
     */
    async startSimulation() {
        try {
            const response = await fetch("/start-simulation", { method: "POST" });
            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }
            const data = await response.json();
            return data.prompt;
        } catch (error) {
            console.error("Error in startSimulation API call:", error);
            throw error;
        }
    }
};

export default API;
