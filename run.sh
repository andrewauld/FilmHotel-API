#!/usr/bin/env bash

# Convenience script to run the FilmHotel API using the virtual environment
# This ensures that all dependencies (like fastapi) are correctly loaded.

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Run the FastAPI server using uvicorn
echo "Starting FilmHotel API on http://127.0.0.1:8000"
echo "API Documentation available at http://127.0.0.1:8000/docs"
uvicorn app.main:app --reload
