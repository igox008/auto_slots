import requests
from urllib.parse import unquote
from datetime import datetime, timedelta
import time
import sys
import re


url = 'https://profile.intra.42.fr/slots.json'
intra = 'https://profile.intra.42.fr/'

if len(sys.argv) != 2:
    print("Usage: python script.py <session_cookie>")
    sys.exit(1)

session_cookie = sys.argv[1]

cookies = {
    '_intra_42_session_production': session_cookie,
}

session = requests.session()

session.cookies.update(cookies)
resp = session.get(intra)

resp_txt = resp.text

csrf_pattern = re.compile(r'<meta\s+name="csrf-token"\s+content="([^"]+)"\s*/?>', re.IGNORECASE)
match = csrf_pattern.search(resp_txt)
csrf_token = ""
if match:
    csrf_token = match.group(1)

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://profile.intra.42.fr',
    'Priority': 'u=1, i',
    'Referer': 'https://profile.intra.42.fr/slots',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'X-Csrf-Token': csrf_token ,
    'X-Requested-With': 'XMLHttpRequest'
}

now = datetime.now()

minute = now.minute
remainder = minute % 15
if remainder == 0:
    rounded_minutes = minute
else:
    rounded_minutes = minute - remainder + 15

rounded_time = now.replace(minute=rounded_minutes, second=0, microsecond=0)

if rounded_minutes == 60:
    rounded_time += timedelta(hours=1)
    rounded_time = rounded_time.replace(minute=0)

begin_at = rounded_time.strftime('%Y-%m-%dT%H:%M:%S')

n = 0
while n == 0:
    try:
        slot_time = int(input("enter how much time you want in each slot in minutes : "))
        if slot_time >= 30 and slot_time <= 360 and slot_time % 15 == 0:
            n = 1
        else :
            print("slot_time must be between 30 and 360, and must be a multiple of 15.")
    except ValueError :
        n = 0
        print("That's not a valid number!")
n = 0
while n == 0 :
    try : 
        slots_number = int(input("enter how many slots you want : "))
        if slots_number > 0 :
            n = 1
        else :
            print("slot_time must be greater than 0")
    except ValueError :
        n = 0
        print("That's not a valid number!")
slot_hours = int(slot_time / 60)
slot_time = int(slot_time % 60)
i = 0
while i < slots_number :
    end_at = (datetime.strptime(begin_at, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=slot_hours, minutes=slot_time)).strftime('%Y-%m-%dT%H:%M:%S')
    data = {
        'slot[begin_at]': begin_at,
        'slot[end_at]': end_at,
        '_': int(time.time())
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    if 'Ending must be before' in response.json()['message']:
        print('Stopping script...')
        break

    message = response.json()['message']
    if message == "Slot has been created" :
        print(f"from '{begin_at}' to '{end_at}': {message}")

    if message != "Slot has been created" :
        begin_at = (datetime.strptime(begin_at, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%S')
    else :
        begin_at = (datetime.strptime(end_at, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%S')
        i += 1

