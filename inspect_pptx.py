import zipfile
import re

pptx_path = r'D:\Mukul_doc\Project\Weekly\colour_templeate.pptx'

with zipfile.ZipFile(pptx_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
            content = z.read(name).decode('utf-8', errors='ignore')
            print(f"=== {name} ===")
            texts = re.findall(r'<a:t>(.*?)</a:t>', content)
            print("Texts snippet:", [t for t in texts if len(t.strip()) > 0][:8])
            srgb = set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', content))
            print("SRGB Colors:", srgb)
            print()
            
    if 'ppt/theme/theme1.xml' in z.namelist():
        theme = z.read('ppt/theme/theme1.xml').decode('utf-8', errors='ignore')
        print("=== Theme Colors ===")
        print("Theme SRGB Colors:", set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', theme)))
