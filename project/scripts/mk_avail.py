# Сводка «Доступность каналов продаж» (HTML для печати в PDF): python3 -I mk_avail.py avail.json out.html
# Данные — из site_check.py. Шрифты — node_modules/@fontsource рядом со скриптом (npm install по package.json).
import json,sys,os,datetime as dt,html
D=json.load(open(sys.argv[1])); outf=sys.argv[2]; d=D['events']
M=lambda s:dt.datetime.fromisoformat(s)+dt.timedelta(hours=3)
snap=M(D['snap']); prev=M(D['prev']); snapd=snap.date()
stamp=snap.strftime('%d.%m.%Y %H:%M')
F='file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'node_modules/@fontsource/unbounded/files/unbounded-cyrillic-')
def n(x): return f"{x:,.0f}".replace(',',' ')
def msk(s): t=dt.datetime.fromisoformat(s)+dt.timedelta(hours=3); return t.strftime('%d.%m %H:%M')
def dd(s): return dt.date.fromisoformat(s[:10])
E_=sorted(d.values(),key=lambda e:e['start'])
al=[e for e in E_ if e['alert']]
ok=[e for e in E_ if not e['alert']]
css=f"""
@font-face{{font-family:Unbounded;font-weight:700;src:url({F}700-normal.woff2)}}
@font-face{{font-family:Unbounded;font-weight:800;src:url({F}800-normal.woff2)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:400px;background:#0c0b12;color:#f5f3fa;font:400 13px/1.45 Inter,sans-serif;font-variant-numeric:tabular-nums;padding:18px}}
.brand{{font:700 12.5px Inter;letter-spacing:.09em;color:#ffb238}}
h1{{font:800 21px/1.2 Unbounded,Inter;margin:6px 0 8px}}
h2{{font:700 14px/1.3 Unbounded,Inter;margin:22px 0 10px}}
.meta{{color:#c7c2d6;font-size:12px}}
.card{{background:#17151f;border:1px solid #2a2635;border-radius:12px;padding:12px 14px;margin-bottom:8px}}
.grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}}
.k{{display:flex;flex-direction:column;justify-content:space-between}} .k .l{{color:#a29cb3;font-size:11px;line-height:1.35;min-height:2.7em}} .k .v{{font:700 18px/1 Inter;margin-top:6px}}
h3{{font:600 12.5px Inter;color:#c7c2d6;margin:14px 0 8px;letter-spacing:.02em}}
.warn{{border-color:#ffcf5c;background:#221d10}}
li.row>span:last-child{{white-space:nowrap;text-align:right}}
.crit{{border-color:#ff5470;background:#22121a}}
.row{{display:flex;justify-content:space-between;align-items:baseline;gap:10px}}
.nm{{font-weight:600}} .sub{{color:#a29cb3;font-size:11.5px}} .sec{{color:#c7c2d6;font-size:12px}}
.big{{font:700 18px Inter;white-space:nowrap}}
.bar{{height:6px;background:#2a2635;border-radius:3px;margin:8px 0 6px;overflow:hidden}}
.bar i{{display:block;height:100%;background:#34d399}}
.chip{{display:inline-block;white-space:nowrap;flex-shrink:0;font-size:10.5px;font-weight:700;padding:1px 7px;border-radius:9px;letter-spacing:.03em}}
.c-ok{{background:#12291f;color:#34d399}} .c-cr{{background:#3a1520;color:#ff5470}} .c-w{{background:#33290f;color:#ffcf5c}}
ul{{list-style:none}} li{{padding:6px 0;border-top:1px solid #2a2635}} li:first-child{{border-top:0}}
.red{{color:#ff5470}} .note{{color:#a29cb3;font-size:11px;margin-top:14px;line-height:1.5}}
"""
h=[f"<html><head><meta charset=utf-8><title>Доступность каналов продаж, выгрузка {snap.strftime('%d.%m.%Y')}</title><style>{css}</style></head><body>"]
h.append(f"""<div class=brand>АРЕНАМАСТЕР · АНАЛИТИКА</div><h1>Доступность каналов продаж</h1>
<div class=meta>Основной канал — сайт livearena.ru<br>Выгрузка БС: {stamp} МСК · сравнение с {prev.strftime('%d.%m.%Y %H:%M')}</div>""")
wn=[e for e in E_ if e.get('warn')]
gr=[e for e in E_ if not e['alert'] and not e.get('warn')]
h.append(f"""<h2>Итого на {snap.strftime('%d.%m')}</h2><div class=grid>
<div class="card k"><div class=l>Мероприятий в продаже</div><div class=v>{len(E_)}</div></div>
<div class="card k crit"><div class=l>Тревога</div><div class=v style="color:#ff5470">{len(al)}</div></div>
<div class="card k warn"><div class=l>Обратить внимание</div><div class=v style="color:#ffcf5c">{len(wn)}</div></div></div>""")
h.append("<h2>Тревога</h2><div class=sub style='margin:-4px 0 10px'>Сайт livearena.ru видит меньше половины мест в продаже</div>")
for e in al:
    sc=[c for c in e['channels'] if c['site']][0]
    b=sc['bound'][0] if sc['bound'] else None
    oth=[c for c in e['channels'] if not c['site'] and c['avail']>0]
    li=[]
    if b: li.append(f"<li class=row><span class=sec>Канал «{html.escape(sc['name'])}» видит только</span><span style='text-align:right;white-space:nowrap'>«{html.escape(b['name'])}»<br>{n(b['price'])} ₽ · свободно {b['free']}</span></li>")
    else: li.append(f"<li class=row><span class=sec>Причина</span><span style='text-align:right;white-space:normal'>{e['reason']}</span></li>")
    if e.get('closed_at'): li.append(f"<li class=row><span class=sec>{'Привязка группы к каналу' if b else 'Закрыт примерно с'}</span><span>{msk(e['closed_at'])}</span></li>")
    li.append(f"<li class=row><span class=sec>Последняя продажа на сайте</span><span>{msk(e['last_site']) if e['last_site'] else 'не было'}</span></li>")
    if e.get('closed_days') is not None: li.append(f"<li class=row><span class=sec>Сайт закрыт</span><span>{e['closed_days']:.0f} дн.{' · новая тревога' if e.get('new_alert') else ''}</span></li>")
    li.append(f"<li class=row><span class=sec>Продажи за 7 дней: сайт / другие</span><span>{e['site7']} / {e['sales7']-e['site7']}</span></li>")
    if e.get('before7'):
        bf=e['before7']; fr=dt.date.fromisoformat(bf['frm']).strftime('%d.%m'); to=dt.date.fromisoformat(bf['to']).strftime('%d.%m')
        li.append(f"<li class=row><span class=sec>За 7 дней до сбоя ({fr}–{to}): сайт / другие</span><span>{bf['site']} / {bf['other']}</span></li>")
    li.append(f"<li class=row><span class=sec>Другие опубликованные каналы</span><span>{len(oth)} · по {n(e['total'])} мест</span></li>")
    h.append(f"""<div class="card crit">
<div class=row><div><div class=nm>{html.escape(e['name'])}</div><div class=sub>{dd(e['start']).strftime('%d.%m.%Y')} · до концерта {(dd(e['start'])-snapd).days} дн. · id&nbsp;{e['id']}</div></div><span class="chip c-cr">ТРЕВОГА</span></div>
<div class=row style="margin-top:10px"><div class=sec>Доступно на сайте</div><div class="big red">{n(e['site'])} из {n(e['total'])}</div></div>
<div class=bar><i style="width:{100*e['site']/e['total']:.1f}%;background:#ff5470"></i></div>
<ul>{''.join(li)}
</ul></div>""")
if not al: h.append("<div class=card><span class=sec>Тревог нет: сайт видит все места в продаже.</span></div>")
else: h.append("<h3>Каналы мероприятий с тревогой</h3>")
for e in al:
    h.append(f"<div class=card><div class=nm style='margin-bottom:4px'>{html.escape(e['name'])}</div><ul>")
    for c in sorted(e['channels'],key=lambda c:(not c['site'],-c['sales7'])):
        col='red' if c['avail']==0 and e['total'] else ''
        h.append(f"<li class=row><span class=sec>{html.escape(c['name'])}</span><span class='{col}' style='white-space:nowrap'>{n(c['avail'])} мест · {c['sales7']} за 7 дн.</span></li>")
    h.append("</ul></div>")
def card(e,cls,chip):
    pct=100*e['site']/e['total'] if e['total'] else 0
    dlt=''
    if e['site_prev'] is not None and e['site_prev']!=e['site']:
        x=e['site']-e['site_prev']; dlt=f" · вчера {n(e['site_prev'])} ({'+' if x>0 else '−'}{n(abs(x))})"
    top=f"<div style='margin-bottom:6px'>{chip}</div>" if cls=='warn' else ''
    right='' if cls=='warn' else chip
    return f"""<div class="card {cls}">{top}<div class=row><div><div class=nm>{html.escape(e['name'])}</div>
<div class=sub>{dd(e['start']).strftime('%d.%m.%Y')} · {(dd(e['start'])-snapd).days} дн. · id&nbsp;{e['id']}</div></div>{right}</div>
<div class=row style="margin-top:8px"><span class=sec>Сайт: {n(e['site'])} из {n(e['total'])}</span><span class=big style="font-size:15px">{pct:.0f}%</span></div>
<div class=bar><i style="width:{pct:.1f}%"></i></div>"""
h.append("<h2>Обратить внимание</h2><div class=sub style='margin:-4px 0 10px'>Нет продаж больше 3 дней; сайт открыт</div>")
if not wn: h.append("<div class=card><span class=sec>Нет.</span></div>")
for e in sorted(wn,key=lambda e:-(e['idle_days'] or 999)):
    ls=f"{msk(e['last_any'])} · {int(e['idle_days'])} дн. без продаж" if e['last_any'] else "продаж не было"
    h.append(card(e,'warn','<span class="chip c-w">НЕТ ПРОДАЖ БОЛЕЕ 3 ДНЕЙ</span>')+f"""<div class=row><span class=sub>Последняя продажа</span><span class=sec>{ls}</span></div></div>""")
h.append(f"<h2>Остальные мероприятия</h2><div class=sub style='margin:-4px 0 10px'>Сайт открыт, продажи идут · {len(gr)}</div>")
for e in gr:
    dlt=f" · сайт вчера {n(e['site_prev'])}" if e['site_prev'] not in (None,e['site']) else ''
    h.append(card(e,'','<span class="chip c-ok">ОК</span>')+f"<div class=sub>Продажи за 7 дн.: сайт {e['site7']} · всего {e['sales7']}{dlt}</div></div>")
chg=[(e,c) for e in E_ for c in e['ch_changes']]
h.append(f"<h2>Изменения настроек каналов с {prev.strftime('%d.%m')}</h2><div class=card>")
if not chg: h.append("<span class=sec>Новых привязок групп к каналам нет.</span>")
else:
    h.append("<ul>")
    for e,c in chg:
        now=', '.join('«'+x+'»' for x in c['now']) or 'все группы'; was=', '.join('«'+x+'»' for x in c['was']) or 'все группы'
        h.append(f"<li><div class=nm>{html.escape(e['name'])}</div><div class=sec>{html.escape(c['name'])}: {html.escape(was)} → {html.escape(now)}{' · '+msk(c['upd']) if c['now'] else ''}</div></li>")
    h.append("</ul>")
h.append("</div>")
h.append("""<div class=note>Доступно — места выведенных групп с тарифом, в продаже (in_sale), не проданные, не пригласительные и не в активной брони; танцпол — по лимиту места. Канал видит все группы сеанса, если к нему ничего не привязано, иначе — только привязанные (Инструкция, п. 4.6). Основной канал — опубликованный канал «… сайт livearena.ru» без пометки «резерв». Тревога — сайт видит меньше 50% доступных мест. Обратить внимание — нет оплаченных продаж ни в одном канале больше 3 дней. Мероприятия — все сеансы архива с датой после выгрузки и местами в продаже, включая не входящие в реестр. Время — МСК.</div></body></html>""")
open(outf,'w').write('\n'.join(h))
