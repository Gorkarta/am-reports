import json, math, sys
C=json.load(open(sys.argv[1]))
d=json.load(open(C['data']))
style=open('style_final.txt').read()+'<style>'+open('svodka.css').read()+'</style>'+__import__('plans_block').CSS; fonts=open('fonts.txt').read()
def n(x): return f"{int(round(x)):,}".replace(',',' ')
def plr(v): return (f"{v/1e6:.1f}".replace('.',',')+' млн ₽') if v>=1e6 else (f"{round(v/1e3):,}".replace(',',' ')+' тыс. ₽')
def pc(x,dec=0): return (f"{x:.{dec}f}").replace('.',',')
def sg(x): return ('+' if x>=0 else '−')+pc(abs(x)*100)+'%'
def cls(x): return 'bad' if x<0 else ('good' if x>=0.15 else 'warnc')
STEPS=[1,1.2,1.5,2,2.5,3,4,5,6,7,8,9,10]
def top(mx):
  mx=max(mx,1e-9); o=10**math.floor(math.log10(mx)); return next(s*o for s in STEPS if s*o>=mx*1.02)
def axisY(ym,L,Wd,ih):
  s=''
  for i in range(6):
    v=ym/5*i; y=10+ih-ih*v/ym; s+=f"<line x1={L} x2={Wd} y1={y} y2={y} stroke='#2a2635'/><text x={L-6} y={y+4} text-anchor=end class=ax>{v:g}</text>"
  return s
def barc(p): return '#34d399' if p>=25 else ('#ffb238' if p>=10 else ('#a29cb3' if p>0 else '#ff5470'))
def zone(s):
  if s=='Танцпол':return 'Танцпол'
  if s=='Партер':return 'Партер'
  if s.startswith('Фан'):return 'Фан-зона'
  if s.startswith('Ложа'):return 'Ложи'
  if s.startswith(('Лаунж','Премиум')):return 'Лаунж и премиум-боксы'
  if s.startswith('Балкон'):return 'Балконы'
  return 'Секторы 100' if s[0]=='1' else 'Секторы 300'
GT,GR=C.get('GT',7000),C.get('GR',60000000); ART=C.get('artist','Стас Михайлов')
NEED=GR/GT
T=d['total']; W=C['weeks']
PLAN_N,PLAN_R=C['plan_n'],C['plan_r']
AU=d['au']['avg']
def wbars(H=170,Wd=364):
  L=34; ih=H-24-12; ym=top(max(max(w[1],w[2]) for w in W)); s=axisY(ym,L,Wd,ih); gw=(Wd-L)/len(W)
  for i,w in enumerate(W):
    bw=min(35,(gw-6)/2); x0=L+i*gw+gw/2-bw-1.5
    for j,(v,c) in enumerate([(w[2],'#5b8def'),(w[1],'#ffb238')]):
      h=ih*v/ym; x=x0+j*(bw+3)
      s+=f"<rect x={x} y={10+ih-h} width={bw} height={h} rx=3 fill='{c}'/><text x={x+bw/2} y={10+ih-h-5} text-anchor=middle class=vl style='font-size:{10 if bw>=30 else 8.5}px'>{n(v)}</text>"
    s+=f"<text x={L+i*gw+gw/2} y={H-4} text-anchor=middle class=ax>{w[5]}</text>"
  if C.get('min_t'):
    pts=[(L+i*gw+gw/2,10+ih-ih*(w[2]*C['min_t']/GT)/ym) for i,w in enumerate(W)]
    s+="<polyline points='"+' '.join(f"{x:.1f},{y:.1f}" for x,y in pts)+"' fill=none stroke='#34d399' stroke-width=2 stroke-dasharray='5 4'/>"+''.join(f"<circle cx={x:.1f} cy={y:.1f} r=3 fill='#34d399'/>" for x,y in pts)
  return f"<svg viewBox='0 0 {Wd} {H}' width=100%>{s}</svg>"
DL=C.get('daily') or d['daily']
def daily(key,k=1,H=190,Wd=364):
  pts=[(r['d'][8:10],r[key]/k) for r in DL]
  L=30; ih=H-24-12; ym=top(max(v for _,v in pts)); s=axisY(ym,L,Wd,ih); gw=(Wd-L)/len(pts)
  for i,(dd,v) in enumerate(pts):
    v=int(v+0.5); h=ih*v/ym; x=L+i*gw+2; w=gw-4; col='#8b5cf6' if i==len(pts)-1 else '#ffb238'
    s+=f"<rect x={x} y={10+ih-h} width={w} height={h} rx=2 fill='{col}'/><text x={x+w/2} y={10+ih-h-4} text-anchor=middle class=vl style='font-size:9.5px'>{v}</text><text x={x+w/2} y={H-4} text-anchor=middle class=ax style='font-size:9.5px'>{dd}</text>"
  return f"<svg viewBox='0 0 {Wd} {H}' width=100%>{s}</svg>"
secs={r['sec']:dict(r,n=int(r['n'])) for r in d['sec'] if r['cap']>0 or r['n']>0}
order=['Танцпол','Фан-зона','Партер','Ложи','Лаунж и премиум-боксы','Секторы 100','Балконы','Секторы 300']
order=[z for z in order if any(zone(k)==z and (v['cap']>0 or v['n']>0) for k,v in secs.items())]
Z={z:dict(cap=0,n=0,r=0) for z in order}
for s_,r in secs.items():
  z=Z[zone(s_)]; z['cap']+=r['cap']; z['n']+=r['n']; z['r']+=r['r']
for z in Z.values(): z['pct']=z['n']/z['cap']*100 if z['cap'] else 0
Wd2,L2,rh2=364,120,30; H2=len(order)*rh2+26; iw2=Wd2-L2-20; tp2=top(max(z['pct'] for z in Z.values())); zs=''
for i in range(6):
  x=L2+iw2*i/5; zs+=f"<line x1={x} x2={x} y1=4 y2={H2-20} stroke='#2a2635'/><text x={x} y={H2-6} text-anchor=middle class=ax>{tp2*i/5:g}%</text>"
for i,zn in enumerate(order):
  z=Z[zn]; y=6+i*rh2; w=iw2*z['pct']/tp2
  zs+=f"<text x={L2-8} y={y+11} text-anchor=end class=ax style='fill:#c7c2d6'>{zn.replace('Лаунж и премиум-боксы','Лаунж и боксы')}</text><rect x={L2} y={y+2} width={w} height=12 rx=2 fill='#ffb238'/><text x={L2} y={y+27} class=vl style='font-weight:500;fill:#c7c2d6'>{pc(z['pct'],1)}% · {z['n']} из {n(z['cap'])}</text>"
def srow(name,prices,cap,nn,r,p1=None):
  p=nn/cap*100 if cap else 0
  extra=f"<div class=sm style='color:#ffcf5c'>продано по {n(r/nn)} ₽ — до изменения цены</div>" if (nn and p1 and abs(r/nn-p1)>1) else ''
  return f"<div class=it><div><div class=a>{name}</div><div class=sm>цена {prices} ₽{(' · выручка '+n(r)+' ₽') if nn else ''}</div>{extra}</div><div class=rt><span class=bar><i style='width:{min(p,100)}%;background:{barc(p)}'></i></span><b>{nn}</b> <span class=sm>из {n(cap)}</span><div class=sm>продано {pc(p)}%</div></div></div>"
blocks=[]
for zn in order:
  z=Z[zn]; hdr=f"<div class=zh>{zn} <span>· {z['n']} из {n(z['cap'])} · {pc(z['pct'],1)}%</span></div>"; rows=[]
  if zn=='Партер':
    for g in d['parter']: rows.append(srow('Группа '+g['name'],n(g['price']),g['cap'],g['n'],g['r'],g['price']))
  else:
    for k,v in sorted([(k,v) for k,v in secs.items() if zone(k)==zn],key=lambda kv:-(kv[1]['n']/kv[1]['cap'] if kv[1]['cap'] else 0)):
      if not v['cap']: continue
      pr=n(v['min']) if v['min']==v['max'] else f"{n(v['min'])}–{n(v['max'])}"
      rows.append(srow(k,pr,v['cap'],v['n'],v['r'],v['min'] if v['min']==v['max'] else None))
    for a_,b_ in C.get('withdrawn',{}).get(zn,[]): rows.append(f"<div class=it><div class=sm>{a_}</div><div class='rt sm'>{b_}</div></div>")
  blocks.append((hdr,rows))
G=d['groups']; AVG=sum(g['sold'] for g in G)/d['cap']*100
NEW={g['id'] for g in d['groups'] if g['created']>=C['new_since']}
gs=[]
for g in G:
  p=g['sold']/g['cap']*100; r=p/AVG if AVG else 0
  if g['id'] in NEW and g['w7']==0 and g['sold']==0: tg=('t-sold','новая')
  elif g['sold']>=g['cap']: tg=('t-sold','распродано')
  elif g['sold']==0: tg=('t-none','нет продаж')
  elif r>=1.5: tg=('t-fast','быстро')
  elif r>=0.67: tg=('t-mid','в среднем')
  else: tg=('t-slow','медленно')
  if g['id'] in NEW and tg[1] not in ('новая',): tg=(tg[0],tg[1]+' · новая')
  was=[x for x in g['prev'] if x!=g['price']]
  wasl=(" <span class=sm style='font-weight:400'>(было "+', '.join(n(x) for x in was)+")</span>") if was else ''
  rr=f"×{pc(r,1)} к среднему" if g['sold'] else "—"
  gs.append(f"<div class=it><div><div class=a>{g['name']}{wasl}<span class='tag {tg[0]}'>{tg[1]}</span></div><div class=sm>цена {n(g['price'])} ₽ · за 7 дней {'+'+str(g['w7']) if g['w7'] else '0'}</div></div><div class=rt><span class=bar><i style='width:{min(p,100)}%;background:{barc(p)}'></i></span><b>{g['sold']}</b> <span class=sm>из {n(g['cap'])}</span><div class=sm>продано {pc(p)}% · {rr}</div></div></div>")
it=''
for zn in ['Партер','Ложи','Лаунж и премиум-боксы','Секторы 100','Балконы','Секторы 300','Танцпол','Фан-зона']:
  rs=[r for r in d['diff'] if r['z']==zn]
  if not rs: continue
  it+=f"<div class=zh>{zn}</div>"
  for r in sorted(rs,key=lambda r:(r['p1'] if r['p1']==r['p1'] and r['p1'] is not None else 0)):
    p0,p1=r['p0'],r['p1']; k=int(r['n']); w='мест' if 11<=k%100<=14 else ('место' if k%10==1 else ('места' if 2<=k%10<=4 else 'мест'))
    if p0 is None or p0!=p0: txt=f"<span class=new>выставлены</span> по {n(p1)} ₽"
    elif p1 is None or p1!=p1: txt=f"<span class=bad>сняты с продажи</span> (было {n(p0)} ₽)"
    else: txt=f"{n(p0)} <span class=arrow>→</span> <b class={'good' if p1>p0 else 'bad'}>{n(p1)} ₽</b>"
    sub=r['secs'].replace('Премиум бокс ','бокс ')
    it+=f"<div class=it><div><div class=a>{k} {w}</div>{'' if sub==zn else '<div class=sm>'+sub+'</div>'}</div><div class=rt>{txt}</div></div>"
def lst(items): return "<div class=list>"+''.join(items)+"</div>"
def bul(items): return "<ul>"+''.join(f"<li>{x}</li>" for x in items)+"</ul>"
def banner(num,title,sub): return f"<div class=sec-lbl>Раздел {num}</div><h2 style='font-size:19px;margin-bottom:4px'>{title}</h2><div class=meta style='margin-bottom:12px'>{sub}</div>"
P={1:[],2:[],3:[]}
def pg(s,b): P[s].append(b)
cap=d['cap']; sold=T['n']; INV=C.get('inv',0); RET=C.get('ret',0); real=sold+INV; RU=d['rules']; OUT=RU['out']; INVO=RU['inv_out']; AV=RU['avail']; WB=RU['wd']+RU['book']; nr=GT-OUT-INVO
import plans_block as PB
MINT,MINR=C.get('min_t'),C.get('min_r')
if MINT:
  KP1,KP2=PB.cards(real,int(round(PLAN_N)),T['r'],PLAN_R,MINT,MINR,GT,GR,f"продано {n(sold+RET)} · пригл. {INV}<br>"+(('возвраты −'+str(RET)) if RET else 'возвратов нет'))
  PATH=PB.path(real,T['r'],MINT,MINR,GT,GR)
pg(1,f"""<div class=brand>Аренамастер · Аналитика</div>
<h1>Отчёт и рекомендации — {ART}</h1>
<div class=meta>Мероприятие: {C.get('event_line')}<br><b>Выгрузка продаж БС: {C['exp_date']}</b><br><b>Версия документа: {C['ver']}</b><br><b>Дата текущей редакции: {C['ed_date']}, время продажи последнего билета в выгрузке {C['last_hm']}</b></div>
<div class=call style='margin-top:10px'><b>Коротко.</b> {C['short']}</div>
<div class=sec-lbl style='margin-top:10px'>Раздел 1</div><h2 style='font-size:19px;margin-bottom:8px'>Продажи</h2>
<div class=kpis style='margin-top:0'>
{KP1}{KP2}
<div class=k><div class=l>Ср. цена продаж</div><div class=v>{n(T['avg'])} ₽</div><div class=s>нужно {n(NEED)} ₽ · <span class={cls(T['avg']/NEED-1)}>{sg(T['avg']/NEED-1)}</span></div></div>
<div class=k><div class=l>Ср. цена в продаже</div><div class=v>{n(AU)} ₽</div><div class=s>нужно {n(NEED)} ₽ · <span class={cls(AU/NEED-1)}>{sg(AU/NEED-1)}</span><br>до концерта {C['days_left']} дн.</div></div></div>
""")
pg(1,f"""{PATH}<div class=card style='margin-top:10px'><div class=t>Билеты: план, выведено, реализовано <span class=sm>(доли — от плана)</span></div>
<svg viewBox='0 0 364 26' width=100%><rect x=0 y=4 width=364 height=18 rx=4 fill='#2a2635'/><rect x=0 y=4 width={364*(OUT+INVO)/GT:.1f} height=18 rx=4 fill='#6b6580'/><rect x=0 y=4 width={364*(real+AV)/GT:.1f} height=18 rx=4 fill='#5b8def'/><rect x=0 y=4 width={364*real/GT:.1f} height=18 rx=4 fill='#8b5cf6'/><rect x=0 y=4 width={364*sold/GT:.1f} height=18 rx=4 fill='#ffb238'/></svg>
<div class=lg><span style='white-space:nowrap;margin-right:10px'><i style="background:#ffb238;margin-left:0"></i>продано {n(sold)}</span><span style='white-space:nowrap;margin-right:10px'><i style="background:#8b5cf6;margin-left:0"></i>пригл. {INV}</span><span style='white-space:nowrap'><i style="background:#5b8def;margin-left:0"></i>доступно к покупке {n(AV)}</span><br>{('<span style="white-space:nowrap;margin-right:10px"><i style="background:#6b6580;margin-left:0"></i>снято / бронь '+n(WB)+'</span>') if WB else ''}<span style='white-space:nowrap'><i style="background:#2a2635;border:1px solid #4a4458;margin-left:0"></i>не выведено {n(nr)}</span></div>
<div style='display:grid;grid-template-columns:1fr 1.15fr 1.15fr .8fr;gap:4px;margin-top:8px;text-align:center'>
<div><div class=sm>План</div><b style='font-size:16px'>{n(GT)}</b></div>
<div><div class=sm>Выведено</div><b style='font-size:16px'>{n(OUT)}</b> <span class=sm>· {pc(OUT/GT*100,1)}%</span></div>
<div><div class=sm>Реализовано</div><b style='font-size:16px'>{n(real)}</b> <span class=sm>· {pc(real/GT*100,1)}%</span></div>
<div><div class=sm>Возвраты</div><b style='font-size:16px'>{RET}</b></div></div></div>""")
def pdev(a,b): return f"<span class={cls(a/b-1)}>{sg(a/b-1)}</span>" if b else '—'
wit=''
for w in W+[['Итого',real,PLAN_N,T['r'],PLAN_R]]:
  if w[4]:
    rv=f"выручка {n(w[3])} ₽ из {plr(w[4])} · {pdev(w[3],w[4])}"+(f"<br>минимум {plr(w[4]*MINR/GR)} · {pdev(w[3],w[4]*MINR/GR)}" if MINT else ''); tv=(f"<div class=sm><span class={cls(w[1]/w[2]-1)}>{sg(w[1]/w[2]-1)}</span></div>"+(f"<div class=sm><span class={cls(w[1]/(w[2]*MINT/GT)-1)}>{sg(w[1]/(w[2]*MINT/GT)-1)}</span> к мин. {n(w[2]*MINT/GT)}</div>" if MINT else '')) if w[2] else ''
  else:
    rv=f"выручка {n(w[3])} ₽ · план за период — 0 ₽"; tv=''
  wit+=f"<div class=it><div><div class=a>{w[0]}</div><div class=sm>{rv}</div></div><div class=rt><b>{w[1]}</b> <span class=sm>из {n(w[2])}</span>{tv}</div></div>"
for _p in json.load(open(C['svodka'])): pg(1,_p)
pg(1,f"""<h3 style='margin-top:0'>{C.get('weeks_title','Темп по неделям')}</h3>
<div class=card><div class=t>{C.get('weeks_cap','Билетов за неделю: факт и план')}</div>{wbars()}<div class=lg><i style="background:#5b8def"></i>План<i style="background:#ffb238"></i>Факт{('<i style="background:#34d399"></i>План-минимум' if MINT else '')}</div></div>
<div class=list style='margin-top:8px'>{wit}</div><div class=foot style='margin-top:8px'>{C['weeks_foot']}</div>""")
pg(1,f"""<h3 style='margin-top:0'>Продажи по дням</h3>
<div class=card><div class=t>Билетов в день, {C['days_caption']}</div>{daily('n')}</div>
<div class=card style="margin-top:10px"><div class=t>Выручка в день, тыс. ₽</div>{daily('r',1000)}<div class=lg><i style="background:#8b5cf6"></i>{C['partial_day']}</div></div>
<div class=foot>{C['clean_foot']}</div>""")
pg(1,f"""<h3 style='margin-top:0'>По зонам зала</h3>
<div class=card><div class=t>Реализация, % мест в продаже</div><svg viewBox='0 0 {Wd2} {H2}' width=100%>{zs}</svg></div>
<div class=foot>Выведено — места групп билетов с назначенным тарифом (танцпол — по лимиту места). Доступно к покупке — выведено, в продаже, в канале продаж, не продано и не забронировано. Цены — текущие тарифы БС; проданные билеты отнесены к текущей группе места. Итого: {n(cap)} мест, {n(sold)} билетов, {n(T['r'])} ₽.</div>""")
PER=13; cur=[]; cnt=0; first=[True]
def flush():
  global cur,cnt
  if cur: pg(1,("<h3 style='margin-top:0'>Продажи по секторам</h3>" if first[0] else "<h3 style='margin-top:0'>Продажи по секторам (продолжение)</h3>")+lst(cur)); first[0]=False
  cur=[]; cnt=0
for hdr,rows in blocks:
  i=0
  while i<len(rows):
    if cnt>=PER-1: flush()
    take=rows[i:i+PER-cnt-1]; cur.append(hdr if i==0 else hdr.replace('</div>',' (продолжение)</div>',1)); cur+=take; cnt+=1+len(take); i+=len(take)
flush()
ch=[gs[:11]]+[gs[k:k+12] for k in range(11,len(gs),12)]
for i,c in enumerate(ch):
  pg(1,("<h3 style='margin-top:0'>Продажи по ценовым группам</h3><div class=meta style='margin:-4px 0 8px'>В среднем по залу продано "+pc(AVG,1)+"% мест в продаже</div>" if i==0 else "<h3 style='margin-top:0'>Продажи по ценовым группам (продолжение)</h3>")+lst(c)+(f"<div class=foot>«×N к среднему» — во сколько раз доля проданных мест группы выше или ниже средней по залу. Метка: быстро — ×1,5 и выше, в среднем — ×0,67–1,5, медленно — ниже ×0,67; «новая» — группа создана после прошлой выгрузки. «(было …)» — цена мест группы в прошлой выгрузке. «За 7 дней» — {C['d7']}.</div>" if i==len(ch)-1 else ''))
N_=d['new']
nl=''.join(f"<div class=it><div><div class=a>{a}</div>{('<div class=sm>'+c+'</div>') if c else ''}</div><div class=rt><b>+{b}</b> <span class=sm>бил.</span></div></div>" for a,b,c in C['new_where']) or "<div class=it><div class=a>Новых продаж нет</div></div>"
EV=C['events']; ES=C.get('ev_split',len(EV))
pg(2,f"""{banner(2,'Новости и изменения',C['period'])}
<div class=stat><div class=k><div class=l>Билетов</div><div class=v>+{N_['n']}</div></div><div class=k><div class=l>Выручка</div><div class=v>+{n(N_['r']/1000)} тыс.</div></div><div class=k><div class=l>Заказов</div><div class=v>{N_['orders']}</div></div></div>
<h3>Где продавалось</h3>{lst([nl])}
<h3>Всплески и события</h3>{bul(EV[:ES])}""")
if EV[ES:]: pg(2,f"""<h3 style='margin-top:0'>Всплески и события (продолжение)</h3>{bul(EV[ES:])}""")
pg(2,f"""<h3 style='margin-top:0'>Переоценка и вывод в продажу</h3><div class=meta style="margin:-4px 0 8px">{C['change_when']}</div>{lst([it or "<div class=it><div class=a>Цены и состав мест в продаже без изменений</div></div>"])}""")
pg(2,f"""<h3 style='margin-top:0'>Что это изменило</h3>{bul(C['changed'])}
<div class=call><b>Без изменений:</b> {C['unchanged']}</div><div class=foot>{C['news_foot']}</div>""")
def upr(rows):
  o=''
  for a,b,sv,c,e in rows:
    nt=("<div class=sm style='color:#c7c2d6'>"+e+"</div>") if e else ''
    o+=f"<div class=it><div><div class=a>{a}</div><div class=sm>продано {b} · сервис: {sv}</div>{nt}</div><div class=rt><span class=new>{c}</span></div></div>"
  return o
RK=C.get('raise_split',5); RC=C.get('raise_chunk',5)
pg(3,f"""{banner(3,'Рекомендации',C.get('rec_sub','Предварительные: до события больше 30 дней'))}
<div class=call style='margin-top:0'><b>Главное.</b> {C['main']}</div><h3>Поднять</h3>{lst([upr(C['raise'][:RK])]) if C['raise'] else bul(C.get('raise_none',['Групп для повышения нет.']))}""")
rest=C['raise'][RK:]
chunks=[rest[i:i+RC] for i in range(0,len(rest),RC)]
for ci,chk in enumerate(chunks):
  pg(3,f"""<h3 style='margin-top:0'>Поднять (продолжение)</h3>{lst([upr(chk)])}"""+(f"<h3>Держать</h3>{bul(C['hold'])}" if (ci==len(chunks)-1 and C.get('hold_with_raise',True)) else ''))
if chunks and C.get('hold_with_raise',True):
  pg(3,f"""<h3 style='margin-top:0'>Снизить</h3>{bul(C['lower'])}<h3>Возможности</h3>{bul(C['opps'])}""")
elif chunks:
  pg(3,f"""<h3 style='margin-top:0'>Держать</h3>{bul(C['hold'])}<h3>Снизить</h3>{bul(C['lower'])}""")
  pg(3,f"""<h3 style='margin-top:0'>Возможности</h3>{bul(C['opps'])}""")
else:
  pg(3,f"""<h3 style='margin-top:0'>Держать</h3>{bul(C['hold'])}<h3>Снизить</h3>{bul(C['lower'])}<h3>Возможности</h3>{bul(C['opps'])}""")
pg(3,f"""<h3 style='margin-top:0'>Слабые места</h3>{bul(C['weak'])}<h3>На что обратить внимание</h3>{bul(C['attn'])}
<div class=foot>Результат — предложение: цены утверждает менеджер и вносит в БС вручную.</div>""")
pg(3,f"""<h3 style='margin-top:0'>Применение методики</h3>{bul(C.get('method',[]))}""")
pages=P[1]+P[2]+P[3]; NN=len(pages)
style=style.replace('</style>','.p1 .k{padding:8px 11px}.p1 .k .v{font-size:19px;margin:2px 0}.p1 h1{font-size:20px;margin:6px 0}.p1 .card{padding:9px 12px}.p1 .call{padding:9px 12px;font-size:12.5px}.p1 .kpis{gap:6px;margin-top:0}</style>')
html=f"<!doctype html><html lang=ru><head><meta charset=utf-8><title>{C['title']}</title>{fonts}{style}</head><body>"+''.join(f"<div class='page{' p1' if i==0 else ''}'>{p}<div class=pn>{i+1} / {NN}</div></div>" for i,p in enumerate(pages))+"</body></html>"
open(C['out'],'w').write(html); print('pages',NN,'avg',AVG)
