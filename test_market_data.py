import requests
import json
import pandas as pd

# Fetch official NSE FII/DII data
url = "https://www.nseindia.com/api/fiidii"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/"
}

session = requests.Session()
# First visit main page to get cookies
session.get("https://www.nseindia.com", headers=headers, timeout=10)
res = session.get(url, headers=headers, timeout=10)
print("NSE FII/DII Status:", res.status_code)
if res.status_code == 200:
    print(res.json())
