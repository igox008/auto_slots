import requests
from urllib.parse import unquote
from datetime import datetime, timedelta
import time
import sys
import re

url = 'https://profile.intra.42.fr/slots.json'
intra = 'https://profile.intra.42.fr/'

USAGE = (
    "Usage:\n"
    "  python script.py <session_cookie>\n"
)

if len(sys.argv) != 2:
    print(USAGE)
    sys.exit(1)

session_cookie = sys.argv[1]

# -------------------- Helpers --------------------
def round_up_to_next_quarter(dt: datetime) -> datetime:
    minute = dt.minute
    remainder = minute % 15
    rounded_minutes = minute if remainder == 0 else minute - remainder + 15
    if rounded_minutes == 60:
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return dt.replace(minute=rounded_minutes, second=0, microsecond=0)

def parse_human_time_to_minutes(tstr: str) -> int:
    """
    Parse '2am', '8:30pm', '14', '14:15', '02:05AM' -> minutes since midnight [0..1439].
    Raises ValueError on bad input.
    """
    s = tstr.strip().lower().replace(" ", "")
    am = s.endswith("am")
    pm = s.endswith("pm")
    if am or pm:
        s = s[:-2]

    if ":" in s:
        h_str, m_str = s.split(":", 1)
        if not (h_str.isdigit() and m_str.isdigit()):
            raise ValueError("Use formats like '2am', '8:30pm', '14:00'.")
        h, m = int(h_str), int(m_str)
    else:
        if not s.isdigit():
            raise ValueError("Use formats like '2am', '8:30pm', '14:00'.")
        h, m = int(s), 0

    if am and pm:
        raise ValueError("Time cannot be both AM and PM.")
    if am:
        if h == 12:
            h = 0
    elif pm:
        if h != 12:
            h += 12

    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError("Hour must be 0–23 (or 1–12 with am/pm) and minutes 0–59.")

    return h * 60 + m

def minutes_to_daytime(dt: datetime, mins: int) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=mins)

def compute_window_duration_minutes(start_min: int, end_min: int) -> int:
    """Duration in minutes of [start -> end) possibly wrapping past midnight."""
    if start_min == end_min:
        return 24 * 60
    if start_min < end_min:
        return end_min - start_min
    return (24 * 60 - start_min) + end_min

def advance_into_allowed_window(dt: datetime, mode: str, manual_range=None) -> datetime:
    """
    If dt is outside the allowed window, jump to the next allowed start.
    manual_range = (start_min, end_min) for manual mode.
    """
    if mode == "all":
        return dt

    day_start_min = 9 * 60   # 09:00
    day_end_min   = 21 * 60  # 21:00

    if mode == "day":
        start_min, end_min = day_start_min, day_end_min
    elif mode == "night":
        start_min, end_min = day_end_min, day_start_min  # wrap (21:00 -> 09:00)
    else:
        start_min, end_min = manual_range

    def is_allowed(d: datetime) -> bool:
        m = int((d - d.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() // 60)
        if start_min <= end_min:
            return start_min <= m < end_min
        else:
            return (m >= start_min) or (m < end_min)

    def next_start_after(d: datetime) -> datetime:
        base_midnight = d.replace(hour=0, minute=0, second=0, microsecond=0)
        if start_min <= end_min:
            candidate = minutes_to_daytime(d, start_min)
            if d <= candidate:
                return candidate
            return base_midnight + timedelta(days=1) + timedelta(minutes=start_min)
        else:
            today_start = minutes_to_daytime(d, start_min)
            if d <= today_start:
                return today_start
            return base_midnight + timedelta(days=1) + timedelta(minutes=start_min)

    return dt if is_allowed(dt) else next_start_after(dt)

def bump_after_slot(dt: datetime, mode: str, manual_range=None) -> datetime:
    return advance_into_allowed_window(dt, mode, manual_range)

def prompt_mode_after_lengths() -> str:
    """
    Prompt user for mode AFTER slot_time_minutes and slots_number are known.
    Accept numbers or words. Returns: 'day' | 'night' | 'all' | 'manual'
    """
    options = {
        "1": "day", "day": "day",
        "2": "night", "night": "night",
        "3": "all", "all": "all",
        "4": "manual", "manual": "manual"
    }
    print("\nSelect slot window mode:")
    print("  1) day    (09:00 → 21:00)")
    print("  2) night  (21:00 → next day 09:00)")
    print("  3) all    (no time restriction)")
    print("  4) manual (enter custom times)")
    print("\nNote: AM = morning (00:00–11:59). PM = afternoon/evening (12:00–23:59).")
    while True:
        choice = input("Enter mode (number or name): ").strip().lower()
        if choice in options:
            return options[choice]
        print("Invalid choice. Please enter 1, 2, 3, 4, or day/night/all/manual.")

# -------------------- Session / CSRF --------------------
cookies = {
    '_intra_42_session_production': session_cookie,
}
session = requests.session()
session.cookies.update(cookies)
resp = session.get(intra)
resp_txt = resp.text

csrf_pattern = re.compile(r'<meta\s+name="csrf-token"\s+content="([^"]+)"\s*/?>', re.IGNORECASE)
match = csrf_pattern.search(resp_txt)
csrf_token = match.group(1) if match else ""

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
    'X-Csrf-Token': csrf_token,
    'X-Requested-With': 'XMLHttpRequest'
}
session.headers.update(headers)

# -------------------- Establish initial begin_at --------------------
now = datetime.now()
rounded_time = round_up_to_next_quarter(now)
begin_at = rounded_time.strftime('%Y-%m-%dT%H:%M:%S')

# Look ahead ~2 weeks to read current slots
start = datetime.now()
end = start + timedelta(minutes=19990)
params = {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")}
resp = session.get(url, data=params)
slots = resp.json()

# If there are existing "Available" slots, start 15 minutes after the latest one.
if isinstance(slots, list) and len(slots) > 0:
    try:
        last_slot = max(slots, key=lambda s: s.get("end", ""))
        last_end_iso = str(last_slot["end"]).replace("Z", "+00:00")
        last_end_dt = datetime.fromisoformat(last_end_iso)
        begin_at_dt = last_end_dt + timedelta(minutes=15)
        begin_at = begin_at_dt.strftime("%Y-%m-%dT%H:%M:%S")
        print(f"Starting 15 minutes after your latest existing slot ending at {last_end_dt.isoformat()}")
    except Exception as e:
        print("Couldn't align to last existing slot; using current time. Details:", e)

# -------------------- Collect slot duration and count --------------------
while True:
    try:
        slot_time_minutes = int(input("Enter slot length in minutes (30–360, multiple of 15): "))
        if 30 <= slot_time_minutes <= 360 and (slot_time_minutes % 15 == 0):
            break
        print("slot_time must be between 30 and 360, and a multiple of 15.")
    except ValueError:
        print("That's not a valid number!")

while True:
    try:
        slots_number = int(input("Enter how many slots you want: "))
        if slots_number > 0:
            break
        print("slots_number must be greater than 0.")
    except ValueError:
        print("That's not a valid number!")

# -------------------- Choose mode (AFTER lengths) --------------------
mode = prompt_mode_after_lengths()
manual_range = None

if mode == "manual":
    print("\nManual window selected.")
    print("Enter times like '2am', '8:30pm', '06:00', or '18:45'.")
    print("AM = morning (00:00–11:59). PM = afternoon/evening (12:00–23:59).")
    while True:
        try:
            start_str = input("Enter daily START time (e.g., 9am): ").strip()
            end_str = input("Enter daily END time (e.g., 6pm): ").strip()
            start_min = parse_human_time_to_minutes(start_str)
            end_min = parse_human_time_to_minutes(end_str)

            # Validate window can fit at least one slot
            window_minutes = compute_window_duration_minutes(start_min, end_min)
            if window_minutes < slot_time_minutes:
                print(f"Your window is {window_minutes} minutes, which is shorter than your slot length "
                      f"({slot_time_minutes} minutes). Please choose a wider window.")
                continue

            manual_range = (start_min, end_min)
            break
        except ValueError as ve:
            print(f"Invalid time: {ve}. Please try again.")

    smh, smm = divmod(manual_range[0], 60)
    emh, emm = divmod(manual_range[1], 60)
    wraps = manual_range[0] > manual_range[1]
    print(f"Daily window set to {smh:02d}:{smm:02d} → {emh:02d}:{emm:02d} "
          f"({'wraps past midnight' if wraps else 'same-day'})")
elif mode == "day":
    print("Day mode selected: 09:00 → 21:00 each day.")
elif mode == "night":
    print("Night mode selected: 21:00 → next day 09:00.")
else:
    print("All-hours mode selected: no time restrictions.")

# Align initial begin_at to allowed window
begin_at_dt = datetime.strptime(begin_at, '%Y-%m-%dT%H:%M:%S')
begin_at_dt = advance_into_allowed_window(begin_at_dt, mode, manual_range)
begin_at = begin_at_dt.strftime('%Y-%m-%dT%H:%M:%S')

# -------------------- Create slots respecting the window --------------------
slot_hours = slot_time_minutes // 60
slot_minutes_only = slot_time_minutes % 60

created = 0
while created < slots_number:
    begin_dt = advance_into_allowed_window(datetime.strptime(begin_at, '%Y-%m-%dT%H:%M:%S'), mode, manual_range)
    end_dt = begin_dt + timedelta(hours=slot_hours, minutes=slot_minutes_only)
    end_at = end_dt.strftime('%Y-%m-%dT%H:%M:%S')

    data = {
        'slot[begin_at]': begin_dt.strftime('%Y-%m-%dT%H:%M:%S'),
        'slot[end_at]': end_at,
        '_': int(time.time())
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    try:
        rjson = response.json()
    except Exception:
        print("Unexpected response (non-JSON). Stopping.")
        break

    msg = rjson.get('message', '')
    if 'Ending must be before' in msg:
        print('Stopping script: server says end must be before some boundary.')
        break

    if msg == "Slot has been created":
        print(f"Created: {begin_dt.strftime('%Y-%m-%d %H:%M')} → {end_dt.strftime('%Y-%m-%d %H:%M')} ({slot_time_minutes} minutes)")
        created += 1
        next_begin = end_dt + timedelta(minutes=15)
    else:
        print(f"Skipped ({begin_dt.strftime('%Y-%m-%d %H:%M')} → {end_dt.strftime('%Y-%m-%d %H:%M')}): {msg}")
        next_begin = begin_dt + timedelta(minutes=15)

    next_begin = bump_after_slot(next_begin, mode, manual_range)
    begin_at = next_begin.strftime('%Y-%m-%dT%H:%M:%S')

print(f"Done. Requested: {slots_number}, Created: {created}.")
