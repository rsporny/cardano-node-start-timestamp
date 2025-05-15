document.addEventListener('DOMContentLoaded', function() {
    // File Content Elements
    const fileContentElement = document.getElementById('fileContent');
    const refreshButton = document.getElementById('refreshButton');
    const simulationButton = document.getElementById('simulationButton');
    const fileSimulationBadge = document.getElementById('fileSimulationBadge');
    const fileStatusContainer = document.getElementById('fileStatusContainer');
    const fileLastRefreshedElement = document.getElementById('fileLastRefreshed');
    
    // Node Tip Elements
    const tipContentElement = document.getElementById('tipContent');
    const refreshTipButton = document.getElementById('refreshTipButton');
    const tipSimulationBadge = document.getElementById('tipSimulationBadge');
    const tipStatusContainer = document.getElementById('tipStatusContainer');
    const tipLastRefreshedElement = document.getElementById('tipLastRefreshed');
    
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
        fileStatusContainer.className = 'alert alert-info mb-3';
        fileStatusContainer.textContent = 'Fetching file content...';
        
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
                    fileSimulationBadge.classList.remove('d-none');
                    simulationMode = true;
                } else {
                    fileSimulationBadge.classList.add('d-none');
                }
                
                if (data.success) {
                    // Update content display
                    fileContentElement.textContent = data.content || '(File is empty)';
                    
                    // Update status with simulation notice if needed
                    fileStatusContainer.className = 'alert alert-success mb-3';
                    if (data.simulation) {
                        fileStatusContainer.innerHTML = '<strong>Simulation mode:</strong> Displaying sample content.';
                    } else {
                        fileStatusContainer.textContent = 'File content loaded successfully.';
                    }
                    
                    // Update timestamp
                    fileLastRefreshedElement.textContent = 'Last refreshed: ' + formatTimestamp(data.timestamp);
                } else {
                    // Handle error
                    fileContentElement.textContent = 'Error fetching file content.';
                    
                    // Update status with error
                    fileStatusContainer.className = 'alert alert-danger mb-3';
                    fileStatusContainer.textContent = 'Error: ' + data.error;
                    
                    // Update timestamp
                    fileLastRefreshedElement.textContent = 'Last attempt: ' + formatTimestamp(data.timestamp);
                    
                    // If Docker is not available, suggest simulation mode
                    if (data.error.includes('Docker is not installed') && !simulationMode) {
                        fileStatusContainer.innerHTML += '<br><br>Try using the Simulation Mode button to view sample content.';
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
                fileStatusContainer.className = 'alert alert-danger mb-3';
                fileStatusContainer.textContent = 'Network error: Could not connect to server. Check console for details.';
            });
    }
    
    // Function to fetch node tip information
    function fetchNodeTip() {
        // Show loading state
        tipContentElement.textContent = 'Loading...';
        tipStatusContainer.className = 'alert alert-info mb-3';
        tipStatusContainer.textContent = 'Fetching node tip information...';
        
        // Disable button during fetch
        refreshTipButton.disabled = true;
        refreshTipButton.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Loading...';
        
        // Build URL with simulation parameter if needed
        const url = simulationMode ? '/get-node-tip?simulation=true' : '/get-node-tip';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // Re-enable button
                refreshTipButton.disabled = false;
                refreshTipButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                
                // Update simulation badge
                if (data.simulation) {
                    tipSimulationBadge.classList.remove('d-none');
                } else {
                    tipSimulationBadge.classList.add('d-none');
                }
                
                if (data.success) {
                    // Try to format JSON if it's valid
                    try {
                        const jsonData = JSON.parse(data.content);
                        tipContentElement.textContent = JSON.stringify(jsonData, null, 2);
                    } catch (e) {
                        // If not valid JSON, just display as text
                        tipContentElement.textContent = data.content || '(Empty response)';
                    }
                    
                    // Update status with simulation notice if needed
                    tipStatusContainer.className = 'alert alert-success mb-3';
                    if (data.simulation) {
                        tipStatusContainer.innerHTML = '<strong>Simulation mode:</strong> Displaying sample node tip data.';
                    } else {
                        tipStatusContainer.textContent = 'Node tip information loaded successfully.';
                    }
                    
                    // Update timestamp
                    tipLastRefreshedElement.textContent = 'Last refreshed: ' + formatTimestamp(data.timestamp);
                } else {
                    // Handle error
                    tipContentElement.textContent = 'Error fetching node tip information.';
                    
                    // Update status with error
                    tipStatusContainer.className = 'alert alert-danger mb-3';
                    tipStatusContainer.textContent = 'Error: ' + data.error;
                    
                    // Update timestamp
                    tipLastRefreshedElement.textContent = 'Last attempt: ' + formatTimestamp(data.timestamp);
                    
                    // If Docker is not available, mention simulation mode
                    if (data.error.includes('Docker is not installed') && !simulationMode) {
                        tipStatusContainer.innerHTML += '<br><br>Try using the Simulation Mode button to view sample content.';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Re-enable button
                refreshTipButton.disabled = false;
                refreshTipButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                
                // Update content display
                tipContentElement.textContent = 'Error connecting to server.';
                
                // Update status
                tipStatusContainer.className = 'alert alert-danger mb-3';
                tipStatusContainer.textContent = 'Network error: Could not connect to server. Check console for details.';
            });
    }
    
    // Toggle simulation mode
    function enableSimulationMode() {
        simulationMode = true;
        fetchFileContent();
        fetchNodeTip();
    }
    
    // Fetch content on page load
    fetchFileContent();
    fetchNodeTip();
    
    // Add event listeners for buttons
    refreshButton.addEventListener('click', fetchFileContent);
    refreshTipButton.addEventListener('click', fetchNodeTip);
    
    // Add event listener for simulation button
    if (simulationButton) {
        simulationButton.addEventListener('click', enableSimulationMode);
    }
    
    // Auto-enable simulation mode if Docker is not available
    if (typeof dockerAvailable !== 'undefined' && !dockerAvailable) {
        console.info('Docker is not available. Simulation mode is recommended.');
    }
});
