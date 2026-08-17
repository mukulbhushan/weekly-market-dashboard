import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.nseindia.com/'
}

s = requests.Session()
s.get("https://www.nseindia.com/api/marketStatus", headers=headers)

endpoints = [
    "https://www.nseindia.com/api/allIndices",
    "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050",
    "https://www.nseindia.com/api/snapshot-capital-market-advances",
    "https://www.nseindia.com/api/block-deal",
    "https://www.nseindia.com/api/ipo-detail"
]

for ep in endpoints:
    r = s.get(ep, headers=headers)
    print(f"{ep} -> Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("  Keys:", list(data.keys()) if isinstance(data, dict) else len(data))
