#!/bin/bash


if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <your _intra_42_session_production>"
    exit 1
fi

session_cookie=$1

function cleanup {
    echo "Removing virtual environment..."
    deactivate
    rm -rf venv
}

trap cleanup INT TERM

python3 -m venv venv

source venv/bin/activate

pip install -q requests

python auto_slots.py $session_cookie

deactivate

rm -rf venv/
