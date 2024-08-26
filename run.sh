#!/bin/bash


if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <take or delete> <your _intra_42_session_production>"
    exit 1
fi

action=$1

if [ "$action" != "take" ] && [ "$action" != "delete" ]; then
    echo "Invalid action. Use 'take' or 'delete'."
    exit 1
fi

session_cookie=$2

function cleanup {
    echo "Removing virtual environment..."
    deactivate
    rm -rf venv
}

trap cleanup INT TERM

python3 -m venv venv

source venv/bin/activate

pip install -q requests

if [ "$action" == "take" ]; then
    python3 auto_slots.py "$session_cookie"
elif [ "$action" == "delete" ]; then
    python3 delete_slots.py "$session_cookie"
fi

deactivate

rm -rf venv/
