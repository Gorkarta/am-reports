"""Сводный дашборд «Мероприятия Live Арена»: python3 mk_pf.py cur prev; python3 mk_dash.py → portfolio_map.html"""
import json,html,re as _re
exec(open('mk_pf2.py').read())
meta=json.load(open('pf_meta.json'))
fm=lambda s:f"{s[8:10]}.{s[5:7]}.{s[:4]}"
def dm(s):return f"{s[8:10]}.{s[5:7]}.{s[:4]} {s[11:16]}"
per=f"<div class=per><span>Изменения за период</span><b>с {fm(meta['prev'])} на {fm(meta['cur'])}</b></div><div class=m2 style=\"margin-top:6px\">Последний билет в выгрузке: <b style=\"color:#f5f3fa\">{dm(meta['last_cur'])}</b> · в прошлой выгрузке: {dm(meta['last_prev'])}</div>\n"
cnt2=lambda *s:len([e for e in D2 if e['st'] in s])
SHORT=[('Музыкальная премия СуперЛайкШоу СТС Kids','СуперЛайк СТС Kids'),('Николай Басков. Юбилейное шоу','Н. Басков'),('Стас Михайлов. Народный Корпоратив','Стас Михайлов'),('Максим Фадеев. Концерт ТВ-съёмка','Максим Фадеев'),('Российская национальная музыкальная премия «Виктория-2027»','Виктория-2027'),('Сольный стендап-концерт Виктории Складчиковой','Складчикова'),('СУПЕРДИСКОТЕКА 90-Х: «ЭТО ФАНТАСТИКА!» (МОСКВА)','Супердискотека 90-х'),('Сольный Стендап Концерт Гурам Амарян «Базар»','Гурам Амарян'),('Comedy Club. Большой концерт. Новое и лучшее','Comedy Club'),('Восемнадцать Друзей Дробыша','Друзья Дробыша'),('ЖАРА МУЗЫКАЛЬНАЯ ПРЕМИЯ 2027','ЖАРА 2027'),('Жара Медиа Премия 2026','Жара Медиа Премия'),('АРИЯ. КОГДА НАСТАНЕТ ЗАВТРА','АРИЯ')]
exec(open('mk_cards.py').read())
kk=f'''<div class="kp kk3"><div class=c><div class=n>+{format(nn,',').replace(',',' ')}</div><div class=s>билетов за период</div></div><div class=c><div class=n>+{nr/1e6:.2f} млн ₽</div><div class=s>выручка за период</div></div><div class=c><div class=n>{len(CD)}</div><div class=s>мероприятий в продаже</div></div></div>
<div class="kp kk4"><div class=c><div class=n style="color:#34d399">{TN['h']}</div><div class=s>Высокий темп продаж</div></div><div class=c><div class=n style="color:#ffcf5c">{TN['m']}</div><div class=s>Средний темп продаж</div></div><div class=c><div class=n style="color:#ff5470">{TN['l']}</div><div class=s>Низкий темп продаж</div></div><div class=c><div class=n style="color:#a29cb3">{len(off)}</div><div class=s>не в продаже</div></div></div>
'''+CARDS
rest=''
if len(prob)>SH: rest=f'<div class=m style="margin-top:8px">и ещё {len(prob)-SH}: '+', '.join(html.escape(e['name'].split(' · ')[0][:32]+' '+e['start'][8:10]+'.'+e['start'][5:7]) for e in prob[SH:])+'</div>'
prs=''.join(f'<div class=pr><b class="{e["cls"]}">{e["st"]}</b> {html.escape(e["name"][:34])}<em>{e["start"][8:10]}.{e["start"][5:7]} · {e["sold"]} бил. · 7 дн.: {e["w7"]} (было {e["pw7"]})</em></div>' for e in prob[:SH])
g=f'<div class=g><div class=c><h3>Лидеры периода (с {meta["prev"][8:10]}.{meta["prev"][5:7]})</h3>{leaders}</div><div class=c><h3>Замедлились (7 дн. к пред. 7 дн.)</h3>{slowb}</div><div class=c><h3>Требуют внимания</h3>{prs}{rest}</div></div>\n'
raw=[e for e in json.load(open('pf_data.json')) if 'не трогать' not in e['name'] and e['sold_p']>0]
for e in raw:
    sh=e['name']
    for a_,b_ in SHORT: sh=sh.replace(a_,b_)
    e['short']=sh;e['dt']=e['start'][8:10]+'.'+e['start'][5:7];e.pop('series',None)
zero=[e for e in json.load(open('pf_data.json')) if 'не трогать' not in e['name'] and e['sold_p']==0 and e['cap']>0]
zt='Не показаны (0 билетов): '+', '.join(f"{e['name'].split('.')[0][:30]} {e['start'][8:10]}.{e['start'][5:7]}" for e in zero)+'; не в продаже: '+', '.join(f"{e['name'].split('.')[0]} {e['start'][8:10]}.{e['start'][5:7]}" for e in off)+'. Очень малые продажи показаны минимальным размером.'
t=open('dash_template.html').read()
out=t.replace('{{HELP}}',open('help_dash.html').read()).replace('{{TOP}}',per+kk+g).replace('{{DATA}}',json.dumps(raw,ensure_ascii=False)).replace('{{ZERO}}',json.dumps(zt,ensure_ascii=False))
TIPS={
'билетов за период':'Реализованные билеты: проданные + пригласительные (минус возвраты и аннулирования). Сравнение двух последних выгрузок БС по всем мероприятиям.',
'выручка за период':'Только по проданным билетам; пригласительные — 0 ₽.',
'мероприятий в продаже':'Мероприятия, по которым есть оплаченные билеты. Тестовые и служебные не учитываются.',
'Высокий темп продаж':'Продажи за 7 дней ≥1,3× к предыдущим 7 дням.',
'Средний темп продаж':'Продажи за 7 дней 0,5–1,3× к предыдущим 7 дням.',
'Низкий темп продаж':'Меньше 0,5× к предыдущим 7 дням, либо нет продаж 6+ дней, либо за 7 дней 0 билетов.',
'не в продаже':'Нет ценовых групп с тарифом или места не выведены; есть только пригласительные.'}
for k_,v_ in TIPS.items():
    out=_re.sub(r'<div class=c>(<div class=n[^>]*>[^<]*</div><div class=s>'+_re.escape(k_)+'</div>)',lambda m_:'<div class=c data-tip="'+v_+'">'+m_.group(1),out)
out=out.replace('<div class=per>','<div class=per data-tip="Сравнение двух последних выгрузок БС. Новые билеты — те, которых не было в прошлой выгрузке. Время — по Москве.">',1)
out=out.replace('<h3>Лидеры периода','<h3 data-tip="Мероприятия с наибольшей выручкой за период между выгрузками; справа: +билетов · выручка.">Лидеры периода',1)
out=out.replace('<h3>Замедлились','<h3 data-tip="Разница билетов за последние 7 дней и предыдущие 7 дней (меньше — хуже). Учитываются мероприятия, у которых в предыдущие 7 дней было 10 и больше билетов.">Замедлились',1)
out=out.replace('<h3>Требуют внимания','<h3 data-tip="Мероприятия со статусом «Стоит», «Замедление», «Внимание» или «Нет продаж»; первыми — ближайшие по дате концерта. «7 дн.: N (было M)» — продажи за 7 дней и за предыдущие 7.">Требуют внимания',1)
open('portfolio_map.html','w').write(out);print('ok',len(raw),'в продаже',len(D2),'не в продаже',len(off))
