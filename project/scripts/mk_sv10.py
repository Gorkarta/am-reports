import json,datetime as dt
TODAY=dt.date(2026,10,14)
c101=json.load(open('curve101.json'));c61=json.load(open('curve61.json'));c76=json.load(open('curve76.json'))
share=lambda c,W,ev,day:c[str((ev-day).days)] if (ev-day).days<=W else 0
n=lambda x:f"{int(round(x)):,}".replace(',',' ')
out={}
# Михайлов
PN=share(c101,101,dt.date(2026,12,26),TODAY)*7000;PR=PN*60e6/7000
SM=dict(min_t=5830,min_r=50000000,prev="../w/prev/",cur="../w/cur/",data="data85.json",prev_data="data85_prev.json",perf=85,GT=7000,GR=60000000,
 exp_date="14.10.2026",last_dm_hm="13.10 18:52",days_left=73,inv=322,ret=18,plan_n=PN,plan_r=round(PR),
 period_sv="13.10 08:26 → 13.10 18:52",sv_bs_when="последнее — 05.10 17:08",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","3 149"],["Снято с продажи","без изменений","109"],["Пригласительные вне групп","+239 (13.10, 16:52 МСК): Ложи 203–219, 14 лож, без заказа","всего 322"]],
 sv_title="Сводка — Стас Михайлов, выгрузка 14.10.2026",out_pdf="out/Сводка — Стас Михайлов, выгрузка 14.10.2026.pdf",out_pages="svodka_pages_85.json",
 out_html="svodka_85.html",out_png="svodka_85.png",event_line="Стас Михайлов, 26.12.2026, Live Арена, Основной зал, id 85",artist="Стас Михайлов",
 inv_line="Пригласительные за период: +239 (13.10, 16:52 МСК; Ложи 203–219, без заказа, вне ценовых групп) — планы не меняются (Методика, п. 2.9).")
# Жара 78 (квота): поправка плана на 40 пригласительных (Ложа 221, 15 000 ₽) — Методика п. 2.9
GTz=747-40;GRz=2300000-600000
PNz=share(c61,61,dt.date(2026,10,29),TODAY)*GTz;PRz=PNz*GRz/GTz
SZ=dict(prev="../w/prev/",cur="../w/cur/",data="data78.json",prev_data="data78_prev.json",perf=78,GT=GTz,GR=GRz,
 exp_date="14.10.2026",last_dm_hm="14.10 08:10",days_left=15,inv=341,ret=51,plan_n=PNz,plan_r=round(PRz),
 period_sv="12.10 23:16 → 14.10 08:10",sv_bs_when="Ложа 221 — 13.10, 12:44 МСК",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","446"],["Ложа 221 · 40 мест по 15 000 ₽","оплаченные билеты (23.09) аннулированы, на тех же местах выписаны пригласительные","−600 000 ₽"]],
 quota_note="Квота: в продаже только часть мероприятия",
 sv_title="Сводка — Жара Медиа Премия 2026, выгрузка 14.10.2026",out_pdf="out/Сводка — Жара Медиа Премия 2026, выгрузка 14.10.2026.pdf",out_pages="svodka_pages_78.json",
 out_html="svodka_78.html",out_png="svodka_78.png",event_line="Жара Медиа Премия 2026, 29.10.2026, Live Арена, Основной зал, id 78",artist="Жара Медиа Премия 2026",
 ret_line="Возвраты за период: 40 билетов (Ложа 221, 15 000 ₽, 600 000 ₽) — проданы 23.09, аннулированы 13.10; на этих местах выписаны пригласительные.",
 inv_line="Пригласительные: +40 (Ложа 221, 13.10 12:44 МСК; места по 15 000 ₽ в прошлой выгрузке) — планы уменьшены на 40 билетов и 600 000 ₽ (Методика, п. 2.9; действующий план 707 / 1 700 000 ₽).")
# Blok3
PNb=share(c76,76,dt.date(2026,11,24),TODAY)*10853;PRb=PNb*59949000/10853
SB=dict(prev="../w/prev/",cur="../w/cur/",data="data83.json",prev_data="data83_prev.json",perf=83,GT=10853,GR=59949000,
 exp_date="14.10.2026",last_dm_hm="14.10 07:23",days_left=41,inv=290,ret=298,plan_n=PNb,plan_r=round(PRb),
 period_sv="13.10 08:34 → 14.10 07:23",sv_bs_when="последнее — 10.10 20:07–21:11 МСК",
 sv_bs_rows=[["Цены и места","без изменений","—"],["Выведено мест","без изменений","9 829"]],
 sv_title="Сводка — Blok3, выгрузка 14.10.2026",out_pdf="out/Сводка — Blok3, выгрузка 14.10.2026.pdf",out_pages="svodka_pages_83.json",
 out_html="svodka_83.html",out_png="svodka_83.png",event_line="Blok3, 24.11.2026, Live Арена, Основной зал, id 83",artist="Blok3",
 inv_line="Пригласительных за период нет (всего 290; действующий план 10 853 / 59 949 000 ₽ — по поправке 12.10).")
for nm,o in (('svcfg_85',SM),('svcfg_78',SZ),('svcfg_83',SB)):json.dump(o,open(nm+'.json','w'),ensure_ascii=False,indent=1)
print('PN85',PN,PR,'PN78',PNz,PRz,'PN83',PNb,PRb)
