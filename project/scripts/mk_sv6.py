import json,datetime as dt
TODAY=dt.date(2026,10,10)
c101=json.load(open('curve101.json'));c61=json.load(open('curve61.json'));c76=json.load(open('curve76.json'))
share=lambda c,W,ev,day:c[str((ev-day).days)] if (ev-day).days<=W else 0
n=lambda x:f"{int(round(x)):,}".replace(',',' ')
out={}
# Михайлов
PN=share(c101,101,dt.date(2026,12,26),TODAY)*7000;PR=PN*60e6/7000
SM=dict(min_t=5830,min_r=50000000,prev="../w/prev/",cur="../w/cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="10.10.2026",last_dm_hm="09.10 21:03",days_left=77,inv=83,ret=12,plan_n=PN,plan_r=round(PR),
 period_sv="08.10 23:31 → 09.10 21:03",sv_bs_when="последнее — 05.10 17:08",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","3 149"],["Снято с продажи","без изменений","109"],["Пригласительные вне групп","Балкон 222 — 51, Лаунж 223 — 16, сектор 110 — 1","+68 · 09.10 17:19–17:21"]],
 sv_title="Сводка — Стас Михайлов, выгрузка 10.10.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 10.10.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",inv_line="Пригласительные за период: 68 (вне ценовых групп: Балкон 222 — 51, Лаунж 223 — 16, сектор 110 — 1; выписаны 09.10 17:19–17:21 МСК) — в список не входят.")
# Жара 78 (квота)
PNz=share(c61,61,dt.date(2026,10,29),TODAY)*747;PRz=PNz*2.3e6/747
SZ=dict(prev="../w/prev/",cur="../w/cur/",data="data78.json",prev_data="data78_prev.json",perf=78,GT=747,GR=2300000,
 exp_date="10.10.2026",last_dm_hm="09.10 08:22",days_left=19,inv=301,ret=11,plan_n=PNz,plan_r=round(PRz),
 period_sv="09.10 09:00 → 10.10 09:00",sv_bs_when="последнее — 23.09 16:45",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","446"]],
 quota_note="Квота: в продаже только часть мероприятия",
 sv_title="Сводка — Жара Медиа Премия 2026, выгрузка 10.10.2026",out_pdf="out/Сводка — Жара Медиа Премия 2026, выгрузка 10.10.2026.pdf",out_pages="svodka_pages_78.json",
 out_html="svodka_78.html",out_png="svodka_78.png",event_line="Жара Медиа Премия 2026, 29.10.2026, Live Арена, Основной зал, id 78",artist="Жара Медиа Премия 2026",inv_line="Пригласительных за период нет.")
# Blok3
PNb=share(c76,76,dt.date(2026,11,24),TODAY)*10855;PRb=PNb*59984000/10855
SB=dict(prev="../w/prev/",cur="../w/cur/",data="data83.json",prev_data="data83_prev.json",perf=83,GT=10855,GR=59984000,
 exp_date="10.10.2026",last_dm_hm="10.10 07:33",days_left=45,inv=288,ret=264,plan_n=PNb,plan_r=round(PRb),
 period_sv="09.10 08:56 → 10.10 07:33",sv_bs_when="последнее — 01.10 17:22",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","8 811"]],
 sv_title="Сводка — Blok3, выгрузка 10.10.2026",out_pdf="out/Сводка — Blok3, выгрузка 10.10.2026.pdf",out_pages="svodka_pages_83.json",
 out_html="svodka_83.html",out_png="svodka_83.png",event_line="Blok3, 24.11.2026, Live Арена, Основной зал, id 83",artist="Blok3",inv_line="Пригласительных за период нет.")
for nm,o in (('svcfg_85',SM),('svcfg_78',SZ),('svcfg_83',SB)):json.dump(o,open(nm+'.json','w'),ensure_ascii=False,indent=1)
print('PN85',PN,PR,'PN78',PNz,PRz,'PN83',PNb,PRb)
