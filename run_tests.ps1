# PowerShell test runner for Databricks identifier fix
# Sets up virtual environment, installs dependencies, and runs tests

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Install/update dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt
if (Test-Path "requirements-dev.txt") {
    pip install -r requirements-dev.txt
}

# Set Python path for local modules
$env:PYTHONPATH = "src"

# Run tests
Write-Host "Running tests..."
python -m pytest tests/ -v

# Run smoke test
Write-Host "Running smoke test..."
python scripts/smoke_repro.py

Write-Host "Test run complete!"