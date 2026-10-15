import json,datetime as dt
TODAY=dt.date(2026,10,15)
c101=json.load(open('curve101.json'));c61=json.load(open('curve61.json'));c76=json.load(open('curve76.json'))
share=lambda c,W,ev,day:c[str((ev-day).days)] if (ev-day).days<=W else 0
out={}
PN=share(c101,101,dt.date(2026,12,26),TODAY)*7000;PR=PN*60e6/7000
SM=dict(min_t=5830,min_r=50000000,prev="../w/prev/",cur="../w/cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="15.10.2026",last_dm_hm="14.10 23:07",days_left=72,inv=322,ret=18,plan_n=PN,plan_r=round(PR),
 period_sv="13.10 18:52 → 14.10 23:07",sv_bs_when="между выгрузками 14.10 и 15.10",
 sv_bs_rows=[["Цены","без изменений","—"],["Выведено мест: +38","партер, группа 18000 — +22; сектор 108, группа 6000 — +7; сектор 307, группа 3000 — +9 (новая группа)","3 149 → 3 187"],["Снято с продажи","без изменений","109"],["Пригласительные вне групп","без изменений","322"]],
 sv_title="Сводка — Стас Михайлов, выгрузка 15.10.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 15.10.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",
 inv_line="Новых пригласительных за период нет (всего 322). Возвратов за период нет (всего 18).")
GTz=707;GRz=1700000
PNz=share(c61,61,dt.date(2026,10,29),TODAY)*GTz;PRz=PNz*GRz/GTz
SZ=dict(prev="../w/prev/",cur="../w/cur/",data="data78.json",prev_data="data78_prev.json",perf=78,GT=GTz,GR=GRz,
 exp_date="15.10.2026",last_dm_hm="15.10 00:22",days_left=14,inv=341,ret=51,plan_n=PNz,plan_r=round(PRz),
 period_sv="14.10 08:10 → 15.10 00:22",sv_bs_when="изменений нет",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","446"]],
 quota_note="Квота: в продаже только часть мероприятия",
 sv_title="Сводка — Жара Медиа Премия 2026, выгрузка 15.10.2026",out_pdf="out/Сводка — Жара Медиа Премия 2026, выгрузка 15.10.2026.pdf",out_pages="svodka_pages_78.json",
 out_html="svodka_78.html",out_png="svodka_78.png",event_line="Жара Медиа Премия 2026, 29.10.2026, Live Арена, Основной зал, id 78",artist="Жара Медиа Премия 2026",
 inv_line="Новых пригласительных и возвратов за период нет (пригласительных 341, возвратов 51). Действующий план 707 / 1 700 000 ₽ (Методика, п. 2.9).")
GTb=10853-3;GRb=59949000-18000
PNb=share(c76,76,dt.date(2026,11,24),TODAY)*GTb;PRb=PNb*GRb/GTb
SB=dict(prev="../w/prev/",cur="../w/cur/",data="data83.json",prev_data="data83_prev.json",perf=83,GT=GTb,GR=GRb,
 exp_date="15.10.2026",last_dm_hm="15.10 07:54",days_left=40,inv=293,ret=304,plan_n=PNb,plan_r=round(PRb),
 period_sv="14.10 07:23 → 15.10 07:54",sv_bs_when="изменений нет",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","9 829"]],
 sv_title="Сводка — Blok3, выгрузка 15.10.2026",out_pdf="out/Сводка — Blok3, выгрузка 15.10.2026.pdf",out_pages="svodka_pages_83.json",
 out_html="svodka_83.html",out_png="svodka_83.png",event_line="Blok3, 24.11.2026, Live Арена, Основной зал, id 83",artist="Blok3",
 inv_line="Пригласительные за период: +3 (танцпол, 15.10 00:57 МСК, места по 6 000 ₽ в прошлой выгрузке) — планы уменьшены на 3 билета и 18 000 ₽ (Методика, п. 2.9; действующий план 10 850 / 59 931 000 ₽). Возвраты за период: 6 билетов на 44 000 ₽ (всего 304).")
for nm,o in (('svcfg_85',SM),('svcfg_78',SZ),('svcfg_83',SB)):json.dump(o,open(nm+'.json','w'),ensure_ascii=False,indent=1)
print('PN85',PN,PR,'PN78',PNz,PRz,'PN83',PNb,PRb)
