import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.nseindia.com/'
}

s = requests.Session()
s.get("https://www.nseindia.com/api/marketStatus", headers=headers)

test_urls = {
    "allIndices": "https://www.nseindia.com/api/allIndices",
    "fiidii": "https://www.nseindia.com/api/fiidiiTradeReact",
    "block_deals": "https://www.nseindia.com/api/block-deal",
    "bulk_deals": "https://www.nseindia.com/api/snapshot-capital-market-bulk-deals",
    "corporate_announcements": "https://www.nseindia.com/api/corporate-announcements?index=equities",
    "event_calendar": "https://www.nseindia.com/api/event-calendar",
    "top_gainers": "https://www.nseindia.com/api/live-analysis-variations?index=gainers",
    "top_losers": "https://www.nseindia.com/api/live-analysis-variations?index=losers",
    "equity_master": "https://www.nseindia.com/api/equity-master"
}

results = {}
for name, url in test_urls.items():
    try:
        r = s.get(url, headers=headers, timeout=10)
        results[name] = {
            "status": r.status_code,
            "sample": str(r.json())[:200] if r.status_code == 200 else r.text[:100]
        }
    except Exception as e:
        results[name] = {"error": str(e)}

with open("nse_endpoints_test.json", "w") as f:
    json.dump(results, f, indent=2)

print("Test complete. Results saved to nse_endpoints_test.json")
