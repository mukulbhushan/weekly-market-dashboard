import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

reader = pypdf.PdfReader('Weekly_Market_Dashboard_2026_08_14.pdf')
print(f"Total Pages: {len(reader.pages)}")

for idx, page in enumerate(reader.pages):
    print(f"\n=================== PAGE {idx+1} TEXT ===================")
    text = page.extract_text()
    print(text)
