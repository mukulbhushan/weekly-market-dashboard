import zipfile
import xml.etree.ElementTree as ET

pptx_path = r'D:\Mukul_doc/Project/Weekly/colour_templeate.pptx'

with zipfile.ZipFile(pptx_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
            content = z.read(name).decode('utf-8', errors='ignore')
            print(f"=== {name} ===")
            if 'bg' in content:
                bg_match = content[content.find('<p:bg>'):content.find('</p:bg>')+7] if '<p:bg>' in content else ''
                print("BG snippet:", bg_match[:200])
            
            # Check solid fills
            fills = [line for line in content.split('>') if 'srgbClr' in line or 'solidFill' in line]
            print("Fill lines snippet:", fills[:6])
            print()
