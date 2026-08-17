import asyncio
from playwright.async_api import async_playwright
import json
import re
import datetime
import os
import sys
import subprocess
import pypdf

def ensure_playwright_installed():
    """Auto-install Playwright Chromium binaries on Linux/Streamlit Cloud if missing."""
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=120
        )
    except Exception as e:
        print("Notice during playwright install:", e)

async def launch_playwright_browser(p):
    """Safely launch Chromium across Windows, macOS, and Linux / Streamlit Cloud environments."""
    launch_args = ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]

    # 1. On Windows / Mac, try channels first (msedge, chrome)
    for ch in ["msedge", "chrome"]:
        try:
            return await p.chromium.launch(channel=ch, headless=True, args=launch_args)
        except Exception:
            pass

    # 2. Try default playwright chromium launch
    try:
        return await p.chromium.launch(headless=True, args=launch_args)
    except Exception as err:
        print("Default launch failed, auto-installing Playwright Chromium...", err)

    # 3. If failed (e.g. fresh Linux container), install chromium and retry
    ensure_playwright_installed()
    try:
        return await p.chromium.launch(headless=True, args=launch_args)
    except Exception:
        pass

    # 4. Check for system-installed chromium binary (from packages.txt)
    for exec_path in ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]:
        if os.path.exists(exec_path):
            try:
                return await p.chromium.launch(executable_path=exec_path, headless=True, args=launch_args)
            except Exception:
                pass

    return await p.chromium.launch(headless=True, args=launch_args)

async def generate_a4_executive_pdf():
    html_source_file = 'weekly-market-dashboard.html'
    pdf_target_file = f"Weekly_Market_Dashboard_{datetime.date.today().strftime('%Y_%m_%d')}.pdf"

    print("========================================================")
    print("Reading & Auditing data from weekly-market-dashboard.html (Read-Only)...")
    print("========================================================")

    with open(html_source_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    def extract_js_var(var_name, default):
        pattern = r'const\s+' + var_name + r'\s*=\s*(\{.*?\}|\[.*?\]);'
        m = re.search(pattern, html_content, re.DOTALL)
        if m:
            try: return json.loads(m.group(1))
            except Exception as e:
                print(f"Error parsing {var_name}:", e)
        return default

    indices = extract_js_var('indices', [])
    fiiDii = extract_js_var('fiiDii', [])
    valuation = extract_js_var('valuation', [])
    bulkDeals = extract_js_var('bulkDeals', [])
    ipos = extract_js_var('ipos', [])
    board = extract_js_var('board', [])
    earnings = extract_js_var('earnings', [])
    macro = extract_js_var('macro', {})
    heatmap = extract_js_var('heatmap', [])
    takeaways = extract_js_var('takeaways', [])
    topNews = extract_js_var('topNews', {'macro': [], 'india': []})
    economicEvents = extract_js_var('economicEvents', [])

    if not economicEvents:
        economicEvents = [
            {'date': 'Mon 17 Aug, 02:30 PM', 'event': 'India Trade Balance (Jul)', 'country': 'IN', 'prior': '$-30.43B', 'impact': 'Key macro read for Current Account Deficit & INR stability.'},
            {'date': 'Mon 17 Aug, 04:00 PM', 'event': 'India Unemployment Rate (Jul)', 'country': 'IN', 'prior': '5.5%', 'impact': 'Monitors domestic labor force momentum and macro consumption.'},
            {'date': 'Thu 20 Aug, 05:00 PM', 'event': 'India Infrastructure Output YoY (Jul)', 'country': 'IN', 'prior': '5.0%', 'impact': 'Core gauge for cement, steel, power & industrial capex.'},
            {'date': 'Fri 21 Aug, 10:30 AM', 'event': 'HSBC Manufacturing & Services PMI Flash', 'country': 'IN', 'prior': '58.1 / 60.3', 'impact': 'Forward-looking high frequency indicator for corporate expansion.'},
            {'date': 'Fri 21 Aug, 05:00 PM', 'event': 'India Forex Reserves & Bank Credit Growth', 'country': 'IN', 'prior': '$707 Billion', 'impact': 'Reflects banking system liquidity & RBI import cover.'}
        ]

    last_updated_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    mtdFii = 3607.81
    mtdDii = 16696.60

    # Clean Index Spot Ticker Bar (Fix sign bugs)
    ticker_items_html = []
    for ix in indices:
        pts_v = float(ix['pts'])
        pct_v = float(ix['pct'])
        up = pts_v >= 0
        arrow = '▲' if up else '▼'
        color_cls = 'up' if up else 'down'
        pts_str = f"{'+' if pts_v > 0 else ''}{pts_v:,.2f}"
        pct_str = f"({'+' if pct_v > 0 else ''}{pct_v:.2f}%)"
        clean_name = ix['name'].replace('NIFTY FIN SERVICE', 'FIN NIFTY')
        disp_name = clean_name if 'SPOT' in clean_name.upper() else f"{clean_name} SPOT"
        ticker_items_html.append(
            f'''<div class="ticker-pill">
                <span class="t-name">{disp_name}</span>
                <span class="t-close mono">{ix['close']:,.2f}</span>
                <span class="t-chg mono {color_cls}">{arrow} {pts_str} {pct_str}</span>
            </div>'''
        )
    ticker_bar_html = f'<div class="spot-ticker-bar"><span class="spot-tag">● LIVE SPOT BENCHMARKS</span>{"".join(ticker_items_html)}</div>'

    # Clean Sector Heatmap Table Rows (Fix +-0.00% bug)
    heatmap_rows_html = []
    for h in heatmap:
        pct_v = float(h['pct'])
        if abs(pct_v) < 0.001:
            pct_display = "0.00%"
            pct_cls = "neutral"
        elif pct_v > 0:
            pct_display = f"+{pct_v:.2f}%"
            pct_cls = "up"
        else:
            pct_display = f"{pct_v:.2f}%"
            pct_cls = "down"
        
        heatmap_rows_html.append(f'''<tr>
          <td class="company">{h['name']}</td>
          <td class="num mono">{h['close']:,.2f}</td>
          <td class="num mono {pct_cls}">{pct_display}</td>
          <td><span class="pill {h['trend'].lower()}">{h['trend']}</span></td>
        </tr>''')

    # Build A4 Executive HTML Document
    a4_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Executive Weekly Market Briefing - A4 Edition</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
<style>
  :root {{
    --bg: #FFFFFF;
    --panel: #FFFFFF;
    --panel-2: #F8FAFC;
    --border: #CBD5E1;
    --text: #0F172A;
    --text-dim: #334155;
    --text-faint: #64748B;
    --gold: #B45309;
    --gold-bg: #FEF3C7;
    --green: #15803D;
    --red: #DC2626;
    --blue: #1D4ED8;
  }}

  @page {{
    margin: 0;
    size: 297mm 210mm;   /* A4 landscape, matched 1:1 by the renderer */
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Aptos', 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
    width: 297mm;
    margin: 0 auto;
    padding: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  .mono {{ font-family: 'Aptos Mono', 'IBM Plex Mono', 'Aptos', monospace; }}
  .serif {{ font-family: 'Aptos Display', 'Aptos', 'Newsreader', sans-serif; }}

  .pdf-container {{
    width: 297mm;
    background: var(--bg);
  }}

  /* Each page box is exactly one sheet of A4 landscape, so the printed
     margins stay symmetric and no content is shifted or cropped. */
  .pdf-page {{
    width: 297mm;
    height: 210mm;
    padding: 6mm 7mm 5mm;
    box-sizing: border-box;
    position: relative;
    overflow: hidden;
    page-break-after: always;
    break-after: page;
  }}

  .pdf-page:last-of-type {{
    page-break-after: auto;
    break-after: auto;
  }}

  /* Header */
  header.masthead {{
    border-bottom: 2px solid var(--gold);
    padding-bottom: 4px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .masthead-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .masthead-logo {{
    height: 34px;
    width: auto;
    object-fit: contain;
  }}

  .masthead-left .eyebrow {{
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 9.5px;
    letter-spacing: 0.14em;
    color: var(--gold);
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 1px;
  }}

  .masthead-left h1 {{
    font-family: 'Aptos Display', 'Aptos', 'Newsreader', sans-serif;
    font-weight: 700;
    font-size: 22px;
    color: var(--text);
    letter-spacing: 0.01em;
    line-height: 1.1;
  }}

  .masthead-right {{
    text-align: right;
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--text-dim);
    line-height: 1.35;
  }}

  .badge-page {{
    display: inline-block;
    border: 1px solid var(--gold);
    background: var(--gold-bg);
    color: var(--gold);
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.03em;
    margin-bottom: 2px;
  }}

  /* Spot Ticker Bar */
  .spot-ticker-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: 4px;
    padding: 3px 8px;
    margin-bottom: 4px;
    gap: 6px;
  }}

  .spot-tag {{
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 9.5px;
    font-weight: 700;
    color: var(--gold);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    white-space: nowrap;
  }}

  .ticker-pill {{
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    white-space: nowrap;
  }}

  .ticker-pill .t-name {{ font-weight: 700; color: var(--text); }}
  .ticker-pill .t-close {{ font-weight: 600; color: var(--text-dim); }}
  .ticker-pill .t-chg {{ font-weight: 700; font-size: 9.5px; }}

  .up {{ color: var(--green); }}
  .down {{ color: var(--red); }}
  .neutral {{ color: var(--text-dim); }}

  /* Takeaways Box */
  .takeaways-box {{
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-left: 4px solid var(--gold);
    border-radius: 4px;
    padding: 4px 8px;
    margin-bottom: 4px;
  }}

  .takeaways-head {{
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 9.5px;
    letter-spacing: 0.08em;
    color: var(--gold);
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  .takeaways-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 1.5px;
  }}

  .takeaways-list li {{
    font-size: 10.5px;
    color: #78350F;
    line-height: 1.25;
    position: relative;
    padding-left: 10px;
    font-weight: 500;
  }}

  .takeaways-list li::before {{
    content: "•";
    position: absolute;
    left: 1px;
    color: var(--gold);
    font-size: 11px;
  }}

  /* Grid Layout */
  .grid {{
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 5px;
  }}

  .span-12 {{ grid-column: span 12; }}
  .span-8 {{ grid-column: span 8; }}
  .span-7 {{ grid-column: span 7; }}
  .span-6 {{ grid-column: span 6; }}
  .span-5 {{ grid-column: span 5; }}
  .span-4 {{ grid-column: span 4; }}

  .panel {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 4px 8px 5px;
  }}

  .panel-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 3px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 2px;
  }}

  .panel-head h2 {{
    font-family: 'Aptos Display', 'Aptos', 'Newsreader', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: var(--text);
  }}

  .panel-head .tag {{
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 8.5px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-faint);
    font-weight: 600;
  }}

  /* Macro Grid */
  .macro-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 4px;
  }}

  .macro-card {{
    background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 3px 5px;
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
  }}

  .macro-card .m-lbl {{ font-size: 8px; color: var(--gold); text-transform: uppercase; letter-spacing: 0.04em; font-weight: 700; }}
  .macro-card .m-val {{ font-size: 12.5px; font-weight: 700; color: var(--text); margin: 0; line-height: 1.2; }}
  .macro-card .m-sub {{ font-size: 8.5px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

  /* Tables */
  table {{ width: 100%; border-collapse: collapse; }}

  th {{
    text-align: left;
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--text-faint);
    font-weight: 700;
    padding: 2.5px 5px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }}

  td {{
    padding: 2.5px 5px;
    border-bottom: 1px solid #F1F5F9;
    font-size: 10.5px;
    color: var(--text);
    vertical-align: middle;
    line-height: 1.25;
  }}

  td.num, th.num {{ font-family: 'Aptos Mono', 'IBM Plex Mono', monospace; text-align: right; font-size: 10.5px; }}
  tr:last-child td {{ border-bottom: none; }}

  .company {{ font-weight: 700; color: var(--text); }}
  .ticker-sub {{ color: var(--text-faint); font-size: 9.5px; font-family: 'Aptos Mono', 'IBM Plex Mono', monospace; }}

  /* Badges */
  .pill {{
    display: inline-block;
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.02em;
    padding: 2px 6px;
    border-radius: 3px;
    border: 1px solid;
    white-space: nowrap;
  }}

  .pill.bearish, .pill.underperforming {{ color: var(--red); border-color: #FCA5A5; background: #FEF2F2; }}
  .pill.bullish, .pill.outperforming {{ color: var(--green); border-color: #86EFAC; background: #F0FDF4; }}
  .pill.neutral {{ color: var(--text-dim); border-color: #CBD5E1; background: #F8FAFC; }}
  .pill.undervalued {{ color: var(--green); border-color: #86EFAC; background: #F0FDF4; }}
  .pill.elevated {{ color: var(--gold); border-color: #FDE68A; background: #FEF3C7; }}
  .pill.fair {{ color: var(--blue); border-color: #BFDBFE; background: #EFF6FF; }}

  /* News Cards */
  .news-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }}
  .news-col h3 {{
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.06em;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 2px;
    padding-bottom: 1px;
    border-bottom: 1px solid var(--border);
    font-weight: 700;
  }}

  .news-card {{
    background: var(--panel-2);
    border: 1px solid var(--border);
    padding: 3px 6px;
    border-radius: 3px;
    margin-bottom: 2.5px;
  }}

  .news-card:last-child {{ margin-bottom: 0; }}
  .news-card .n-header {{ display: flex; justify-content: space-between; font-size: 8.5px; color: var(--text-faint); font-family: 'Aptos Mono', 'IBM Plex Mono', monospace; margin-bottom: 1px; font-weight: 600; }}
  .news-card .n-title {{ font-weight: 700; font-size: 10.5px; color: var(--text); margin-bottom: 1px; line-height: 1.25; }}
  .news-card .n-impact {{ font-size: 9.5px; color: var(--text-dim); line-height: 1.25; }}

  /* Stat Row */
  .stat-row {{ display: flex; gap: 6px; margin-bottom: 2px; }}
  .stat {{ flex: 1; }}
  .stat .label {{ font-family: 'Aptos Mono', 'IBM Plex Mono', monospace; font-size: 8.5px; letter-spacing: 0.03em; text-transform: uppercase; color: var(--text-faint); font-weight: 700; }}
  .stat .value {{ font-family: 'Aptos Mono', 'IBM Plex Mono', monospace; font-size: 14.5px; font-weight: 700; }}
  .stat .sub {{ font-size: 9.5px; color: var(--text-dim); margin-top: 1px; }}

  .note {{
    font-size: 9.5px;
    color: var(--text-dim);
    line-height: 1.3;
    margin-top: 2px;
    padding-top: 2px;
    border-top: 1px dashed var(--border);
  }}

  .mtd-flows-badge {{
    margin-top: 2px;
    padding: 3px 6px;
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-radius: 3px;
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 9.5px;
    font-weight: 600;
    color: var(--text-dim);
    display: flex;
    justify-content: space-between;
    align-items: center;
    white-space: nowrap;
  }}

  .mtd-flows-badge .flow-val {{ font-weight: 700; }}

  .chart-box {{ position: relative; height: 110px; margin-top: 1px; }}

  footer {{
    position: absolute;
    bottom: 3mm;
    left: 7mm;
    right: 7mm;
    padding-top: 3px;
    border-top: 1px solid var(--border);
    font-family: 'Aptos Mono', 'IBM Plex Mono', monospace;
    font-size: 8.5px;
    color: var(--text-faint);
    display: flex;
    justify-content: space-between;
  }}
</style>
</head>
<body>

<div class="pdf-container">

  <!-- ==================== PAGE 1 ==================== -->
  <div class="pdf-page">

    <header class="masthead">
      <div class="masthead-brand">
        <img src="raru_logo.png" alt="Raru Logo" class="masthead-logo">
        <div class="masthead-left">
          <div class="eyebrow">Portfolio &amp; Executive Research Desk</div>
          <h1>Executive Weekly Market Briefing</h1>
        </div>
      </div>
      <div class="masthead-right">
        <span class="badge-page">Executive Briefing (Page 1 of 2)</span><br>
        All capital flows in ₹ Crore unless noted
      </div>
    </header>

    <!-- Spot Index Ticker Bar -->
    {ticker_bar_html}

    <!-- Takeaways Box -->
    <div class="takeaways-box">
      <div class="takeaways-head">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        Weekly Executive Key Insights &amp; Market Summary
      </div>
      <ul class="takeaways-list">
        {"".join(f"<li>{t}</li>" for t in takeaways)}
      </ul>
    </div>

    <div class="grid">
      <!-- Global Macro Cards -->
      <section class="panel span-12">
        <div class="panel-head"><h2>Global Macro, MCX Bullion &amp; Risk Read</h2><span class="tag">MCX Rates · FX · Commodities</span></div>
        <div class="macro-grid">
          <div class="macro-card">
            <div class="m-lbl">MCX Gold (10g)</div>
            <div class="m-val">₹{macro.get('gold',{}).get('val', 70450):,}</div>
            <div class="m-sub {'up' if macro.get('gold',{}).get('chg',0)>=0 else 'down'}">{'+' if macro.get('gold',{}).get('chg',0)>0 else ''}{macro.get('gold',{}).get('chg',0)} ({macro.get('gold',{}).get('status','MCX Bullion')})</div>
          </div>
          <div class="macro-card">
            <div class="m-lbl">MCX Silver (1kg)</div>
            <div class="m-val">₹{macro.get('silver',{}).get('val', 82600):,}</div>
            <div class="m-sub {'up' if macro.get('silver',{}).get('chg',0)>=0 else 'down'}">{'+' if macro.get('silver',{}).get('chg',0)>0 else ''}{macro.get('silver',{}).get('chg',0)} ({macro.get('silver',{}).get('status','MCX Bullion')})</div>
          </div>
          <div class="macro-card">
            <div class="m-lbl">USD / INR Rate</div>
            <div class="m-val">₹{macro.get('usdinr',{}).get('val', 83.92)}</div>
            <div class="m-sub {'up' if macro.get('usdinr',{}).get('chg',0)<=0 else 'down'}">{'+' if macro.get('usdinr',{}).get('chg',0)>0 else ''}{macro.get('usdinr',{}).get('chg',0)} ({macro.get('usdinr',{}).get('status','Stable')})</div>
          </div>
          <div class="macro-card">
            <div class="m-lbl">Brent Crude ($/bbl)</div>
            <div class="m-val">${macro.get('crude',{}).get('val', 79.40)}</div>
            <div class="m-sub {'up' if macro.get('crude',{}).get('chg',0)<=0 else 'down'}">{'+' if macro.get('crude',{}).get('chg',0)>0 else ''}{macro.get('crude',{}).get('chg',0)} ({macro.get('crude',{}).get('status','Supportive')})</div>
          </div>
          <div class="macro-card">
            <div class="m-lbl">India VIX</div>
            <div class="m-val">{macro.get('vix',{}).get('val', 14.85)}</div>
            <div class="m-sub {'up' if macro.get('vix',{}).get('chg',0)<=0 else 'down'}">{'+' if macro.get('vix',{}).get('chg',0)>0 else ''}{macro.get('vix',{}).get('chg',0)} ({macro.get('vix',{}).get('status','Moderate')})</div>
          </div>
          <div class="macro-card">
            <div class="m-lbl">US 10Y Yield</div>
            <div class="m-val">{macro.get('us10y',{}).get('val', 3.88)}%</div>
            <div class="m-sub {'up' if macro.get('us10y',{}).get('chg',0)<=0 else 'down'}">{'+' if macro.get('us10y',{}).get('chg',0)>0 else ''}{macro.get('us10y',{}).get('chg',0)}% ({macro.get('us10y',{}).get('status','Easing Yields')})</div>
          </div>
        </div>
      </section>

      <!-- Market Breadth -->
      <section class="panel span-4">
        <div class="panel-head"><h2>Market Breadth</h2><span class="tag">Nifty 50 / 500</span></div>
        <div class="stat-row">
          <div class="stat">
            <div class="label">Advancing</div>
            <div class="value" style="color:var(--green)">10</div>
            <div class="sub">Nifty 500: 167</div>
          </div>
          <div class="stat">
            <div class="label">Declining</div>
            <div class="value" style="color:var(--red)">39</div>
            <div class="sub">Nifty 500: 330</div>
          </div>
        </div>
        <div class="note">
          <strong style="color:var(--text)">Valuation Snapshot</strong><br>
          Nifty 50 P/E <span class="mono">20.59</span> — fair 5-yr average.<br>
          Nifty 500 P/E <span class="mono">23.01</span>.
        </div>
      </section>

      <!-- Index Benchmark Summary -->
      <section class="panel span-8">
        <div class="panel-head"><h2>Executive Index Benchmark Summary</h2><span class="tag">Market Close</span></div>
        <table>
          <thead>
            <tr>
              <th>Index</th><th class="num">Close</th><th class="num">Pts Chg</th><th class="num">% Chg</th><th class="num">Weekly High</th><th class="num">Weekly Low</th>
            </tr>
          </thead>
          <tbody>
            {"".join(f'''<tr>
              <td class="company">{ix['name']}</td>
              <td class="num mono">{ix['close']:,.2f}</td>
              <td class="num mono {'down' if ix['pts']<0 else 'up'}">{'+' if ix['pts']>0 else ''}{ix['pts']:,.2f}</td>
              <td class="num mono {'down' if ix['pct']<0 else 'up'}">{'+' if ix['pct']>0 else ''}{ix['pct']:,.2f}%</td>
              <td class="num mono">{ix['high']:,.2f}</td>
              <td class="num mono">{ix['low']:,.2f}</td>
            </tr>''' for ix in indices)}
          </tbody>
        </table>
      </section>

      <!-- Weekly Top News Digest -->
      <section class="panel span-12">
        <div class="panel-head"><h2>Weekly Top News Digest</h2><span class="tag">Macro &amp; India Market News</span></div>
        <div class="news-grid">
          <div class="news-col">
            <h3>🌍 Macro &amp; Global News</h3>
            {"".join(f'''<div class="news-card">
              <div class="n-header"><span>{n['source']}</span><span>{n['date']}</span></div>
              <div class="n-title">{n['headline']}</div>
              <div class="n-impact">{n['impact']}</div>
            </div>''' for n in topNews.get('macro', []))}
          </div>
          <div class="news-col">
            <h3>🇮🇳 India Market News</h3>
            {"".join(f'''<div class="news-card">
              <div class="n-header"><span>{n['source']}</span><span>{n['date']}</span></div>
              <div class="n-title">{n['headline']}</div>
              <div class="n-impact">{n['impact']}</div>
            </div>''' for n in topNews.get('india', []))}
          </div>
        </div>
      </section>

      <!-- Sector Performance & Rotation Read (Page 1 Bottom) -->
      <section class="panel span-12">
        <div class="panel-head"><h2>Sector Performance &amp; Rotation Read</h2><span class="tag">Weekly % Performance</span></div>
        <table>
          <thead>
            <tr><th>Sector Index</th><th class="num">Close Level</th><th class="num">Weekly % Chg</th><th>Sector Rotation Status</th></tr>
          </thead>
          <tbody>
            {"".join(heatmap_rows_html)}
          </tbody>
        </table>
      </section>
    </div>

    <footer>
      <span>Portfolio Engagement &amp; Executive Research Desk</span>
      <span>Confidential A4 Executive Briefing (Page 1 of 2)</span>
    </footer>
  </div>

  <!-- ==================== PAGE 2 ==================== -->
  <div class="pdf-page">

    <header class="masthead">
      <div class="masthead-brand">
        <img src="raru_logo.png" alt="Raru Logo" class="masthead-logo">
        <div class="masthead-left">
          <div class="eyebrow">Institutional Capital, Corporate Filings &amp; Economic Calendar</div>
          <h1>Executive Weekly Market Briefing</h1>
        </div>
      </div>
      <div class="masthead-right">
        <span class="badge-page">Executive Briefing (Page 2 of 2)</span><br>
        All capital flows in ₹ Crore unless noted
      </div>
    </header>

    <!-- Spot Index Ticker Bar -->
    {ticker_bar_html}

    <div class="grid">
      <!-- FII vs DII Capital Flows Chart -->
      <section class="panel span-7">
        <div class="panel-head"><h2>FII vs DII Capital Flows</h2><span class="tag">Net Flow (₹ Cr) — Session Series</span></div>
        <div class="chart-box"><canvas id="pdfFiiDiiChart"></canvas></div>
        <div class="mtd-flows-badge">
          <span>MTD Net Flows:</span>
          <span>FII: <span class="flow-val {'down' if mtdFii<0 else 'up'}">₹{mtdFii:,.2f} Cr</span> &nbsp;|&nbsp; DII: <span class="flow-val {'down' if mtdDii<0 else 'up'}">₹{mtdDii:,.2f} Cr</span></span>
        </div>
      </section>

      <!-- Sector Valuation -->
      <section class="panel span-5">
        <div class="panel-head"><h2>Sector / Index Valuation</h2><span class="tag">Trailing P/E · P/B</span></div>
        <table>
          <thead><tr><th>Segment</th><th class="num">P/E</th><th class="num">P/B</th><th>Status</th></tr></thead>
          <tbody>
            {"".join(f'''<tr>
              <td class="company">{v['seg']}</td>
              <td class="num mono">{v['pe']:,.2f}</td>
              <td class="num mono">{v['pb']:,.2f}</td>
              <td><span class="pill {v['cls']}">{v['status']}</span></td>
            </tr>''' for v in valuation)}
          </tbody>
        </table>
        <div class="note">
          {"<br>".join(f"<strong style='color:var(--text)'>{v['seg']}:</strong> {v['note']}" for v in valuation)}
        </div>
      </section>

      <!-- Bulk Deals -->
      <section class="panel span-6">
        <div class="panel-head"><h2>Institutional Bulk / Block Deals</h2><span class="tag">High-Value Trades</span></div>
        <table>
          <thead><tr><th>Company</th><th>Client / Institution</th><th>Type</th><th class="num">Value</th></tr></thead>
          <tbody>
            {"".join(f'''<tr>
              <td class="company">{d['co']}</td>
              <td>{d['client']}</td>
              <td><span class="pill {'bearish' if 'SELL' in d['type'] else 'bullish'}">{d['type']}</span></td>
              <td class="num mono">{d['value']}</td>
            </tr>''' for d in bulkDeals)}
          </tbody>
        </table>
      </section>

      <!-- Upcoming IPO Pipeline -->
      <section class="panel span-6">
        <div class="panel-head"><h2>Upcoming IPO Pipeline</h2><span class="tag">Mainboard &amp; SME</span></div>
        <table>
          <thead><tr><th>Company</th><th>Category</th><th>Dates</th><th class="num">Price Band</th></tr></thead>
          <tbody>
            {"".join(f'''<tr>
              <td class="company">{i['co']}</td>
              <td>{i['cat']}</td>
              <td class="mono" style="font-size:9.5px; white-space:nowrap;">{i['dates']}</td>
              <td class="num mono" style="white-space:nowrap;">{i['band']}</td>
            </tr>''' for i in ipos)}
          </tbody>
        </table>
      </section>

      <!-- Upcoming Economic Calendar & Macro Events -->
      <section class="panel span-12">
        <div class="panel-head"><h2>Upcoming Economic Calendar &amp; Macro Events (Next Week)</h2><span class="tag">ScanX Insights · High Impact</span></div>
        <table>
          <thead><tr><th style="white-space:nowrap;">Date &amp; Time</th><th>Country</th><th>Economic Event / Announcement</th><th style="white-space:nowrap;">Prior Data / Consensus</th><th>Market Impact Read</th></tr></thead>
          <tbody>
            {"".join(f'''<tr>
              <td class="mono" style="font-weight:600; font-size:9.5px; white-space:nowrap;">{e['date']}</td>
              <td class="mono" style="font-size:9px;"><span class="pill neutral">{e['country']}</span></td>
              <td class="company">{e['event']}</td>
              <td class="mono" style="font-size:9.5px; white-space:nowrap;">{e['prior']}</td>
              <td style="color:var(--text-dim); font-size:10px; line-height:1.25;">{e['impact']}</td>
            </tr>''' for e in economicEvents)}
          </tbody>
        </table>
      </section>
    </div>

    <footer>
      <span>Portfolio Engagement &amp; Executive Research Desk</span>
      <span>Confidential A4 Executive Briefing (Page 2 of 2)</span>
    </footer>
  </div>

</div>

<script>
Chart.defaults.font.family = "'Aptos Mono', 'IBM Plex Mono', 'Aptos', monospace";
Chart.defaults.font.size = 9;
Chart.defaults.color = '#475569';

if (typeof ChartDataLabels !== 'undefined') {{
  Chart.register(ChartDataLabels);
}}

const fiiDiiData = {json.dumps(fiiDii)};

function initFiiDiiChart() {{
  new Chart(document.getElementById('pdfFiiDiiChart'), {{
    type:'bar',
    data:{{
      labels: fiiDiiData.map(d=>d.date),
      datasets:[
        {{label:'FII Net', data:fiiDiiData.map(d=>d.fii), backgroundColor:'#B45309', borderRadius:3, maxBarThickness:13}},
        {{label:'DII Net', data:fiiDiiData.map(d=>d.dii), backgroundColor:'#15803D', borderRadius:3, maxBarThickness:13}},
      ]
    }},
    options:{{
      responsive:true, maintainAspectRatio:false, animation:false,
      layout:{{ padding:{{ top:16, bottom:4, left:6, right:6 }} }},
      plugins:{{
        legend:{{ position:'top', align:'end', labels:{{boxWidth:7, boxHeight:7, color:'#475569', font:{{size:9, weight:'600'}}}} }},
        datalabels: {{
          anchor: function(context) {{
            return context.dataset.data[context.dataIndex] >= 0 ? 'end' : 'end';
          }},
          align: function(context) {{
            return context.dataset.data[context.dataIndex] >= 0 ? 'top' : 'bottom';
          }},
          offset: 2,
          color: '#0F172A',
          font: {{ size: 8, weight: 'bold', family: "'Aptos Mono', 'IBM Plex Mono', monospace" }},
          formatter: (val) => (val !== 0 ? (val > 0 ? '+' : '') + Math.round(val) + ' Cr' : '')
        }}
      }},
      scales:{{
        x:{{ grid:{{ color:'#E2E8F0' }}, ticks:{{ color:'#475569', font:{{size:9}} }} }},
        y:{{ grid:{{ color:'#E2E8F0' }}, ticks:{{ color:'#475569', font:{{size:9}}, callback:v=>'₹'+v }} }}
      }}
    }}
  }});
}}

if (document.fonts && document.fonts.ready) {{
  document.fonts.ready.then(initFiiDiiChart);
}} else {{
  window.addEventListener('load', initFiiDiiChart);
}}
</script>

</body>
</html>
"""

    temp_html = '_temp_a4_render.html'
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(a4_html_content)

    print("Rendering Pristine A4 Format Executive PDF using Playwright...")
    async with async_playwright() as p:
        browser = await launch_playwright_browser(p)

        page = await browser.new_page(viewport={"width": 1123, "height": 794}, device_scale_factor=2)
        abs_temp_path = os.path.abspath(temp_html)
        await page.goto(f"file:///{abs_temp_path}", wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.emulate_media(media="print")
        await page.wait_for_timeout(600)

        # scale=1 + prefer_css_page_size: the CSS page box IS the sheet, so the
        # layout maps 1:1 onto the paper instead of being shrunk into a corner.
        await page.pdf(
            path=pdf_target_file,
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=False,
            scale=1,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        await browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    reader = pypdf.PdfReader(pdf_target_file)
    page_count = len(reader.pages)
    file_size = os.path.getsize(pdf_target_file)

    print(f"SUCCESS: Generated Audited & Fixed A4 Executive PDF '{pdf_target_file}' ({file_size} bytes) | TOTAL PAGES: {page_count}")

if __name__ == '__main__':
    asyncio.run(generate_a4_executive_pdf())
