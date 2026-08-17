import requests
import re

headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get('https://scanx.trade/main-QCTJGINR.js', headers=headers)
text = res.text

print("Length of main.js:", len(text))

# Search for relative paths like /api/ or /v1/ or endpoints
relative_apis = set(re.findall(r'["\'](/api/[^"\']+|/v\d+/[^"\']+|/scanx/[^"\']+)["\']', text))
print("Relative APIs:", relative_apis)

# Search for domain strings or base URLs
urls = set(re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^"\']*', text))
print("All URLs found count:", len(urls))
for u in list(urls)[:30]:
    print(" ", u)
