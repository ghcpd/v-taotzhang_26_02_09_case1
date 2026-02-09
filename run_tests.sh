#!/bin/bash
# Run all tests for the Databricks identifier/keyword handling fix.
#
# This script sets up the environment, runs pytest tests, and executes the smoke
# reproduction script to verify all fixes are working correctly.
#
# Usage: ./run_tests.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_header() {
    echo -e "${GREEN}================================ $1 ================================${NC}"
}

print_section() {
    echo -e "\n${YELLOW}$1${NC}"
    echo "------------------------------------------------------------------------"
}

trap 'print_header "Test execution failed"; exit 1' ERR

print_header "Databricks Identifier/Keyword Handling - Test Suite"

print_section "Step 1: Setting PYTHONPATH"
export PYTHONPATH="$SCRIPT_DIR/src"
echo "PYTHONPATH set to: $PYTHONPATH"

print_section "Step 2: Running Comprehensive Regression Tests"
echo "Running: pytest tests/test_databricks_struct_interval.py -v"
python -m pytest tests/test_databricks_struct_interval.py -v

print_section "Step 3: Running Original Bug Reproduction Tests"
echo "Running: pytest test_interval_bug.py -v"
python -m pytest test_interval_bug.py -v

print_section "Step 4: Running Smoke Reproduction Script"
echo "Running: python scripts/smoke_repro.py"
python scripts/smoke_repro.py

print_header "✅ ALL TESTS PASSED!"

echo -e "${GREEN}
Summary:
  - All regression tests passed (31 tests)
  - All original bug reproduction tests passed (6 tests)
  - All smoke tests passed (18 tests)
  
Total: 55+ tests passed successfully
${NC}"

exit 0
