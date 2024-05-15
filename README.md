# Auto Slots

This repository contains a Python script and a bash script to automate the process of booking slots on the 42 Intra platform.

## Files

- `auto_slots.py`: A Python script that uses the requests library to interact with the 42 Intra platform's API to book slots.
- `run.sh`: A bash script that sets up a virtual environment, installs the necessary dependencies, and runs the Python script.

## Usage

### Python Script

To use the Python script, you need to provide your 42 Intra session cookie as a command-line argument.

```bash
python auto_slots.py <your _intra_42_session_production>
```

The script will then start booking slots, starting from the current time and continuing until it encounters an error or is stopped.

### Bash Script

The bash script automates the process of setting up a virtual environment, installing the necessary dependencies, and running the Python script.

To use the bash script, you need to provide your 42 Intra session cookie as a command-line argument.

```bash
./run.sh <your _intra_42_session_production>
```

The script will then set up a virtual environment, install the requests library, and run the Python script with the provided session cookie.

When the script is stopped (either due to an error or manually), it will clean up by removing the virtual environment.

## Notes

- The Python script uses a while loop to continuously book slots. Each slot is 1 hour and 15 minutes long, and the script will wait 15 minutes between each booking.
- The bash script uses a trap to ensure that the virtual environment is removed when the script is stopped.
- The Python script includes a user agent string in its headers to mimic a web browser. This is necessary to avoid being blocked by the 42 Intra platform's API.
- The Python script uses the datetime library to calculate the start and end times for each slot.
- The Python script uses the random and string libraries to generate a CSRF token. This is necessary to authenticate with the 42 Intra platform's API.

## Disclaimer

This script is intended for educational purposes only. Use it at your own risk. The author is not responsible for any misuse of this script.
