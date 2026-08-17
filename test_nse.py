import requests

url = "https://www.niftyindices.com/api/indices/getindexdata"
# or nseindia
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': '*/*',
    'Referer': 'https://www.nseindia.com/reports/fii-dii'
}

s = requests.Session()
s.get('https://www.nseindia.com', headers=headers)
res = s.get('https://www.nseindia.com/api/fii-dii', headers=headers)
print("Status:", res.status_code)
if res.status_code == 200:
    print(res.json())
