import json
import re

with open('weekly-market-dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

def extract_js_var(var_name):
    # Match const var_name = { ... }; or const var_name = [ ... ];
    pattern = r'const\s+' + var_name + r'\s*=\s*(\{.*?\}|\[.*?\]);'
    m = re.search(pattern, content, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception as e:
            print(f"Error parsing {var_name}:", e)
    return None

for var in ['indices', 'fiiDii', 'valuation', 'bulkDeals', 'ipos', 'board', 'earnings', 'macro', 'heatmap', 'takeaways', 'topNews']:
    val = extract_js_var(var)
    print(f"{var}:", type(val), len(val) if isinstance(val, (list, dict)) else val)
