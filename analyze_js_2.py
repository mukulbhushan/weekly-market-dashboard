import requests
import re

res = requests.get('https://scanx.trade/main-QCTJGINR.js')
text = res.text

# Let's search for keywords like http, fetch, axios, post, get, api, prod, backend, dhan
keywords = ['backend', 'baseUrl', 'BASE_URL', 'host', 'api.', 'scan', 'screener', 'dhan.co']

for kw in keywords:
    matches = [m.start() for m in re.finditer(kw, text, re.IGNORECASE)]
    print(f"Keyword '{kw}': {len(matches)} matches")
    for idx in matches[:5]:
        snippet = text[max(0, idx-50):min(len(text), idx+100)]
        print(f"   ... {snippet} ...")
