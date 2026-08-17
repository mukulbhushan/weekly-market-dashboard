import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://scanx.trade/'
}

res = requests.get('https://scanx.trade/', headers=headers)
print("Page length:", len(res.text))

scripts = re.findall(r'src="([^"]+\.js)"', res.text)
print("Script tags found:", scripts)

for script in scripts:
    script_url = script if script.startswith('http') else f"https://scanx.trade/{script.lstrip('/')}"
    print(f"\nFetching {script_url}...")
    try:
        s_res = requests.get(script_url, headers=headers)
        endpoints = set(re.findall(r'https://[a-zA-Z0-9_.-]+/[a-zA-Z0-9_./\-?=&%]+', s_res.text))
        api_like = [e for e in endpoints if 'api' in e or 'v1' in e or 'v2' in e or 'scan' in e or 'dhan' in e or 'trade' in e]
        print(f"Found {len(api_like)} API-like endpoints:")
        for ep in api_like[:20]:
            print("  ", ep)
    except Exception as e:
        print("Error fetching script:", e)
