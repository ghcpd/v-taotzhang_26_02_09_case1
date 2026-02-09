#!/bin/sh

# create virtual environment if not exists
if [ ! -d .venv ]; then
    python -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements-dev.txt

python -m unittest discover -v
