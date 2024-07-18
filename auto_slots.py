import requests
from urllib.parse import unquote
from datetime import datetime, timedelta
import time
import sys


url = 'https://profile.intra.42.fr/slots.json'

if len(sys.argv) != 2:
    print("Usage: python script.py <session_cookie>")
    sys.exit(1)

session_cookie = sys.argv[1]


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
    'X-Csrf-Token': "k/QPgp7n5qVeNC9iVxWtCI5rijPLzQncd4sndbYJx3Ed0ZFAnN8nbs3MGh6zbghSh2NOohb8s6mq1uWDgdUAHA==" ,
    'X-Requested-With': 'XMLHttpRequest'
}

cookies = {
    '_intra_42_session_production': session_cookie,
}

begin_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

while True:
    end_at = (datetime.strptime(begin_at, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=1, minutes=15)).strftime('%Y-%m-%dT%H:%M:%S')
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
    print(f"from '{begin_at}' to '{end_at}': {message}")

    begin_at = (datetime.strptime(end_at, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%S')

