document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const fileContentElement = document.getElementById('fileContent');
    const refreshButton = document.getElementById('refreshButton');
    const simulationButton = document.getElementById('simulationButton');
    const simulationBadge = document.getElementById('simulationBadge');
    const statusContainer = document.getElementById('statusContainer');
    const lastRefreshedElement = document.getElementById('lastRefreshed');
    
    // Track simulation mode state
    let simulationMode = false;
    
    // Function to format timestamp
    function formatTimestamp(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleString();
        } catch (e) {
            console.error('Error formatting timestamp:', e);
            return isoString;
        }
    }
    
    // Function to fetch file content
    function fetchFileContent() {
        // Show loading state
        fileContentElement.textContent = 'Loading...';
        statusContainer.className = 'alert alert-info mb-3';
        statusContainer.textContent = 'Fetching file content...';
        
        // Disable buttons during fetch
        refreshButton.disabled = true;
        refreshButton.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Loading...';
        if (simulationButton) {
            simulationButton.disabled = true;
        }
        
        // Build URL with simulation parameter if needed
        const url = simulationMode ? '/get-file-content?simulation=true' : '/get-file-content';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // Re-enable buttons
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                if (simulationButton) {
                    simulationButton.disabled = false;
                }
                
                // Update simulation badge
                if (data.simulation) {
                    simulationBadge.classList.remove('d-none');
                    simulationMode = true;
                } else {
                    simulationBadge.classList.add('d-none');
                }
                
                if (data.success) {
                    // Update content display
                    fileContentElement.textContent = data.content || '(File is empty)';
                    
                    // Update status with simulation notice if needed
                    statusContainer.className = 'alert alert-success mb-3';
                    if (data.simulation) {
                        statusContainer.innerHTML = '<strong>Simulation mode:</strong> Displaying sample content.';
                    } else {
                        statusContainer.textContent = 'File content loaded successfully.';
                    }
                    
                    // Update timestamp
                    lastRefreshedElement.textContent = 'Last refreshed: ' + formatTimestamp(data.timestamp);
                } else {
                    // Handle error
                    fileContentElement.textContent = 'Error fetching file content.';
                    
                    // Update status with error
                    statusContainer.className = 'alert alert-danger mb-3';
                    statusContainer.textContent = 'Error: ' + data.error;
                    
                    // Update timestamp
                    lastRefreshedElement.textContent = 'Last attempt: ' + formatTimestamp(data.timestamp);
                    
                    // If Docker is not available, suggest simulation mode
                    if (data.error.includes('Docker is not installed') && !simulationMode) {
                        statusContainer.innerHTML += '<br><br>Try using the Simulation Mode button to view sample content.';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Re-enable buttons
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                if (simulationButton) {
                    simulationButton.disabled = false;
                }
                
                // Update content display
                fileContentElement.textContent = 'Error connecting to server.';
                
                // Update status
                statusContainer.className = 'alert alert-danger mb-3';
                statusContainer.textContent = 'Network error: Could not connect to server. Check console for details.';
            });
    }
    
    // Toggle simulation mode
    function enableSimulationMode() {
        simulationMode = true;
        fetchFileContent();
    }
    
    // Fetch content on page load
    fetchFileContent();
    
    // Add event listener for refresh button
    refreshButton.addEventListener('click', fetchFileContent);
    
    // Add event listener for simulation button
    if (simulationButton) {
        simulationButton.addEventListener('click', enableSimulationMode);
    }
    
    // Auto-enable simulation mode if Docker is not available
    if (typeof dockerAvailable !== 'undefined' && !dockerAvailable) {
        console.info('Docker is not available. Simulation mode is recommended.');
    }
});
