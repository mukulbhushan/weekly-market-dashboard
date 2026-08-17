import requests
import json
import datetime
import yfinance as yf

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.nseindia.com/'
}

s = requests.Session()
s.get("https://www.nseindia.com/api/marketStatus", headers=headers)

print("=== 1. ALL INDICES & VALUATIONS ===")
r = s.get("https://www.nseindia.com/api/allIndices", headers=headers)
if r.status_code == 200:
    all_ind = r.json().get('data', [])
    for idx in all_ind:
        if idx.get('index') in ['NIFTY 50', 'NIFTY BANK', 'NIFTY 500', 'NIFTY IT', 'NIFTY FINANCIAL SERVICES']:
            print(f"Index: {idx.get('index')} | Last: {idx.get('last')} | Chg: {idx.get('variation')} | %Chg: {idx.get('percentChange')} | PE: {idx.get('pe')} | PB: {idx.get('pb')} | Adv: {idx.get('advances')} | Dec: {idx.get('declines')}")

print("\n=== 2. EVENT CALENDAR (Board Meetings) ===")
r = s.get("https://www.nseindia.com/api/event-calendar", headers=headers)
if r.status_code == 200:
    events = r.json()
    print(f"Total events found: {len(events)}")
    for ev in events[:5]:
        print(f"  {ev.get('symbol')} | {ev.get('company')} | {ev.get('purpose')} | {ev.get('date')}")

print("\n=== 3. CORPORATE ANNOUNCEMENTS ===")
r = s.get("https://www.nseindia.com/api/corporate-announcements?index=equities", headers=headers)
if r.status_code == 200:
    anns = r.json()
    print(f"Total announcements found: {len(anns)}")
    for an in anns[:5]:
        print(f"  {an.get('symbol')} | {an.get('an_dt')} | {an.get('desc', '')[:60]} | {an.get('attchmntText', '')[:60]}")

print("\n=== 4. YFINANCE INDEX BENCHMARKS ===")
tickers = ['^NSEI', '^NSEBANK', 'NIFTY_FIN_SERVICE.NS', '^BSESN']
for t in tickers:
    try:
        tk = yf.Ticker(t)
        hist = tk.history(period='7d')
        if not hist.empty:
            last_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else last_close
            pts_chg = last_close - prev_close
            pct_chg = pts_chg / prev_close
            w_high = hist['High'].max()
            w_low = hist['Low'].min()
            print(f"Ticker {t}: Close={last_close:.2f}, Chg={pts_chg:.2f}, %Chg={pct_chg*100:.2f}%, W_High={w_high:.2f}, W_Low={w_low:.2f}")
    except Exception as e:
        print(f"Error {t}: {e}")
