import os
import subprocess
import logging
import shutil
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Sample contents for demonstration
SAMPLE_CONTENT = """#!/bin/bash
# Cardano node startup script
export CARDANO_NODE_SOCKET_PATH="/node/socket/node.socket"
export NODE_HOME="/node"
export PATH="${NODE_HOME}/bin:${PATH}"

# Start cardano-node with mainnet configuration
cardano-node run \
  --topology ${NODE_HOME}/config/mainnet-topology.json \
  --database-path ${NODE_HOME}/db \
  --socket-path ${CARDANO_NODE_SOCKET_PATH} \
  --host-addr 0.0.0.0 \
  --port 3001 \
  --config ${NODE_HOME}/config/mainnet-config.json
"""

# Sample tip query result for demonstration
SAMPLE_TIP_CONTENT = """{
  "epoch": 215,
  "hash": "6b3e5232dc21e05f856ac0e5bcc4412f19f2e5eb9b1a96e97c8c978e5350ded7",
  "slot": 4310469,
  "block": 4638927,
  "era": "Babbage",
  "syncProgress": "100.00"
}"""

def is_docker_available():
    """
    Check if Docker is available on the system
    """
    return shutil.which('docker') is not None

def execute_docker_command(command_type="file", use_simulation=False):
    """
    Execute Docker commands to get information from the Cardano node
    command_type: "file" to get the cardano.start file or "tip" to get node tip info
    use_simulation: If True, return sample content instead of running the command
    """
    if use_simulation:
        logger.info(f"Using simulation mode - returning sample {command_type} content")
        if command_type == "tip":
            return {"success": True, "content": SAMPLE_TIP_CONTENT, "error": None, "simulation": True}
        else:  # default to file
            return {"success": True, "content": SAMPLE_CONTENT, "error": None, "simulation": True}
    
    if not is_docker_available():
        error_message = "Docker is not installed or not available in the system PATH"
        logger.error(error_message)
        return {"success": False, "content": None, "error": error_message, "simulation": False}
    
    try:
        logger.debug(f"Executing Docker command for {command_type}")
        
        if command_type == "tip":
            # Execute the tip query command
            cmd = ["docker", "exec", "cardano-node-1", "cardano-cli", "query", "tip", "--testnet-magic", "42"]
        else:
            # Default to getting the file content
            cmd = ["docker", "exec", "cardano-node-1", "cat", "/shared/cardano.start"]
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.debug(f"Command executed successfully: {result.stdout[:100]}...")
        return {"success": True, "content": result.stdout, "error": None, "simulation": False}
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}: {e.stderr}"
        logger.error(error_message)
        return {"success": False, "content": None, "error": error_message, "simulation": False}
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error(error_message)
        return {"success": False, "content": None, "error": error_message, "simulation": False}

@app.route('/')
def index():
    """
    Render the main page of the application
    """
    logger.info(f"Access attempt at {datetime.now().isoformat()}")
    docker_available = is_docker_available()
    return render_template('index.html', docker_available=docker_available)

@app.route('/get-file-content')
def get_file_content():
    """
    API endpoint to get the file content
    """
    logger.info(f"File content requested at {datetime.now().isoformat()}")
    
    # Check if simulation mode was requested
    use_simulation = request.args.get('simulation', 'false').lower() == 'true'
    
    # Execute command with simulation parameter
    result = execute_docker_command(command_type="file", use_simulation=use_simulation)
    
    if result["success"]:
        return jsonify({
            "success": True,
            "content": result["content"],
            "timestamp": datetime.now().isoformat(),
            "simulation": result.get("simulation", False)
        })
    else:
        return jsonify({
            "success": False,
            "error": result["error"],
            "timestamp": datetime.now().isoformat(),
            "simulation": result.get("simulation", False)
        }), 500

@app.route('/get-node-tip')
def get_node_tip():
    """
    API endpoint to get the Cardano node tip information
    """
    logger.info(f"Node tip info requested at {datetime.now().isoformat()}")
    
    # Check if simulation mode was requested
    use_simulation = request.args.get('simulation', 'false').lower() == 'true'
    
    # Execute command with simulation parameter
    result = execute_docker_command(command_type="tip", use_simulation=use_simulation)
    
    if result["success"]:
        return jsonify({
            "success": True,
            "content": result["content"],
            "timestamp": datetime.now().isoformat(),
            "simulation": result.get("simulation", False)
        })
    else:
        return jsonify({
            "success": False,
            "error": result["error"],
            "timestamp": datetime.now().isoformat(),
            "simulation": result.get("simulation", False)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
