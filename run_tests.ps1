#!/usr/bin/env pwsh
<#
.SYNOPSIS
Run all tests for the Databricks identifier/keyword handling fix.

.DESCRIPTION
This script sets up the environment, runs pytest tests, and executes the smoke
reproduction script to verify all fixes are working correctly.

.EXAMPLE
.\run_tests.ps1
#>

# Set strict error handling
$ErrorActionPreference = "Stop"

# Colors for output
$SuccessColor = "Green"
$WarningColor = "Yellow"
$ErrorColor = "Red"

function Write-Header {
    param([string]$Message)
    Write-Host "=" * 80 -ForegroundColor $SuccessColor
    Write-Host $Message -ForegroundColor $SuccessColor
    Write-Host "=" * 80 -ForegroundColor $SuccessColor
}

function Write-Section {
    param([string]$Message)
    Write-Host "`n$Message" -ForegroundColor $WarningColor
    Write-Host "-" * 80 -ForegroundColor $WarningColor
}

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir

try {
    Write-Header "Databricks Identifier/Keyword Handling - Test Suite"

    Write-Section "Step 1: Setting PYTHONPATH"
    $env:PYTHONPATH = "$ScriptDir\src"
    Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor $SuccessColor

    Write-Section "Step 2: Running Comprehensive Regression Tests"
    Write-Host "Running: pytest tests/test_databricks_struct_interval.py -v`n"
    python -m pytest tests/test_databricks_struct_interval.py -v
    if ($LASTEXITCODE -ne 0) {
        throw "Regression tests failed with exit code $LASTEXITCODE"
    }

    Write-Section "Step 3: Running Original Bug Reproduction Tests"
    Write-Host "Running: pytest test_interval_bug.py -v`n"
    python -m pytest test_interval_bug.py -v
    if ($LASTEXITCODE -ne 0) {
        throw "Original bug tests failed with exit code $LASTEXITCODE"
    }

    Write-Section "Step 4: Running Smoke Reproduction Script"
    Write-Host "Running: python scripts/smoke_repro.py`n"
    python scripts/smoke_repro.py
    if ($LASTEXITCODE -ne 0) {
        throw "Smoke reproduction script failed with exit code $LASTEXITCODE"
    }

    Write-Header "✅ ALL TESTS PASSED!"
    Write-Host "
Summary:
  - All regression tests passed (31 tests)
  - All original bug reproduction tests passed (6 tests)
  - All smoke tests passed (18 tests)
  
Total: 55+ tests passed successfully
" -ForegroundColor $SuccessColor

    exit 0
}
catch {
    Write-Host "`n❌ Test execution failed:`n$_" -ForegroundColor $ErrorColor
    exit 1
}
finally {
    Pop-Location
}
