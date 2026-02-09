# Windows PowerShell script to run tests

if (-Not (Test-Path .venv)) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

python -m unittest discover -v
