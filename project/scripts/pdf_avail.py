# Печать сводки доступности в PDF (одна длинная страница 400 px): python3 -I pdf_avail.py in.html out.pdf [preview.png]
import sys,os,shutil
from playwright.sync_api import sync_playwright
src,pdf=os.path.abspath(sys.argv[1]),sys.argv[2]; png=sys.argv[3] if len(sys.argv)>3 else None
exe=next((p for p in(shutil.which('google-chrome'),shutil.which('chromium'),shutil.which('chromium-browser')) if p),None)
with sync_playwright() as p:
    b=p.chromium.launch(**({'executable_path':exe} if exe else {}))
    pg=b.new_page(viewport={'width':400,'height':800},device_scale_factor=2)
    pg.goto('file://'+src); pg.wait_for_timeout(600)
    h=pg.evaluate('document.documentElement.scrollHeight')
    pg.pdf(path=pdf,width='400px',height=f'{h+2}px',print_background=True,margin={'top':'0','bottom':'0','left':'0','right':'0'})
    if png: pg.screenshot(path=png,full_page=True)
    b.close()
print(pdf,h)
