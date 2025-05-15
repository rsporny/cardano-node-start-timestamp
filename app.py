import os
import subprocess
import logging
import shutil
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Create database models
class CommandLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command_type = db.Column(db.String(50), nullable=False)  # 'file' or 'tip'
    content = db.Column(db.Text)
    error = db.Column(db.Text)
    success = db.Column(db.Boolean, default=False)
    simulation = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CommandLog {self.command_type} {self.timestamp}>"
        
    def to_dict(self):
        return {
            "id": self.id,
            "command_type": self.command_type,
            "content": self.content,
            "error": self.error,
            "success": self.success,
            "simulation": self.simulation,
            "timestamp": self.timestamp.isoformat()
        }

# Create all tables
with app.app_context():
    db.create_all()

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
    # Prepare log entry
    log_entry = CommandLog()
    log_entry.command_type = command_type
    log_entry.simulation = use_simulation
    
    if use_simulation:
        logger.info(f"Using simulation mode - returning sample {command_type} content")
        if command_type == "tip":
            log_entry.content = SAMPLE_TIP_CONTENT
            log_entry.success = True
            db.session.add(log_entry)
            db.session.commit()
            return {"success": True, "content": SAMPLE_TIP_CONTENT, "error": None, "simulation": True}
        else:  # default to file
            log_entry.content = SAMPLE_CONTENT
            log_entry.success = True
            db.session.add(log_entry)
            db.session.commit()
            return {"success": True, "content": SAMPLE_CONTENT, "error": None, "simulation": True}
    
    if not is_docker_available():
        error_message = "Docker is not installed or not available in the system PATH"
        logger.error(error_message)
        
        # Log the error
        log_entry.error = error_message
        log_entry.success = False
        db.session.add(log_entry)
        db.session.commit()
        
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
        
        # Log the successful result
        log_entry.content = result.stdout
        log_entry.success = True
        db.session.add(log_entry)
        db.session.commit()
        
        return {"success": True, "content": result.stdout, "error": None, "simulation": False}
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}: {e.stderr}"
        logger.error(error_message)
        
        # Log the error
        log_entry.error = error_message
        log_entry.success = False
        db.session.add(log_entry)
        db.session.commit()
        
        return {"success": False, "content": None, "error": error_message, "simulation": False}
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error(error_message)
        
        # Log the error
        log_entry.error = error_message
        log_entry.success = False
        db.session.add(log_entry)
        db.session.commit()
        
        return {"success": False, "content": None, "error": error_message, "simulation": False}

@app.route('/')
def index():
    """
    Render the main page of the application
    """
    logger.info(f"Access attempt at {datetime.now().isoformat()}")
    docker_available = is_docker_available()
    return render_template('index.html', docker_available=docker_available)

@app.route('/history')
def history():
    """
    Render the command history page
    """
    logger.info(f"History page access at {datetime.now().isoformat()}")
    return render_template('history.html')

@app.route('/api/history')
def get_history():
    """
    API endpoint to get command history
    """
    logger.info(f"Command history requested at {datetime.now().isoformat()}")
    try:
        # Get all logs, ordered by timestamp (newest first)
        logs = CommandLog.query.order_by(CommandLog.timestamp.desc()).all()
        
        # Convert logs to dictionary format
        log_list = [log.to_dict() for log in logs]
        
        return jsonify({
            "success": True,
            "logs": log_list
        })
    except Exception as e:
        logger.error(f"Error retrieving command history: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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
