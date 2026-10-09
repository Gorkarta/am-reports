"""Генератор «Сводки»: python3 svodka_gen.py cfg.json"""
import json,sys,re,math,os,asyncio,hashlib
import pandas as pd,numpy as np
from scipy.spatial import ConvexHull
from playwright.async_api import async_playwright
C=json.load(open(sys.argv[1]));PRE=C['prev'];CUR=C['cur'];PERF=str(C.get('perf',85))
d=json.load(open(C['data']));dp=json.load(open(C['prev_data']))
SRC={'19':('ЯАфиша','#ffcc00'),'38':('Кассир.ру','#2dd4bf')}
def load(D):
    t=pd.read_csv(D+'tickets.csv',dtype=str,usecols=['id','order_id','seat_id','performance_id','price','deleted','is_invite','refunded_at','created_at'])
    o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['id','status','viewer_id'])
    t=t[(t.performance_id==PERF)&(t.deleted!='t')&(t.is_invite!='t')].merge(o,left_on='order_id',right_on='id',suffixes=('','_o'))
    t=t[~t.viewer_id.isin(['2608','10'])&t.status.isin(['10','15'])].copy()
    t['price']=t.price.astype(float);t['seat_id']=t.seat_id.astype(int);return t
def refunds(D):
    t=pd.read_csv(D+'tickets.csv',dtype=str,usecols=['id','order_id','seat_id','performance_id','price','deleted','is_invite','created_at'])
    o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['id','sold_at'])
    t=t.merge(o,left_on='order_id',right_on='id',suffixes=('','_o'))
    return t[(t.performance_id==PERF)&(t.deleted=='t')&(t.is_invite!='t')&t.sold_at.notna()].copy()
A=load(PRE);B=load(CUR);N=B[~B.id.isin(A.id)].copy()
seats=pd.read_csv(CUR+'seats.csv',dtype=str,usecols=['id','sector_id','row','num']);sec=pd.read_csv(CUR+'sectors.csv',dtype=str,usecols=['id','name']).rename(columns={'id':'sid','name':'sname'})
seats['id']=seats.id.astype(int)
def enrich(t):
    t=t.merge(seats,left_on='seat_id',right_on='id',suffixes=('','_s')).merge(sec,left_on='sector_id',right_on='sid')
    t['ts']=pd.to_datetime(t.created_at,format='mixed',utc=True)+pd.Timedelta(hours=3)
    t['src']=t.viewer_id.map(lambda e:SRC.get(e,('LA','#f9423a'))[0]);t['col']=t.viewer_id.map(lambda e:SRC.get(e,('','#f9423a'))[1])
    return t
N=enrich(N)
perf=pd.read_csv(CUR+'performances.csv',dtype=str,usecols=['id','hall_schema_id']);hs=perf[perf.id==PERF].hall_schema_id.iloc[0]
HK={'92':'89'}.get(str(hs),str(hs))
b=pd.read_csv(CUR+'hall_schema_bindings.csv',usecols=['hall_schema_id','seat_id','x','y']);b=b[b.hall_schema_id==int(hs)]
m=b.merge(seats,left_on='seat_id',right_on='id').merge(sec,left_on='sector_id',right_on='sid')
m=m[~((m.x==0)&(m.y==0))&~m.sname.str.startswith('Ложа')].copy()
def zone(n):
    if n=='Танцпол':return 'Танцпол'
    if n=='Партер':return 'Партер'
    if n.startswith('Фан'):return 'Фан-зона'
    if n.startswith('Ложа'):return 'Ложи'
    if n.startswith(('Лаунж','Премиум')):return 'Лаунж и боксы'
    if n.startswith('Балкон'):return 'Балконы'
    if n.startswith('ММГН'):return 'Секторы 100'
    return 'Секторы 100' if int(re.search(r'\d+',n).group())<200 else 'Секторы 300'
m['zone']=m.sname.map(zone)
FANZ={'84':[(7300,13000),(11900,13000),(11900,16000),(7300,16000)]}
DANCE={'84':[(7300,10200),(11900,10200),(11900,12600),(7300,12600)],'78':[(7300,10200),(11900,10200),(11900,12600),(7300,12600)],'89':[(8300,14500),(10900,14500),(10900,16250),(8300,16250)],'48':[(7571,10000),(11643,10000),(11643,14034),(7571,14034)]}
if HK=='78':
    dm=m.sname=='Танцпол'
    m=m[~dm].copy()
ZC={'Фан-зона':'#ffb238','Ложи':'#a29cb3','Танцпол':'#ff6a4d','Партер':'#8b5cf6','Лаунж и боксы':'#2dd4bf','Секторы 100':'#5b8def','Балконы':'#34d399','Секторы 300':'#ff4fa3'}
def hull(pts,pad=120):
    a=np.array(pts);ang=np.linspace(0,2*np.pi,9)[:-1];q=np.vstack([a+[pad*np.cos(t),pad*np.sin(t)] for t in ang]);return q[ConvexHull(q).vertices]
H={}
for n,g in m.groupby('sname'):
    H[n]=np.array(FANZ[HK],float) if n=='Фан-зона' else hull(g[['x','y']].values)
if HK in ('78','84','89','48') :
    H['Танцпол']=np.array(DANCE.get(HK,DANCE['89']),float)
zone_of=m.drop_duplicates('sname').set_index('sname').zone.to_dict();zone_of['Танцпол']='Танцпол'
soldA=set(A.seat_id)
Nm=N.merge(m[['seat_id','x','y']],on='seat_id',how='left')
dmask=Nm.sname=='Танцпол'
if dmask.any() and HK=='78':
    poly=DANCE.get(HK,DANCE['89']);x0=min(p[0] for p in poly);x1=max(p[0] for p in poly);y0=min(p[1] for p in poly);y1=max(p[1] for p in poly)
    def jit(oid,k):
        h=int(hashlib.md5((oid+k).encode()).hexdigest()[:8],16)/0xffffffff;return h
    Nm.loc[dmask,'x']=[x0+400+(x1-x0-800)*jit(o,'x') for o in Nm.loc[dmask,'order_id']]
    Nm.loc[dmask,'y']=[y0+400+(y1-y0-800)*jit(o,'y') for o in Nm.loc[dmask,'order_id']]
Nm=Nm.dropna(subset=['x','y'])
if len(Nm):
    orders=Nm.groupby('order_id').agg(src=('src','first'),col=('col','first'),n=('price','size'),r=('price','sum'),x=('x','mean'),y=('y','mean'),ts=('ts','min'),zone=('sname','first')).reset_index()
else:
    orders=pd.DataFrame(columns=['order_id','src','col','n','r','x','y','ts','zone'])
K=8.2*.55
orders['rad']=orders.r.astype(float).pow(.5)*K
orders=orders.sort_values('r',ascending=False).reset_index(drop=True);orders['ox']=orders.x;orders['oy']=orders.y;orders['dir']=0
for i in range(len(orders)):
    for _ in range(12):
        hit=False
        for j in range(i):
            dx=orders.ox[i]-orders.ox[j];dy=orders.oy[i]-orders.oy[j]
            if math.hypot(dx,dy)<(orders.rad[i]+orders.rad[j])*1.75*0.9:
                sgn=1 if (dx>=0) else -1
                orders.loc[i,'ox']=orders.ox[j]+sgn*(orders.rad[i]+orders.rad[j])*1.75*1.0;orders.loc[i,'dir']=sgn;hit=True;break
        if not hit:break
W=364
def svgwrap(inner):return f"<svg viewBox='-100 -200 19900 18500' width='{W}'>{inner}</svg>"
cont="".join(f"<polygon points='{' '.join(f'{x:.0f},{y:.0f}' for x,y in p)}' fill='none' stroke='{ZC[zone_of[n]]}' stroke-width='38' stroke-opacity='.75' stroke-linejoin='round'/>" for n,p in H.items())
dots="".join(f"<circle cx='{r.x}' cy='{r.y}' r='{44 if r.seat_id in soldA else 22}' fill='{'#8a84a3' if r.seat_id in soldA else '#2c2938'}'/>" for r in m.itertuples())
ZL=dict(ZC);ZL['Лаунж']=ZC['Лаунж и боксы']
bub="";lbl=""
fmtk=lambda v:(str(round(v/1000,1)).replace('.0','').replace('.',','))+' тыс.'
circ=[(r.ox,r.oy,r.rad*1.75+60) for r in orders.itertuples()]
placed=[]
def hit(rect,ex=None):
    x0,y0,x1,y1=rect
    for cx,cy,cr in circ:
        if x0-cr<cx<x1+cr and y0-cr<cy<y1+cr and (max(x0,min(cx,x1))-cx)**2+(max(y0,min(cy,y1))-cy)**2<cr*cr:return True
    for p in placed:
        if not(x1<p[0] or x0>p[2] or y1<p[1] or y0>p[3]):return True
    return False
for r in orders.itertuples():
    bub+=f"<circle cx='{r.ox:.0f}' cy='{r.oy:.0f}' r='{r.rad*1.75:.0f}' fill='none' stroke='{r.col}' stroke-width='60' opacity='.6'/><circle cx='{r.ox:.0f}' cy='{r.oy:.0f}' r='{r.rad:.0f}' fill='{r.col}'/>"
for r in orders.sort_values('r',ascending=False).itertuples():
    t=fmtk(r.r);w=len(t)*300;h=520;R=r.rad*1.75+140
    cands=[(r.ox+R,r.oy+190,'start'),(r.ox-R,r.oy+190,'end'),(r.ox,r.oy-R,'middle'),(r.ox,r.oy+R+h,'middle')]
    R2=R*1.9
    cands+= [(r.ox+R2,r.oy+190,'start'),(r.ox-R2,r.oy+190,'end'),(r.ox+R*.6,r.oy-R2,'start'),(r.ox-R*.6,r.oy-R2,'end'),(r.ox+R*.6,r.oy+R2+h,'start'),(r.ox-R*.6,r.oy+R2+h,'end')]
    if r.dir<0:cands=[cands[1],cands[0]]+cands[2:]
    pick=None
    for x,y,a in cands:
        x0=x if a=='start' else (x-w if a=='end' else x-w/2);rect=(x0,y-h,x0+w,y+60)
        if not hit(rect):pick=(x,y,a,rect);break
    if pick is None:
        x,y,a=cands[0];x0=x;rect=(x0,y-h,x0+w,y+60);pick=(x,y,a,rect)
    placed.append(pick[3]);lbl+=f"<text x='{pick[0]:.0f}' y='{pick[1]:.0f}' fill='#fff' font-size='520' font-weight='800' text-anchor='{pick[2]}' font-family='Inter'>{t}</text>"
zl=""
ZPS={'89':{'Танцпол':[(9600,16650)],'Партер':[(9600,12100)],'Секторы 100':[(9600,7700),(9600,9300),(6300,10300),(12900,10300)],'Секторы 300':[(9600,1000)],'Балконы':[(2000,12700),(17300,12700)],'Лаунж':[(3300,16700),(16100,16700)]},
     '84':{'Танцпол':[(9650,12480)],'Фан-зона':[(9650,15700)],'Секторы 100':[(9650,5700)],'Секторы 300':[(9600,900)],'Балконы':[(1300,12900),(17800,12900)],'Лаунж':[(3300,16700),(16100,16700)]},
     '78':{'Танцпол':[(9650,12480)],'Секторы 100':[(9650,5700)],'Секторы 300':[(9600,900)],'Балконы':[(1300,12900),(17800,12900)],'Лаунж':[(3300,16700),(16100,16700)]},
     '48':{'Танцпол':[(9607,12300)],'Секторы 100':[(9600,7700),(9600,8700)],'Секторы 300':[(9600,900)],'Балконы':[(1300,12500),(17800,12500)],'Лаунж':[(3300,16700),(16100,16700)]}}
ZP=ZPS.get(HK,ZPS['89'])
for z,ps in ZP.items():
    for (x,y) in ps:
        w=len(z)*330;rect=(x-w/2,y-500,x+w/2,y+100)
        if z in('Балконы','Лаунж') or not hit(rect):
            zl+=f"<text x='{x}' y='{y}' fill='{ZL[z]}' font-size='480' font-weight='700' text-anchor='middle' font-family='Inter' opacity='.95'>{z}</text>"
            if z not in('Балконы','Лаунж'):break
svg=svgwrap(cont+dots+bub+lbl+zl)
dot=lambda c,t:f"<span><b style='color:{c}'>●</b> {t}</span> "
leg="".join(f"<div style='text-align:center'><svg width='{2*math.sqrt(v)*K*1.75*.0189+6:.0f}' height='{2*math.sqrt(v)*K*1.75*.0189+6:.0f}'><circle cx='50%' cy='50%' r='{math.sqrt(v)*K*1.75*.0189:.1f}' fill='none' stroke='#a29cb3' stroke-width='1.6' opacity='.7'/><circle cx='50%' cy='50%' r='{math.sqrt(v)*K*.0189:.1f}' fill='#a29cb3'/></svg><div style='color:#a29cb3;font-size:10.5px;white-space:nowrap'>{v//1000} тыс. ₽</div></div>" for v in C.get('legend',(4000,10000,16000)))
mapcard=f"<div class=card style='padding:10px;margin-bottom:6px'>{svg}<div class=lg style='margin-top:6px'>{dot('#ffcc00','ЯАфиша')}{dot('#2dd4bf','Кассир')}{dot('#f9423a','LA')}{dot('#8a84a3','продано ранее')}</div><div style='display:flex;gap:16px;align-items:flex-end;margin-top:6px'><div class=lg style='margin:0 0 14px'>Размер точки — сумма заказа (1 точка = 1 заказ):</div>{leg}</div></div>"
pc_=lambda x:(f'{x:.2f}').replace('.',',')
n_=lambda x:f"{int(round(x)):,}".replace(',',' ')
def rng(a):
    a=sorted(int(x) for x in a);r=[];st=p=a[0]
    for x in a[1:]+[None]:
        if x is not None and x==p+1:p=x;continue
        r.append(str(st) if st==p else f"{st}–{p}")
        if x is not None:st=p=x
    return ", ".join(r)
def skey(n):
    mm=re.search(r'\d+',n);return (0 if n=='Танцпол' else 1,int(mm.group()) if mm else 0,n)
ZORD=['Танцпол','Фан-зона','Партер','Ложи','Лаунж и боксы','Секторы 100','Балконы','Секторы 300']
N['zone']=N.sname.map(zone) if len(N) else []
units=[]
for z in ZORD:
    zs=N[N.zone==z] if len(N) else N
    if len(zs)==0:continue
    first=True
    for sn in sorted(zs.sname.unique(),key=skey):
        g=zs[zs.sname==sn];rows=""
        if sn=='Танцпол':
            for p,x in g.groupby('price'):rows+=f"<div class=it><div class=a>Без ряда и номера<div class=sm>{x.ts.min().strftime('%d.%m %H:%M')}</div></div><div class=rt><b>{n_(x.price.sum())} ₽</b><div class=sm>{len(x)} × {n_(p)}</div></div></div>"
        else:
            for (r,p),x in g.assign(rn=g.row.astype(int),nn=g.num.astype(int)).groupby(['rn','price']):
                rows+=f"<div class=it><div class=a><b>Ряд {r}</b> · {'места' if len(x)>1 else 'место'} {rng(x.nn)}<div class=sm>{x.ts.min().strftime('%d.%m %H:%M')}</div></div><div class=rt><b>{n_(x.price.sum())} ₽</b><div class=sm>{len(x)} × {n_(p)}</div></div></div>"
        nrows=rows.count('<div class=it>');title=sn
        html=(f"<div class=sh style='margin:10px 0 5px'>{z}</div>" if first else '')+f"<div class=list style='margin-bottom:8px'><div class=zh>{title} <span>{len(g)} бил. · {n_(g.price.sum())} ₽</span></div>{rows}</div>"
        units.append((z,html,(28 if first else 0)+36+nrows*54+8));first=False
if not units: units.append(('x',"<div class=list><div class=it><div class=a>Новых продаж за период нет</div></div></div>",70))
RA=refunds(PRE);RB=refunds(CUR)
rn=RB[~RB.id.isin(RA.id)].copy();rn['seat_id']=rn.seat_id.astype(int)
rn=rn.merge(seats,left_on='seat_id',right_on='id',suffixes=('','_s')).merge(sec,left_on='sector_id',right_on='sid')
if len(rn):
    parts=[]
    for (sn,r,p),x in rn.assign(rn_=rn.row.astype(int),nn=rn.num.astype(int)).groupby(['sname','rn_','price']):
        if sn=='Танцпол': parts.append(f"танцпол ({len(x)} × {n_(float(p))} ₽)");continue
        parts.append(f"{'сектор ' if sn.isdigit() else ''}{sn}, ряд {r}, {'места' if len(x)>1 else 'место'} {rng(x.nn)} ({len(x)} × {n_(float(p))} ₽)")
    retline=f"Возвраты за период: {len(rn)} {'билета' if 2<=len(rn)<=4 else ('билет' if len(rn)==1 else 'билетов')} — "+"; ".join(parts)+" — в список не входят."
else:retline="Возвратов за период нет."
foot=f"<div class=foot>{C.get('ret_line',retline)} {C.get('inv_line','Пригласительных за период нет.')} Время — по Москве.</div>"
bs_rows="".join(f"<div class=row><div>{a}<div class=sub>{s_}</div></div><div class=r>{r_}</div></div>" for a,s_,r_ in C['sv_bs_rows'])
bs_block=f"<div class=sh>Изменения в БС <span>{C['sv_bs_when']}</span></div><div class=card>{bs_rows}</div>"
T=d['total'];INV=C['inv'];RET=C['ret'];real=T['n']+INV;PN=C.get('plan_n');PR=C.get('plan_r')
sg=lambda x:(('+' if x>=0 else '−') if round(abs(x)*100) else '')+str(round(abs(x)*100))+'%'
cl=lambda x:'bad' if x<0 else ('good' if x>=0.15 else 'warnc')
AU=d['au'];_pv=AU.get('prev',{}).get('avg')
AUCH=('было {} ₽ · <span class={}>{}</span>'.format(n_(_pv),'good' if AU['avg']>_pv else 'bad',('+' if AU['avg']>=_pv else '−')+str(round(abs(AU['avg']/_pv-1)*100,1)).replace('.',',')+'%') if abs(AU['avg']/_pv-1)>=0.0005 else 'без изменений') if (_pv and not C.get('base')) else ''
cap=d['cap'];GT=C.get('GT',7000);GR=C.get('GR',60000000);ART=C.get('artist','Стас Михайлов')
NEED=(GR/GT) if (GR and GT) else None
mln1=lambda v:(f"{v/1e6:.1f}").replace('.',',')+' млн'
mln=lambda v:(f"{v/1e6:.2f}").replace('.',',')+' млн'
hdr=f"""<div class=brand>Аренамастер · Аналитика</div>
<h1 style='font-size:18px'>Сводка продаж — {ART}</h1>
<div class=meta>Мероприятие: {C.get('event_line','')}<br>Выгрузка БС: <b>{C['exp_date']}</b> · последний билет: <b>{C['last_dm_hm']}</b><br>До концерта: <b>{C['days_left']} дн.</b></div>{('<div class=meta style="color:#ffb238;font-weight:600;margin-top:4px">'+C['quota_note']+'</div>') if C.get('quota_note') else ''}"""
if PN:
    k1=f"<div class=k><div class=l>Реализовано билетов</div><div class=v>{n_(real)}</div><div class=s>план-прогноз на сегодня {n_(int(PN+0.5))} · <span class={cl(real/PN-1)}>{sg(real/PN-1)}</span><br><span class=sub>продано {n_(T['n']+RET)} · пригл. {INV}<br>{('возвраты −'+str(RET)) if RET else 'возвратов нет'}</span></div></div>"
    k2=f"<div class=k><div class=l>Выручка</div><div class=v>{mln(T['r'])} ₽</div><div class=s>план-прогноз на сегодня {mln1(PR)} · <span class={cl(T['r']/PR-1)}>{sg(T['r']/PR-1)}</span></div></div>"
else:
    k1=f"<div class=k><div class=l>Реализовано билетов</div><div class=v>{n_(real)}</div><div class=s>плана нет (базовая выгрузка)<br><span class=sub>продано {n_(T['n']+RET)} · пригл. {INV}<br>{('возвраты −'+str(RET)) if RET else 'возвратов нет'}</span></div></div>"
    k2=f"<div class=k><div class=l>Выручка</div><div class=v>{mln(T['r'])} ₽</div><div class=s>цель по выручке не задана</div></div>"
k3=(f"<div class=k><div class=l>Ср. цена продаж</div><div class=v>{n_(T['avg'])} ₽</div><div class=s>нужна {n_(NEED)} · <span class={cl(T['avg']/NEED-1)}>{sg(T['avg']/NEED-1)}</span></div></div>" if NEED else
    f"<div class=k><div class=l>Ср. цена продаж</div><div class=v>{n_(T['avg'])} ₽</div><div class=s>нужная не задана</div></div>")
path=""
MINT=C.get('min_t');MINR=C.get('min_r')
if PN and MINT and MINR and GT and GR:
    import plans_block as PB
    k1,k2=PB.cards(real,int(PN+0.5),T['r'],PR,MINT,MINR,GT,GR,f"продано {n_(T['n']+RET)} · пригл. {INV}<br>"+(('возвраты −'+str(RET)) if RET else 'возвратов нет'))
    path=PB.path(real,T['r'],MINT,MINR,GT,GR)
elif GT and GR:
    path=f"""<div class=card style='margin-top:8px'><div class=t>Путь к цели: {n_(GT)} билетов, {(str(GR//1000000) if GR%1000000==0 else pc_(GR/1e6))} млн ₽</div>
<div class=pb><i style='width:{min(real/GT*100,100):.1f}%;background:#ffb238'></i></div>
<div class=sub>билеты {str(round(real/GT*100,1)).replace('.',',')}% · выручка {str(round(T['r']/GR*100,1)).replace('.',',')}%</div></div>"""
itogo=f"""<div class=sh>Итого на {C['exp_date'][:5]}</div>
<div class=kpis style='margin-top:0'>
{k1}{k2}{k3}
<div class=k><div class=l>Доступно к покупке</div><div class=v>{n_(AU['n'])}</div><div class=s><span style='color:#ffb238;font-weight:600'>ср. цена {n_(AU['avg'])} ₽</span><br><span class=sub>{AUCH}</span></div></div></div>
{path}"""
avg0=dp['total']['avg'];avg1=T['avg']
retrev=rn.price.astype(float).sum() if len(rn) else 0
revsub=(f"возвраты −{n_(retrev)} ₽ ({len(rn)} бил.)" if len(rn) else "₽")
chg=f"""<div class=sh style='margin-top:0'>Что изменилось <span>{C['period_sv']}</span></div>
<div class=kpis style='margin-top:0;grid-template-columns:1fr 1fr 1fr'>
<div class=k style='padding:9px'><div class=l>Билетов</div><div class=v style='font-size:18px'>+{len(N)}</div><div class=s>{orders.shape[0]} заказов</div></div>
<div class=k style='padding:9px'><div class=l>Выручка</div><div class=v style='font-size:18px'>+{n_(N.price.sum())}</div><div class=s>{revsub}</div></div>
<div class=k style='padding:9px'><div class=l style='letter-spacing:0;white-space:nowrap'>Ср. цена продаж</div><div class=v style='font-size:18px'>{sg(avg1/avg0-1)}</div><div class=s>{n_(avg0)} → {n_(avg1)}</div></div></div>
<div style='height:10px'></div>"""
CAP=690;pages_l=[];cur=[];used=0
for z,html,h in units:
    if used+h>CAP and cur:pages_l.append(''.join(cur));cur=[];used=0
    cur.append(html);used+=h
tail=foot+bs_block;th=40+len(C['sv_bs_rows'])*62+40
if used+th>CAP and cur:pages_l.append(''.join(cur));cur=[];used=0
cur.append(tail);pages_l.append(''.join(cur))
rep_pages=[chg+mapcard]+pages_l
json.dump(rep_pages,open(C['out_pages'],'w'),ensure_ascii=False)
css=open('style_final.txt').read()+'<style>'+open('svodka.css').read()+'</style>'+(__import__('plans_block').CSS if C.get('min_t') else '');F=open('fonts.txt').read()
allhtml=f"{hdr}{itogo}{chg}<div class=sh>Новые продажи <span>+{len(N)} бил. · {n_(N.price.sum())} ₽</span></div>{mapcard}{''.join(u[1] for u in units)}{foot}{bs_block}"
title=C['sv_title']
html=f"<!doctype html><meta charset=utf-8><title>{title}</title>{F}{css}<style>.page{{height:auto;overflow:visible;padding-bottom:26px}}.lg span{{margin-right:9px;white-space:nowrap}}</style><body><div class=page>{allhtml}</div>"
open(C.get('out_html','svodka_out.html'),'w').write(html)
async def go():
    async with async_playwright() as p:
        br=await p.chromium.launch();pg=await br.new_page(viewport={'width':400,'height':820},device_scale_factor=2)
        await pg.goto('file://'+os.getcwd()+'/'+C.get('out_html','svodka_out.html'));await pg.wait_for_timeout(1200)
        await pg.screenshot(path=C.get('out_png','svodka_out.png'),full_page=True)
        h=await pg.evaluate('document.querySelector(".page").getBoundingClientRect().height')
        await pg.add_style_tag(content='@page{size:400px %dpx;margin:0}html,body{height:%dpx;overflow:hidden}'%(h+1,h+1))
        await pg.pdf(path=C['out_pdf'],width='400px',height='%dpx'%(h+1),print_background=True);print('svodka h',h)
        await br.close()
asyncio.run(go())
print('orders',len(orders),'new',len(N),N.price.sum(),'pages_l',len(pages_l))
