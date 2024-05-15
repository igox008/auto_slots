import requests
from urllib.parse import unquote
from datetime import datetime, timedelta
import time

url = 'https://profile.intra.42.fr/slots.json'

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
    'X-Csrf-Token': '/+ohZKq38rMtlDmXcffm6w6bLjUJrLMCs+z1pXx87TIjGPYgGJnLJ43wVl/WvropI6fhlaT+KkitAM8xh20FnQ==',
    'X-Requested-With': 'XMLHttpRequest'
}

cookies = {
    '_ga': 'GA1.1.416685602.1715074746',
    'cf_clearance': 'BzQn.PhtNZjn4qmJzw0jIovm1fmojC5y6eaG6qSEpeA-1715147091-1.0.1.1-Se5dvgqHac.s0AP4w7D2mlvJIfvY6ihRQfUqYva2WTaCfZLPTu5FXXJcCZ5LdcKNhfGgQI7QWuhwbZxDarYU2w',
    'user.id': 'MTY2Mjk2--eddf26d2061f8f3fe1dc43f7477e2c1dfd921a22',
    '_intra_42_session_production': '2286df65d4ef69fd9e61f57004fc9baa',
    'locale': 'en',
    'intra': 'v2',
    'cf_clearance': 'x0q1XKzyL.3yZ3Udlvlp.G28_BhxRMUdiKrrnm9rjEc-1715725819-1.0.1.1-RTunNozbr5qbnGoZ5J_6LysGZIuWWIDHEIOLCt4.0N.qb7qYCw8zRTZ7XQbsFZ0L8j.P5HbkUM2EcJ5yqRcLOw',
    '_ga_BJ34XNRJCV': 'GS1.1.1715725818.63.1.1715727577.0.0.0'
}

# set begin_at to the current date and time
begin_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

# loop forever
while True:
    # set end_at to be equal to begin_at plus 1 hour and 15 minutes
    end_at = (datetime.strptime(begin_at, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=1, minutes=15)).strftime('%Y-%m-%dT%H:%M:%S')

    # update the data dictionary with the new times
    data = {
        'slot[begin_at]': begin_at,
        'slot[end_at]': end_at,
        '_': int(time.time())
    }

    # send the POST request
    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    # check if the response contains the error message
    if 'Ending must be before' in response.json()['message']:
        print('Stopping script...')
        break

    # print the message in the specified format
    message = response.json()['message']
    print(f"from '{begin_at}' to '{end_at}': {message}")

    # set begin_at to be equal to the last end_at plus 15 minutes
    begin_at = (datetime.strptime(end_at, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%S')

