import json,datetime as dt
TODAY=dt.date(2026,10,21)
c101=json.load(open('curve101.json'));c61=json.load(open('curve61.json'));c76=json.load(open('curve76.json'))
share=lambda c,W,ev,day:c[str((ev-day).days)] if (ev-day).days<=W else 0
out={}
PN=share(c101,101,dt.date(2026,12,26),TODAY)*7000;PR=PN*60e6/7000
SM=dict(min_t=5830,min_r=50000000,prev="../prev/",cur="../cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="21.10.2026",last_dm_hm="21.10 08:45",days_left=66,inv=337,ret=21,plan_n=PN,plan_r=round(PR),
 period_sv="20.10 00:29 → 21.10 08:45",sv_bs_when="20.10 в 12:37 МСК",
 sv_bs_rows=[["Ложа 220 — новая группа","10 мест по 30 000 ₽ (распродана 20.10)","+10"],["Премиум бокс 121","выставлены 12 мест по 28 000 ₽","+12"],["Секторы 100: переоценка","106 мест (105, 109): 6 000 → 6 500 ₽","↑ 6 500"],["Секторы 100: новые места","сектор 109: 6 × 6 800 и 6 × 7 000 ₽","+12"],["Сектор 306","выставлены 15 мест по 5 000 ₽","+15"],["Секторы 100: сняты с продажи","8000 — 48 мест (103, 105, 109, 110); 10000 — 14 мест (106, 108)","−62"],["Выведено мест","было 3 187","3 224"]],
 sv_title="Сводка — Стас Михайлов, выгрузка 21.10.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 21.10.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",
 inv_line="Пригласительные за период: 15 (Ложа 207, вне групп, поправка планов 0 / 0 ₽; всего 337).",ret_line="Возвратов за период нет (всего 21).")
GTz=1021;GRz=2700000
PNz=share(c61,61,dt.date(2026,10,29),TODAY)*GTz;PRz=PNz*GRz/GTz
SZ=dict(prev="../prev/",cur="../cur/",data="data78.json",prev_data="data78_prev.json",perf=78,GT=GTz,GR=GRz,
 exp_date="21.10.2026",last_dm_hm="20.10 22:56",days_left=8,inv=341,ret=52,plan_n=PNz,plan_r=round(PRz),
 period_sv="19.10 21:39 → 20.10 22:56",sv_bs_when="20.10 в 12:51–13:17 МСК",
 sv_bs_rows=[["Сектора 100: новые места","4000 — 51, 5000 — 47, 6000 — 13, 7200 — 21, 4500 — 7","+139"],["Сектора 300: новые места","2200 — 51, 2300 — 10, 2500 — 12, 2600 — 8, 2800 — 6, 3000 — 8","+95"],["Балкон 202","выставлены 10 мест по 4 500 ₽","+10"],["Танцпол 2200","лимит группы: 50 → 80 мест","+30"],["Выведено мест","было 446","720"]],
 quota_note="Квота: в продаже только часть мероприятия",
 sv_title="Сводка — Жара Медиа Премия 2026, выгрузка 21.10.2026",out_pdf="out/Сводка — Жара Медиа Премия 2026, выгрузка 21.10.2026.pdf",out_pages="svodka_pages_78.json",
 out_html="svodka_78.html",out_png="svodka_78.png",event_line="Жара Медиа Премия 2026, 29.10.2026, Live Арена, Основной зал, id 78",artist="Жара Медиа Премия 2026",
 inv_line="Пригласительных за период нет (всего 341). Цель квоты пересчитана из-за вывода 274 мест: 1 021 билет / 2,7 млн ₽ (прежний план 707 / 1,7 млн ₽).",ret_line="Возврат за период: 1 билет на 7 200 ₽ (всего 52) — в список не входит.")
GTb=10845;GRb=59902000
PNb=share(c76,76,dt.date(2026,11,24),TODAY)*GTb;PRb=PNb*GRb/GTb
SB=dict(prev="../prev/",cur="../cur/",data="data83.json",prev_data="data83_prev.json",perf=83,GT=GTb,GR=GRb,
 exp_date="21.10.2026",last_dm_hm="21.10 08:18",days_left=34,inv=298,ret=335,plan_n=PNb,plan_r=round(PRb),
 period_sv="20.10 00:34 → 21.10 08:18",sv_bs_when="изменений нет",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","9 829"]],
 sv_title="Сводка — Blok3, выгрузка 21.10.2026",out_pdf="out/Сводка — Blok3, выгрузка 21.10.2026.pdf",out_pages="svodka_pages_83.json",
 out_html="svodka_83.html",out_png="svodka_83.png",event_line="Blok3, 24.11.2026, Live Арена, Основной зал, id 83",artist="Blok3",
 inv_line="Новые пригласительные за период: 2 (сектор 308, ряд 4, места 5–6, по 6 000 ₽; созданы 20.10 в 11:15 МСК) — поправка планов −2 билета / −12 000 ₽, действующий план 10 845 / 59 902 000 ₽ (Методика, п. 2.9).",ret_line="Возвраты за период: 10 билетов на 77 000 ₽ (всего 335) — в список не входят.")
for nm,o in (('svcfg_85',SM),('svcfg_78',SZ),('svcfg_83',SB)):json.dump(o,open(nm+'.json','w'),ensure_ascii=False,indent=1)
print('PN85',PN,PR,'PN78',PNz,PRz,'PN83',PNb,PRb)
