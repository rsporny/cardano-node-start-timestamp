# Cardano Node File Viewer

A web-based application that displays the contents of files from a Cardano node running in Docker, and shows node tip information. The application includes historical logging of command outputs with timestamps.

## Features

- View contents of `/shared/cardano.start` file from a Cardano node Docker container
- Display Cardano node tip information from `cardano-cli query tip --testnet-magic 42`
- Simulation mode for testing without Docker
- Historical logging of all command executions with timestamps
- Filtering and viewing command history

## Requirements

- Python 3.8 or newer
- PostgreSQL database (for command history logging)
- Docker (optional - the app will work in simulation mode without it)
- A running Cardano node Docker container named `cardano-node-1` (optional)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd cardano-node-file-viewer
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r local_requirements.txt
   ```
   
   Or install them manually:
   ```
   pip install flask flask-sqlalchemy gunicorn psycopg2-binary
   ```

4. Set up the PostgreSQL database:
   - Create a PostgreSQL database
   - Set the following environment variables:
     ```
     export DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>
     ```
     On Windows:
     ```
     set DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>
     ```

## Running the Application

1. Start the application:
   ```
   python main.py
   ```
   
   Or using Gunicorn (recommended for production, Linux/Mac only):
   ```
   gunicorn --bind 0.0.0.0:8080 main:app
   ```

2. Access the application in your browser:
   ```
   http://localhost:8080
   ```

3. If you don't have Docker or a Cardano node container:
   - Click the "Simulation Mode" button to see sample data

## Using the Application

### Main Page

- **View File Content**: Displays the contents of the `/shared/cardano.start` file from the Docker container
- **Node Tip Information**: Shows the result of querying the Cardano node tip
- **Refresh Button**: Updates the displayed information
- **Simulation Mode**: Shows sample data when Docker is unavailable
- **History Button**: View the history of command executions

### History Page

- View all past command executions with timestamps
- Filter by command type (file or tip)
- Filter by status (success, error)
- Filter by simulation status

## Configuration

- The default port is 8080 (changed from 5000 to avoid conflicts)
- You can modify the port in `main.py` if needed
- The expected Docker container name is `cardano-node-1`

## Troubleshooting

- **Address already in use**: Change the port in `main.py` to an available port
- **Database connection issues**: Make sure your DATABASE_URL is correct
- **Docker not found**: Either install Docker and start a Cardano node container, or use the simulation mode

## Notes for Docker Users

If you're running a Cardano node in Docker, make sure:
1. Your container is named `cardano-node-1` (or modify the code in app.py accordingly)
2. The file exists at `/shared/cardano.start` within the container
3. The container has cardano-cli installed and configured properly