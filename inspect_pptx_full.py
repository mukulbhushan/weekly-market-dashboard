import zipfile
import re

pptx_path = r'D:\Mukul_doc\Project\Weekly\colour_templeate.pptx'

with zipfile.ZipFile(pptx_path, 'r') as z:
    for name in z.namelist():
        if 'slideMaster' in name or 'slideLayout' in name:
            content = z.read(name).decode('utf-8', errors='ignore')
            print(f"=== {name} ===")
            colors = set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', content))
            print("SRGB Colors:", colors)
            print()
