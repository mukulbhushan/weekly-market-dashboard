import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

s = requests.Session()
r1 = s.get("https://www.nseindia.com", headers=headers)
print("NSE Homepage status:", r1.status_code)

r2 = s.get("https://www.nseindia.com/api/marketStatus", headers=headers)
print("MarketStatus:", r2.status_code)
if r2.status_code == 200:
    print(r2.json())
