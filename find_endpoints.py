import requests
import re

res = requests.get('https://scanx.trade/main-QCTJGINR.js')
text = res.text

# Look for patterns like 'https://' or 'http://' or endpoints like api/
urls = set(re.findall(r'https?://[a-zA-Z0-9_.-]+(?:\.[a-zA-Z0-9_.-]+)+[/\w\-?=%&.]*', text))
print("All URLs in main JS:")
for u in sorted(urls):
    print(" ", u)

# Search for dhan or scanx API domains
dhan_matches = set(re.findall(r'[a-zA-Z0-9._-]*dhan[a-zA-Z0-9._-]*', text, re.I))
print("\nDhan matches:", list(dhan_matches)[:20])

# Search for API route strings
routes = set(re.findall(r'["\'](/v\d/[^"\']+|/api/[^"\']+|/scanx/[^"\']+)["\']', text))
print("\nRoutes:", routes)
