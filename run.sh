#!/bin/bash


if { [ "$#" -eq 1 ] && [ "$1" != "get_sess" ] && [ "$1" != "clear" ]; } && [ "$#" -ne 2 ]; then
    echo "Usage: $0 <take or delete> <your _intra_42_session_production>"
    echo "or if you wanna get your _intra_42_session_production"
    echo "use : $0 get_sess"
    echo "if you wanna clear the environement use $0 clear"
    exit 1
fi

action=$1

if [ "$action" != "take" ] && [ "$action" != "delete" ] &&  [ "$action" != "get_sess" ]&&  [ "$action" != "clear" ]; then
    echo "Invalid action. Use 'take', 'delete', 'get_sess' or 'clear'."
    exit 1
fi

session_cookie=$2

function cleanup {
    echo "Removing virtual environment..."
    if [ ! -z "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    rm -rf venv
    exit 1
}

# trap cleanup INT TERM

if [ "$action" == "clear" ]; then
    cleanup
fi

python3 -m venv venv

source venv/bin/activate

echo "Downloading some dependecies..."
pip install -q requests
if [ "$action" == "get_sess" ]; then
    pip install -q readchar
    pip install -q webdriver-manager
    pip install -q selenium
fi


if [ "$action" == "take" ]; then
    python3 auto_slots.py "$session_cookie"
elif [ "$action" == "delete" ]; then
    python3 delete_slots.py "$session_cookie"
elif [ "$action" == "get_sess" ]; then
    python3 session_id.py
fi

deactivate
