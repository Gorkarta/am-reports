import asyncio,sys,json,os
from playwright.async_api import async_playwright
S=os.path.dirname(os.path.abspath(__file__))+'/'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page()
    async def route(r):
      if r.request.url.startswith('file://'):return await r.continue_()
      return await r.abort()
    await pg.route('**/*',route);await pg.goto('file://'+S+'gen.html')
    for W in map(int,sys.argv[1:]):
      r=await pg.evaluate("(W)=>{const a=buildCurve('concert',W);const o={};for(let d=0;d<=W;d++)o[d]=a[d];return o}",W)
      json.dump(r,open(S+f'curve{W}.json','w'))
      print(W,[ (d,r[d]) for d in ('0','1','2','3','20','60') if d in r])
    await b.close()
asyncio.run(main())
