import json,datetime as dt
TODAY=dt.date(2026,11,14)
c101=json.load(open('curve101.json'));c61=json.load(open('curve61.json'));c76=json.load(open('curve76.json'))
# Методика v1.7, п. 2.1: выручка — по своей кривой (curve.py пишет curve{W}_r.json)
r101=json.load(open('curve101_r.json'));r61=json.load(open('curve61_r.json'));r76=json.load(open('curve76_r.json'))
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
BS85=mkbs(85,4235,4235)
NOCH=[["Цены и места","без изменений","—"]]
BS78=mkbs(78,720,720)
BS83=mkbs(83,9926,9926)
SM=dict(min_t=5830,min_r=50000000,prev="prev/",cur="cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="14.11.2026",last_dm_hm="14.11 07:43",days_left=42,inv=339,ret=57,plan_n=PN,plan_r=round(PR),
 period_sv="13.11 07:53 → 14.11 07:43",sv_bs_when="изменений нет",
 sv_bs_rows=NOCH+[["Выведено мест","без изменений","4 235"]],
 sv_title="Сводка — Стас Михайлов, выгрузка 14.11.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 14.11.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",
 inv_line="Новых пригласительных за период нет (всего 339); поправка планов 0 билетов / 0 ₽. Возвраты за период: новых нет (всего 57).")
GTz=1021;GRz=2700000
PNz=share(c61,61,dt.date(2026,10,29),TODAY)*GTz;PRz=share(r61,61,dt.date(2026,10,29),TODAY)*GRz
SZ=dict(prev="prev/",cur="cur/",data="data78.json",prev_data="data78_prev.json",perf=78,GT=GTz,GR=GRz,
 exp_date="14.11.2026",last_dm_hm="29.10 17:47",days_left=0,inv=385,ret=54,plan_n=PNz,plan_r=round(PRz),
 period_sv="29.10 17:47 → 29.10 17:47",sv_bs_when="изменений нет",
 sv_bs_rows=NOCH+[["Выведено мест","без изменений","720"]],
 quota_note="Квота: в продаже только часть мероприятия",
 sv_title="Сводка — Жара Медиа Премия 2026, выгрузка 14.11.2026",out_pdf="out/Сводка — Жара Медиа Премия 2026, выгрузка 14.11.2026.pdf",out_pages="svodka_pages_78.json",
 out_html="svodka_78.html",out_png="svodka_78.png",event_line="Жара Медиа Премия 2026, 29.10.2026, Live Арена, Основной зал, id 78",artist="Жара Медиа Премия 2026",
 inv_line="Новых пригласительных за период нет (всего 385). Концерт состоялся 29.10.2026 (до него 0 дн.). Цель квоты 1 021 билет / 2,7 млн ₽ (без изменений).")
GTb=10820;GRb=59579500
PNb=share(c76,76,dt.date(2026,11,24),TODAY)*GTb;PRb=share(r76,76,dt.date(2026,11,24),TODAY)*GRb
SB=dict(prev="prev/",cur="cur/",data="data83.json",prev_data="data83_prev.json",perf=83,GT=GTb,GR=GRb,
 exp_date="14.11.2026",last_dm_hm="14.11 08:47",days_left=10,inv=430,ret=711,plan_n=PNb,plan_r=round(PRb),
 period_sv="13.11 08:32 → 14.11 08:47",sv_bs_when="изменений нет",
 sv_bs_rows=NOCH+[["Выведено мест","без изменений","9 926"]],
 sv_title="Сводка — Blok3, выгрузка 14.11.2026",out_pdf="out/Сводка — Blok3, выгрузка 14.11.2026.pdf",out_pages="svodka_pages_83.json",
 out_html="svodka_83.html",out_png="svodka_83.png",event_line="Blok3, 24.11.2026, Live Арена, Основной зал, id 83",artist="Blok3",
 inv_line="Новых пригласительных за период нет (всего 430); поправка планов 0 (план 10 820 / 59 579 500 ₽ без изменений). Возвраты за период: 34 билета на 233 500 ₽ (всего 711).")
SA=dict(prev="prev/",cur="cur/",data="data57.json",prev_data="data57_prev.json",perf=57,GT=8109,GR=None,
 exp_date="14.11.2026",last_dm_hm="13.11 23:50",days_left=125,inv=0,ret=121,
 period_sv="13.11 04:09 → 13.11 23:50",sv_bs_when="изменений нет",
 sv_bs_rows=NOCH+[["Выведено мест","без изменений","7 467"]],
 noplan_text="плана нет (параметры уточняются)",legend=[5000,15000,30000],
 sv_title="Сводка — Akmal, выгрузка 14.11.2026",out_pdf="out/Сводка — Akmal, выгрузка 14.11.2026.pdf",out_pages="svodka_pages_57.json",
 out_html="svodka_57.html",out_png="svodka_57.png",event_line="Akmal, 19.03.2027, Live Арена, Основной зал, id 57",artist="Akmal",
 inv_line="Пригласительных нет.")
for nm,o in (('svcfg_85',SM),('svcfg_78',SZ),('svcfg_83',SB),('svcfg_57',SA)):json.dump(o,open(nm+'.json','w'),ensure_ascii=False,indent=1)
print('PN85',PN,PR,'PN78',PNz,PRz,'PN83',PNb,PRb)
