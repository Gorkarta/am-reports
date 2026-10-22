import http.server, threading, json, os, sys, shutil, datetime
from playwright.sync_api import sync_playwright

ROOT = '/home/claude/work/out'
SITE = ROOT + '/site'
os.makedirs(SITE + '/data', exist_ok=True)
for f in ('pf_page.json', 'channels.json'):
    shutil.copy(f'{ROOT}/{f}', f'{SITE}/data/{f}')
json.dump({'export_cur': '2026-10-22 09:00'}, open(SITE + '/data/meta.json', 'w'))
STATE = {'down': False}


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def do_GET(self):
        if STATE['down']:
            self.send_response(503); self.end_headers(); return
        super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*'); super().end_headers()

    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
SH = ROOT + '/shells_test'
PF = f'file://{SH}/Портфель мероприятий Live Арена.html'
CH = f'file://{SH}/Каналы продаж — портфельная аналитика.html'
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()

    def run(name, url, clock=None, down=False, w=1440, h=900, shot=None):
        STATE['down'] = down
        ctx = b.new_context(viewport={'width': w, 'height': h})
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
        if clock:
            pg.clock.install(time=clock)
        pg.goto(url)
        pg.wait_for_timeout(1500)
        st = pg.inner_text('#dstat') if pg.query_selector('#dstat') else None
        cls = pg.get_attribute('#dstat', 'class')
        body = pg.inner_text('body')
        if shot:
            pg.screenshot(path=shot, full_page=True)
        res[name] = dict(status=st, cls=cls, errors=errs, chars=len(body))
        ctx.close()
        return body

    T_NIGHT = datetime.datetime(2026, 10, 23, 1, 30, tzinfo=datetime.timezone.utc)   # 04:30 МСК
    T_WAIT = datetime.datetime(2026, 10, 23, 6, 20, tzinfo=datetime.timezone.utc)     # 09:20 МСК
    T_STALE = datetime.datetime(2026, 10, 23, 10, 0, tzinfo=datetime.timezone.utc)    # 13:00 МСК
    for nm, u in (('pf', PF), ('ch', CH)):
        run(nm + '_ok', u, T_NIGHT, shot=f'{ROOT}/{nm}_1440.png')
        run(nm + '_mobile', u, T_NIGHT, w=400, h=900, shot=f'{ROOT}/{nm}_400.png')
        run(nm + '_wait', u, T_WAIT)
        run(nm + '_stale', u, T_STALE)
        run(nm + '_offline', u, T_NIGHT, down=True, shot=f'{ROOT}/{nm}_offline.png')
    # сравнение с прежней статической страницей «Портфеля»
    body_shell = run('pf_cmp', PF, T_NIGHT)
    STATE['down'] = False
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}); pg = ctx.new_page()
    pg.goto('file:///home/claude/work/src/portfolio_map.html'); pg.wait_for_timeout(800)
    body_static = pg.inner_text('body'); ctx.close()
    res['pf_equal_text_ignoring_status'] = (body_shell.replace('Данные актуальны: выгрузка БС от 22.10.2026 09:00 МСК', '').split() == body_static.split())
    b.close()
for k, v in res.items():
    print(k, json.dumps(v, ensure_ascii=False))
