import json,datetime as dt
TODAY=dt.date(2026,10,22)
c101=json.load(open('curve101.json'));c61=json.load(open('curve61.json'));c76=json.load(open('curve76.json'))
share=lambda c,W,ev,day:c[str((ev-day).days)] if (ev-day).days<=W else 0
out={}
PN=share(c101,101,dt.date(2026,12,26),TODAY)*7000;PR=PN*60e6/7000
SM=dict(min_t=5830,min_r=50000000,prev="../prev/",cur="../cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="22.10.2026",last_dm_hm="21.10 23:05",days_left=65,inv=337,ret=24,plan_n=PN,plan_r=round(PR),
 period_sv="21.10 08:45 → 21.10 23:05",sv_bs_when="изменений нет",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","3 224"]],
 sv_title="Сводка — Стас Михайлов, выгрузка 22.10.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 22.10.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",
 inv_line="Новых пригласительных за период нет (всего 337); поправка планов 0 билетов / 0 ₽.",ret_line="Возвраты за период: 3 билета на 12 000 ₽ — сектор 305, ряд 11, места 29–31 (3 × 4 000 ₽; куплены и возвращены 21.10); всего 24 — в список не входят.")
GTz=1021;GRz=2700000
PNz=share(c61,61,dt.date(2026,10,29),TODAY)*GTz;PRz=PNz*GRz/GTz
SZ=dict(prev="../prev/",cur="../cur/",data="data78.json",prev_data="data78_prev.json",perf=78,GT=GTz,GR=GRz,
 exp_date="22.10.2026",last_dm_hm="21.10 23:09",days_left=7,inv=341,ret=54,plan_n=PNz,plan_r=round(PRz),
 period_sv="20.10 22:56 → 21.10 23:09",sv_bs_when="изменений нет",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","720"]],
 quota_note="Квота: в продаже только часть мероприятия",
 sv_title="Сводка — Жара Медиа Премия 2026, выгрузка 22.10.2026",out_pdf="out/Сводка — Жара Медиа Премия 2026, выгрузка 22.10.2026.pdf",out_pages="svodka_pages_78.json",
 out_html="svodka_78.html",out_png="svodka_78.png",event_line="Жара Медиа Премия 2026, 29.10.2026, Live Арена, Основной зал, id 78",artist="Жара Медиа Премия 2026",
 inv_line="Пригласительных за период нет (всего 341). Цель квоты 1 021 билет / 2,7 млн ₽ (без изменений).",ret_line="Возвраты за период: 2 билета на 14 400 ₽ — сектор 102, ряд 5, места 19–20 (2 × 7 200 ₽; куплены 06.09, удалены 21.10); всего 54 — в список не входят.")
GTb=10845;GRb=59902000
PNb=share(c76,76,dt.date(2026,11,24),TODAY)*GTb;PRb=PNb*GRb/GTb
SB=dict(prev="../prev/",cur="../cur/",data="data83.json",prev_data="data83_prev.json",perf=83,GT=GTb,GR=GRb,
 exp_date="22.10.2026",last_dm_hm="22.10 07:48",days_left=33,inv=298,ret=340,plan_n=PNb,plan_r=round(PRb),
 period_sv="21.10 08:18 → 22.10 07:48",sv_bs_when="изменений нет",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","9 829"]],
 sv_title="Сводка — Blok3, выгрузка 22.10.2026",out_pdf="out/Сводка — Blok3, выгрузка 22.10.2026.pdf",out_pages="svodka_pages_83.json",
 out_html="svodka_83.html",out_png="svodka_83.png",event_line="Blok3, 24.11.2026, Live Арена, Основной зал, id 83",artist="Blok3",
 inv_line="Новых пригласительных за период нет (всего 298); действующий план 10 845 / 59 902 000 ₽ (Методика, п. 2.9).",ret_line="Возвраты за период: 5 билетов на 50 500 ₽ — Премиум бокс 125, ряд 3, места 10–11 (2 × 17 000 ₽); сектор 306, ряд 15, место 19 (4 500 ₽); танцпол (2 × 6 000 ₽); всего 340 — в список не входят.")
for nm,o in (('svcfg_85',SM),('svcfg_78',SZ),('svcfg_83',SB)):json.dump(o,open(nm+'.json','w'),ensure_ascii=False,indent=1)
print('PN85',PN,PR,'PN78',PNz,PRz,'PN83',PNb,PRb)
