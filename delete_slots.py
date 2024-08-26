import requests
import sys
import time
from datetime import datetime, timedelta
import re


url = 'https://profile.intra.42.fr/slots'
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
    'Accept-Language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7',
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
    'X-Csrf-Token': csrf_token,
    'X-Requested-With': 'XMLHttpRequest'
}


start = datetime.now()
end = start + timedelta(minutes=19990)

data = {
    "start": start.strftime("%Y-%m-%d"),
    "end": end.strftime("%Y-%m-%d")
}




session.headers.update(headers)

resp = session.get(url, data=data)

slots = resp.json()

if not slots :
    print("there is no slots to delete...!")
for slot in slots:
    tmp = {
        "ids" : slot['ids'],
        "_method" : "delete",
        "_" : str(datetime.now()),
        "confirm" : False
    }
    tmp = session.post(f"{url}/{slot['id']}.json", data=tmp, headers=headers)
    print(tmp.json()['message'])
