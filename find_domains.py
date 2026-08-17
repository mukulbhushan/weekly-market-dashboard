import requests
import re

res = requests.get('https://scanx.trade/main-QCTJGINR.js')
text = res.text

# Let's search for "environment" or "prod" or "api" or "domain" or "host"
matches = re.findall(r'(\w+:\s*["\']https?://[^"\']+["\'])', text)
print("Config object matches:")
for m in matches:
    print(" ", m)

# Search for strings containing '.' like '.co' or '.in' or '.trade' or '.com'
domains = set(re.findall(r'["\']([a-zA-Z0-9-]+\.(?:dhan|scanx|trade|co|in|com|net|io|org)[^"\']*)["\']', text))
print("\nDomain strings:")
for d in list(domains)[:30]:
    print(" ", d)
