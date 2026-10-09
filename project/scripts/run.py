import asyncio, json, sys, os
from playwright.async_api import async_playwright
S=os.path.dirname(os.path.abspath(__file__))+'/'
LIB={'papaparse.min.js':S+'node_modules/papaparse/papaparse.min.js','jszip.min.js':S+'node_modules/jszip/dist/jszip.min.js','xlsx.full.min.js':S+'node_modules/xlsx/dist/xlsx.full.min.js'}
DATE,ZIP,WORD,GT,GR=sys.argv[1:6]; START=sys.argv[6] if len(sys.argv)>6 and sys.argv[6]!='-' else None; OUT=sys.argv[7] if len(sys.argv)>7 else 'pf'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':1000})
    async def route(r):
      u=r.request.url
      for k,v in LIB.items():
        if u.endswith(k): return await r.fulfill(path=v, content_type='application/javascript')
      if u.startswith('file://'): return await r.continue_()
      return await r.abort()
    await pg.route('**/*', route)
    pg.on('console', lambda m: print('CONSOLE', m.text) if m.type=='error' else None)
    await pg.goto('file://'+S+'gen.html')
    await pg.click('#navPlanFact')
    await pg.set_input_files('#pfSalesFile', ZIP)
    await pg.wait_for_function("!document.getElementById('pfEventSel').disabled", timeout=240000)
    opts=await pg.eval_on_selector_all('#pfEventSel option','os=>os.map(o=>[o.value,o.textContent])')
    val=[o for o in opts if WORD in o[1]]
    print(val)
    await pg.select_option('#pfEventSel', val[0][0])
    await pg.wait_for_timeout(1000)
    await pg.fill('#pfDate',DATE); await pg.dispatch_event('#pfDate','change'); await pg.fill('#pfGoalT',GT); await pg.fill('#pfGoalR',GR)
    for i in ['pfGoalT','pfGoalR']: await pg.dispatch_event('#'+i,'input'); await pg.dispatch_event('#'+i,'change')
    if START:
      await pg.fill('#pfStart',START); await pg.dispatch_event('#pfStart','input'); await pg.dispatch_event('#pfStart','change')
    await pg.click('#pfBuildBtn'); await pg.wait_for_timeout(3000)
    print('ERR:', await pg.inner_text('#pfErr'))
    print(await pg.inner_text('#pfResult'))
    await b.close()
asyncio.run(main())
