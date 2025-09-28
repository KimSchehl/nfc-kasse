#!/bin/bash
# Start NFC-Kasse in development mode
# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
