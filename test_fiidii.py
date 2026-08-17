import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.nseindia.com/reports/fii-dii'
}

s = requests.Session()
s.get("https://www.nseindia.com/api/marketStatus", headers=headers)

r = s.get("https://www.nseindia.com/api/fiidiiTradeReact", headers=headers)
print("FII/DII Status:", r.status_code)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
