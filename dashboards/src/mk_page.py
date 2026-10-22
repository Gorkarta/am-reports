"""Собирает pf_page.json — данные дашборда «Портфель мероприятий Live Арена» для загрузки с GitHub.
Запускать после mk_pf.py и mk_pf3.py:  PYTHONPATH=. python3 -s mk_page.py [выходной.json]
Использует тот же код, что mk_dash.py (карточки, темп, подсказки), и вырезает из готовой страницы блок {{TOP}}.
"""
import sys, json
exec(open('mk_dash.py', encoding='utf-8').read())       # даёт t, out, raw, zt, meta и пишет portfolio_map.html
OUT_JSON = sys.argv[1] if len(sys.argv) > 1 else 'pf_page.json'
help_html = open('help_dash.html', encoding='utf-8').read()
pre, post = t.split('{{TOP}}')
prefix = pre.replace('{{HELP}}', help_html)
suffix = post.replace('{{DATA}}', json.dumps(raw, ensure_ascii=False)).replace('{{ZERO}}', json.dumps(zt, ensure_ascii=False))
assert out.startswith(prefix) and out.endswith(suffix), 'структура страницы изменилась — проверить mk_dash.py / шаблон'
top = out[len(prefix):len(out) - len(suffix)]
page = dict(cur=meta['cur'], prev=meta['prev'], last_cur=meta['last_cur'], last_prev=meta['last_prev'],
            top=top, data=raw, zero=zt, help=help_html)
json.dump(page, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('pf_page.json:', OUT_JSON, len(top), 'знаков в блоке TOP,', len(raw), 'мероприятий')
