#!/bin/bash

function cleanup {
    echo "Removing virtual environment..."
    deactivate
    rm -rf venv
}

trap cleanup INT TERM

python3 -m venv venv

source venv/bin/activate

pip install -q requests

python auto_slots.py

deactivate

rm -rf venv/
