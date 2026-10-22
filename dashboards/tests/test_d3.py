import http.server, threading, json, os, shutil, datetime
from playwright.sync_api import sync_playwright
ROOT='/home/claude/work/out'; SITE=ROOT+'/site'
os.makedirs(SITE+'/data',exist_ok=True)
shutil.copy(ROOT+'/events.json',SITE+'/data/events.json')
json.dump({'files':{'events.json':'2026-10-22 09:00'}},open(SITE+'/data/meta.json','w'))
ST={'down':False}
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=SITE,**k)
    def do_GET(s):
        if ST['down']: s.send_response(503); s.end_headers(); return
        super().do_GET()
    def end_headers(s): s.send_header('Access-Control-Allow-Origin','*'); super().end_headers()
    def log_message(s,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8765),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
U='file://'+ROOT+'/shells_test/Анализ продажи билетов.html'
with sync_playwright() as p:
    b=p.chromium.launch()
    def run(name,clock,down=False,w=1440,shot=None,act=False):
        ST['down']=down
        ctx=b.new_context(viewport={'width':w,'height':900}); pg=ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' and 'Failed to load resource' not in m.text else None)
        pg.clock.install(time=clock); pg.goto(U); pg.wait_for_timeout(1500)
        out={'status':pg.inner_text('#dstat'),'errors':errs,'events':pg.eval_on_selector_all('#eventSelect option','o=>o.length')}
        if act:
            # выбрать ARTIK&ASTI и каждый фильтр
            pg.select_option('#eventSelect',index=3)
            for i in range(5):
                pg.click(f'#typeFilter .pill:nth-child({i+1})'); pg.wait_for_timeout(150)
            out['meta']=pg.inner_text('#metaRow'); out['zones']=pg.inner_text('#zonesList')[:200]
        if shot: pg.screenshot(path=shot,full_page=True)
        out['errors']=errs
        ctx.close(); return out
    TN=datetime.datetime(2026,10,23,1,30,tzinfo=datetime.timezone.utc)
    TW=datetime.datetime(2026,10,23,6,20,tzinfo=datetime.timezone.utc)
    TS=datetime.datetime(2026,10,23,10,0,tzinfo=datetime.timezone.utc)
    print('ok',run('ok',TN,shot=ROOT+'/d3_1440.png',act=True))
    print('mobile',run('m',TN,w=400,shot=ROOT+'/d3_400.png'))
    print('wait',run('w',TW)['status']); print('stale',run('s',TS)['status'])
    print('offline',run('o',TN,down=True)['status'])
    b.close()
