import asyncio,os,sys
from playwright.async_api import async_playwright
async def m(f,out):
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':400,'height':820})
        await pg.goto('file://'+os.getcwd()+'/'+f);await pg.wait_for_timeout(1500)
        print(await pg.evaluate("[...document.querySelectorAll('.page')].map((p,i)=>[i+1,p.scrollHeight-p.clientHeight])"))
        if out:await pg.pdf(path=out,width='400px',height='820px',print_background=True)
        await b.close()
asyncio.run(m(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None))
