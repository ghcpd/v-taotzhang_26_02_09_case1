#!/bin/bash
# Bash test runner for Databricks identifier fix
# Sets up virtual environment, installs dependencies, and runs tests

set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

# Set Python path for local modules
export PYTHONPATH=src

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

# Run smoke test
echo "Running smoke test..."
python scripts/smoke_repro.py

echo "Test run complete!"