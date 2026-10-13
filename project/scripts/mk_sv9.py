import json,datetime as dt
TODAY=dt.date(2026,10,13)
c101=json.load(open('curve101.json'));c61=json.load(open('curve61.json'));c76=json.load(open('curve76.json'))
share=lambda c,W,ev,day:c[str((ev-day).days)] if (ev-day).days<=W else 0
n=lambda x:f"{int(round(x)):,}".replace(',',' ')
out={}
# Михайлов
PN=share(c101,101,dt.date(2026,12,26),TODAY)*7000;PR=PN*60e6/7000
SM=dict(min_t=5830,min_r=50000000,prev="../w/prev/",cur="../w/cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="13.10.2026",last_dm_hm="13.10 08:26",days_left=74,inv=83,ret=13,plan_n=PN,plan_r=round(PR),
 period_sv="12.10 06:33 → 13.10 08:26",sv_bs_when="последнее — 05.10 17:08",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","3 149"],["Снято с продажи","без изменений","109"],["Пригласительные вне групп","новых нет (с 09.10 — 68 в Балкон 222, Лаунж 223, сектор 110)","без изменений"]],
 sv_title="Сводка — Стас Михайлов, выгрузка 13.10.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 13.10.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",inv_line="Пригласительных за период нет.")
# Жара 78 (квота)
PNz=share(c61,61,dt.date(2026,10,29),TODAY)*747;PRz=PNz*2.3e6/747
SZ=dict(prev="../w/prev/",cur="../w/cur/",data="data78.json",prev_data="data78_prev.json",perf=78,GT=747,GR=2300000,
 exp_date="13.10.2026",last_dm_hm="12.10 23:16",days_left=16,inv=301,ret=11,plan_n=PNz,plan_r=round(PRz),
 period_sv="11.10 20:14 → 12.10 23:16",sv_bs_when="последнее — 23.09 16:45",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","446"]],
 quota_note="Квота: в продаже только часть мероприятия",
 sv_title="Сводка — Жара Медиа Премия 2026, выгрузка 13.10.2026",out_pdf="out/Сводка — Жара Медиа Премия 2026, выгрузка 13.10.2026.pdf",out_pages="svodka_pages_78.json",
 out_html="svodka_78.html",out_png="svodka_78.png",event_line="Жара Медиа Премия 2026, 29.10.2026, Live Арена, Основной зал, id 78",artist="Жара Медиа Премия 2026",inv_line="Пригласительных за период нет.")
# Blok3
PNb=share(c76,76,dt.date(2026,11,24),TODAY)*10853;PRb=PNb*59949000/10853
SB=dict(prev="../w/prev/",cur="../w/cur/",data="data83.json",prev_data="data83_prev.json",perf=83,GT=10853,GR=59949000,
 exp_date="13.10.2026",last_dm_hm="13.10 08:34",days_left=42,inv=290,ret=291,plan_n=PNb,plan_r=round(PRb),
 period_sv="12.10 08:44 → 13.10 08:34",sv_bs_when="последнее — 10.10 20:07–21:11 МСК",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","9 829"]],
 sv_title="Сводка — Blok3, выгрузка 13.10.2026",out_pdf="out/Сводка — Blok3, выгрузка 13.10.2026.pdf",out_pages="svodka_pages_83.json",
 out_html="svodka_83.html",out_png="svodka_83.png",event_line="Blok3, 24.11.2026, Live Арена, Основной зал, id 83",artist="Blok3",inv_line="Пригласительные: +2 билета (12.10, 17:25 МСК; места по 17 500 ₽ в прошлой выгрузке) — планы уменьшены на 2 билета и 35 000 ₽ (Методика, п. 2.9; действующий план 10 853 / 59 949 000 ₽).")
for nm,o in (('svcfg_85',SM),('svcfg_78',SZ),('svcfg_83',SB)):json.dump(o,open(nm+'.json','w'),ensure_ascii=False,indent=1)
print('PN85',PN,PR,'PN78',PNz,PRz,'PN83',PNb,PRb)
