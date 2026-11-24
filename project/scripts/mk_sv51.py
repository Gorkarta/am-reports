import json,datetime as dt
TODAY=dt.date(2026,11,24)
c101=json.load(open('curve101.json'))
# Методика v1.7, п. 2.1: выручка — по своей кривой (curve.py пишет curve{W}_r.json)
r101=json.load(open('curve101_r.json'))
share=lambda c,W,ev,day:c[str(max((ev-day).days,0))] if (ev-day).days<=W else 0
PN=share(c101,101,dt.date(2026,12,26),TODAY)*7000;PR=share(r101,101,dt.date(2026,12,26),TODAY)*60e6
def pl(n,a,b,c):
    return f"{n} {a if n%10==1 and n%100!=11 else (b if 2<=n%10<=4 and not 12<=n%100<=14 else c)}"
fm=lambda v:f"{int(v):,}".replace(',',' ')
def mkbs(P,out_prev,out_now):
    d=json.load(open(f'data{P}.json'));rows=[]
    sx=lambda t:(('секторы ' if ',' in t else 'сектор ')+t) if all(x.strip().isdigit() for x in t.split(',')) else t
    for r in sorted(d['diff'],key=lambda r:(str(r['z']),(r['p0'] if r['p0']==r['p0'] else 0),(r['p1'] if r['p1']==r['p1'] else 0))):
        a,b,k=r['p0'],r['p1'],int(r['n']);secs=r['secs']
        if a!=a: rows.append([f"Выведено в продажу · {fm(b)} ₽",sx(secs),'+'+pl(k,'место','места','мест')])
        elif b!=b: rows.append([f"Снято с продажи · {fm(a)} ₽",sx(secs),pl(k,'место','места','мест')])
        else: rows.append([f"{fm(a)} → {fm(b)} ₽ · {('+' if b>a else '−')}{round(abs(b/a-1)*100)}%",sx(secs),pl(k,'место','места','мест')])
    rows.append(['Выведено мест','было '+fm(out_prev),fm(out_now)])
    return rows
BS85=[['Цены групп','без изменений','—'],['Вывод и снятие мест','без изменений','—'],['Выведено мест','было 4 474','4 474']]
SM=dict(min_t=5830,min_r=50000000,prev="prev/",cur="cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="24.11.2026",last_dm_hm="24.11 08:13",days_left=32,inv=339,ret=107,plan_n=PN,plan_r=round(PR),
 period_sv="22.11 23:27 → 24.11 08:13",sv_bs_when="между выгрузками 23.11 и 24.11",
 sv_bs_rows=BS85,
 sv_title="Сводка — Стас Михайлов, выгрузка 24.11.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 24.11.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",
 inv_line="Новых пригласительных за период нет (всего 339); поправка планов 0 билетов / 0 ₽. Возвратов за период 7 билетов на 50 300 ₽ (всего 107; из них 2 билета партера по 14 000 ₽ куплены и возвращены в этом же периоде).")
json.dump(SM,open("svcfg_85.json","w"),ensure_ascii=False,indent=1)
