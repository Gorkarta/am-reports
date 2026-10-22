"""Собирает «оболочки» дашбордов, которые при открытии берут данные с GitHub (см. shell_common.py).

  python3 -s mk_shell.py <pf_page.json> <channels.json> <мастер «Каналы продаж».html> <папка_вывода> [BASE_URL]

Результат: «Портфель мероприятий Live Арена.html» (из dash_template.html) и
«Каналы продаж — портфельная аналитика.html» (из действующей мастер-копии). В каждый встроен последний снимок данных
на случай, если GitHub недоступен.
"""
import sys, json, re, os
from shell_common import STATUS_CSS, loader, js_safe

PF_JSON, CH_JSON, CH_MASTER, OUTDIR = sys.argv[1:5]
BASE = sys.argv[5] if len(sys.argv) > 5 else 'https://raw.githubusercontent.com/Gorkarta/am-reports/main/dashboards/data/'
os.makedirs(OUTDIR, exist_ok=True)


def must_replace(text, old, new, count=1):
    assert text.count(old) >= 1, 'не найден фрагмент: ' + old[:70]
    return text.replace(old, new, count)


# ---------------- Портфель мероприятий ----------------
t = open('dash_template.html', encoding='utf-8').read()
pf = json.load(open(PF_JSON, encoding='utf-8'))
t = must_replace(t, '<style>\nbody{width:auto', '<style>' + STATUS_CSS + '</style><style>\nbody{width:auto')
t = must_replace(t, '<div id=hp>{{HELP}}</div>\n{{TOP}}', '<div id=hp></div><div id=dstat class=ds></div>\n<div id=top></div>')
t = must_replace(t, 'const D={{DATA}};', 'const D=PF.data;')
t = must_replace(t, "document.getElementById('zero').textContent={{ZERO}};", "document.getElementById('zero').textContent=PF.zero;")
t = must_replace(t, '<script>\nconst D=PF.data;', '<script>\nfunction startPF(PF){\nPF.data.forEach(function(e){e.name=AMEsc(e.name);e.short=AMEsc(e.short)});\nconst D=PF.data;')
last = t.rindex('</script>')
t = t[:last] + '}\n</script>\n<script>' + loader(BASE) + '\nvar EMB=' + js_safe(json.dumps(pf, ensure_ascii=False, separators=(',', ':'))) + ';\n' \
    "AMLoad({file:'pf_page.json',embedded:EMB,cur:function(d){return d.cur},render:function(PF){" \
    "document.getElementById('top').innerHTML=AMSan(PF.top);document.getElementById('hp').innerHTML=AMSan(PF.help);startPF(PF)}});\n</script>" + t[last + len('</script>'):]
assert '{{' not in t, 'остались незаполненные метки'
open(os.path.join(OUTDIR, 'Портфель мероприятий Live Арена.html'), 'w', encoding='utf-8').write(t)

# ---------------- Каналы продаж ----------------
h = open(CH_MASTER, encoding='utf-8').read()
ch = json.load(open(CH_JSON, encoding='utf-8'))
h = must_replace(h, '</style>', STATUS_CSS + '</style>')   # первый </style> — основной блок стилей
h = must_replace(h, '<p class="subtitle">Комплексный анализ продажи билетов и каналов сбыта</p>',
                 '<p class="subtitle">Комплексный анализ продажи билетов и каналов сбыта</p>\n      <div id="dstat" class="ds"></div>')
m = re.search(r'<script id="dashboard-data" type="application/json">.*?</script>', h, re.S)
assert m, 'не найден блок данных'
h = h[:m.start()] + '<script id="dashboard-data" type="application/json">' + js_safe(json.dumps(ch, ensure_ascii=False, separators=(',', ':'))) + '</script>' + h[m.end():]
h = must_replace(h, '(function(){\n  "use strict";\n  var DATA = JSON.parse(document.getElementById(\'dashboard-data\').textContent);',
                 'function startChannels(DATA){\n  "use strict";')
h = must_replace(h, "  document.getElementById('genDate').textContent = DATA.meta.generated;\n  render();\n})();",
                 "  document.getElementById('genDate').textContent = DATA.meta.generated;\n  render();\n}")
h = must_replace(h, 'Снимок данных на <span id="genDate"></span> · источник — bs_export (билетная система) · статический расчёт, не подключён к базе напрямую',
                 'Данные на <span id="genDate"></span> · источник — выгрузка билетной системы (GitHub), обновляется ежедневно после 09:00 МСК')
h = must_replace(h, 'заказ оплачен (orders.status 10 или 15)', 'заказ оплачен (orders.sold_at заполнено)')
last = h.rindex('</script>')
h = h[:last] + '</script>\n<script>' + loader(BASE) + '\n' \
    "var EMB=JSON.parse(document.getElementById('dashboard-data').textContent);\n" \
    "function esc(d){d.rows.forEach(function(r){r.c=AMEsc(r.c)});d.returns.forEach(function(r){r.c=AMEsc(r.c)});" \
    "['channel_rank','top_bar_keys','top_time_keys'].forEach(function(k){d[k]=d[k].map(AMEsc)});return d}\n" \
    "AMLoad({file:'channels.json',embedded:EMB,cur:function(d){return d.export_cur},render:function(d){startChannels(esc(d))}});\n</script>" + h[last + len('</script>'):]
open(os.path.join(OUTDIR, 'Каналы продаж — портфельная аналитика.html'), 'w', encoding='utf-8').write(h)
print('ok:', os.listdir(OUTDIR))
