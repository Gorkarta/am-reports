import pandas as pd, numpy as np, json, re, sys
CUR='cur/'; PRE='prev/'  # папки с распакованными выгрузками рядом со скриптами
# python3 mk_pf.py 'ГГГГ-ММ-ДД ЧЧ:ММ' (выгрузка cur) 'ГГГГ-ММ-ДД ЧЧ:ММ' (выгрузка prev)
EXPORT_CUR=pd.Timestamp(sys.argv[1]); EXPORT_PRE=pd.Timestamp(sys.argv[2])
TEST={'5','10','11','12','16','18'}
import os
DEC=json.load(open('exclusions.json',encoding='utf-8')) if os.path.exists('exclusions.json') else {}  # решения владельца: id -> {"решение":"исключить|оставить","дата","причина"}
TEST|={k for k,v in DEC.items() if v.get('решение')=='исключить'}
def msk(s):
  x=pd.to_datetime(s,format='mixed',utc=True)+pd.Timedelta(hours=3)
  return x.dt.tz_localize(None) if hasattr(x,'dt') else x.tz_localize(None)
def load(D):
  p=pd.read_csv(D+'performances.csv',dtype=str); s=pd.read_csv(D+'shows.csv',dtype=str,usecols=['id','name'])
  p=p.merge(s.rename(columns={'id':'show_id','name':'show'}),on='show_id',how='left'); p['start']=msk(p.start_at)
  t=pd.read_csv(D+'tickets.csv',dtype=str,usecols=['id','order_id','seat_id','performance_id','price','deleted','is_invite','created_at'])
  o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['id','status','sold_at','viewer_id'])
  inv=t[(t.is_invite=='t')&(t.deleted!='t')].groupby('performance_id').size()
  t=t.merge(o,left_on='order_id',right_on='id',suffixes=('','_o'))
  t=t[(t.deleted!='t')&(t.is_invite!='t')&t.sold_at.notna()&~t.viewer_id.isin(['2608','10'])].copy()
  t['price']=t.price.astype(float); t['ts']=msk(t.created_at); t['d']=t.ts.dt.strftime('%Y-%m-%d')
  tg=pd.read_csv(D+'ticket_groups.csv',dtype=str,usecols=['id','performance_id','created_at'])
  tr=pd.read_csv(D+'tariffs.csv',dtype=str); deft=tr[tr.is_default=='t'][['id','performance_id']]
  tt=pd.read_csv(D+'tariff_ticket_groups.csv',dtype=str).merge(deft,left_on='tariff_id',right_on='id',suffixes=('','_t'))
  price=tt.drop_duplicates(['performance_id','ticket_group_id']).set_index(['performance_id','ticket_group_id']).price.astype(float)
  gt=pd.read_csv(D+'ticket_group_tickets.csv',dtype=str).merge(tg[['id','performance_id']],left_on='ticket_group_id',right_on='id',suffixes=('','_g'))
  se=pd.read_csv(D+'seats.csv',dtype=str,usecols=['id','limit']); se['lim']=pd.to_numeric(se['limit'],errors='coerce').fillna(0)
  gt=gt.merge(se,left_on='seat_id',right_on='id',suffixes=('','_s')); gt['n']=gt.lim.where(gt.lim>1,1)
  gt['p']=[price.get((a,b),np.nan) for a,b in zip(gt.performance_id,gt.ticket_group_id)]
  return dict(p=p,t=t,gt=gt,inv=inv,ngroups=tg.groupby('performance_id').size())
A=load(PRE); B=load(CUR)
p=B['p']; p=p[(p.start>=EXPORT_CUR)&~p.id.isin(TEST)&~p.show.str.contains('тест',case=False,na=False)].copy()
rows=[]
days=[(EXPORT_CUR.normalize()-pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(13,-1,-1)]
d7=[(EXPORT_CUR.normalize()-pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6,-1,-1)]
dp7=[(EXPORT_CUR.normalize()-pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(13,6,-1)]
for r in p.itertuples():
  pid=r.id; t=B['t'][B['t'].performance_id==pid]; ta=A['t'][A['t'].performance_id==pid]
  gt=B['gt'][(B['gt'].performance_id==pid)]; gta=A['gt'][(A['gt'].performance_id==pid)]
  ins=gt[gt.in_sale=='t']; insa=gta[gta.in_sale=='t']
  new=t[~t.id.isin(ta.id)]
  by=t.groupby('d').size()
  ser=[int(by.get(d,0)) for d in days]
  w7=int(sum(by.get(d,0) for d in d7)); pw7=int(sum(by.get(d,0) for d in dp7))
  last=t.ts.max() if len(t) else None
  a=insa.drop_duplicates('seat_id').set_index('seat_id').p; b=ins.drop_duplicates('seat_id').set_index('seat_id').p
  common=a.index.intersection(b.index); ch=[(x,y) for x,y in zip(a[common],b[common]) if x==x and y==y and abs(x-y)>0.5]
  up=sum(1 for x,y in ch if y>x); dn=sum(1 for x,y in ch if y<x)
  pct=(np.mean([y/x-1 for x,y in ch if x>0])*100) if ch else 0
  added=len(b.index.difference(a.index)); removed=len(a.index.difference(b.index))
  rows.append(dict(id=pid,name=r.show,start=r.start.strftime('%Y-%m-%d %H:%M'),days_left=int((r.start.normalize()-EXPORT_CUR.normalize()).days),
    created=str(pd.to_datetime(r.created_at,utc=True)+pd.Timedelta(hours=3))[:10],sold=int(len(t))+int(B['inv'].get(pid,0)),sold_p=int(len(t)),rev=float(t.price.sum()),avg=float(t.price.mean()) if len(t) else 0,
    new_n=int(len(new))+int(B['inv'].get(pid,0))-int(A['inv'].get(pid,0))-int(len(ta[~ta.id.isin(t.id)])),new_r=float(new.price.sum())-float(ta[~ta.id.isin(t.id)].price.sum()),w7=w7,pw7=pw7,series=ser,last=str(last)[:16] if last is not None else None,
    since_last=(round((EXPORT_CUR-last).total_seconds()/86400,1) if last is not None else None),
    cap=int(ins.drop_duplicates('seat_id').n.sum()),inv=int(B['inv'].get(pid,0)),
    chg=dict(up=up,dn=dn,pct=round(float(pct),1),added=int(added),removed=int(removed),newgroups=int(B['ngroups'].get(pid,0)-A['ngroups'].get(pid,0)))))
# --- Жёсткая проверка подозрительных мероприятий (Инструкция, п. 9.2.1): без ответа владельца дашборд не строится ---
susp=[]
for r in rows:
    if r['id'] in DEC: continue
    why=[]
    sp,inv,avg,sl=r['sold_p'],r['inv'],r['avg'],r['since_last']
    if 1<=sp<=20 and inv>=9*sp and (sl is None or sl>30) and avg>0:
        oth=[x['avg'] for x in rows if x['name']==r['name'] and x['id']!=r['id'] and x['sold_p']>20 and x['avg']>0]
        if oth and avg>3*(sum(oth)/len(oth)): why.append(f"{sp} оплаченных по ср. {avg:,.0f} ₽ (у остальных сеансов артиста ≈{sum(oth)/len(oth):,.0f} ₽), пригласительных {inv}, продаж не было {sl if sl is not None else 'давно'} дн.".replace(',',' '))
    d=r['start'][:10]
    if sp<=20 and any(x['id']!=r['id'] and x['name']==r['name'] and x['start'][:10]==d and x['sold_p']>20 for x in rows): why.append('второй сеанс артиста в тот же день при малых продажах')
    if why: susp.append((r['id'],r['name'],r['start'][:10],'; '.join(why)))
if susp:
    print('СТОП: подозрительные мероприятия — нужен ответ владельца, дашборд не построен.')
    for i,n,d,w in susp: print(f'  id {i} «{n}» {d}: {w}')
    print('Ответ внести в exclusions.json: {"<id>": {"решение":"исключить|оставить","дата":"ДД.ММ.ГГГГ","причина":"..."}}')
    sys.exit(2)
json.dump(rows,open('pf_data.json','w'),ensure_ascii=False,indent=0)
json.dump(dict(cur=str(EXPORT_CUR)[:16],prev=str(EXPORT_PRE)[:16],last_cur=str(B['t'].ts.max())[:16],last_prev=str(A['t'].ts.max())[:16]),open('pf_meta.json','w'))
df=pd.DataFrame(rows); pd.set_option('display.width',250,'display.max_colwidth',34)
print(df.sort_values('start')[['id','name','start','days_left','sold','rev','new_n','w7','pw7','since_last','cap']].to_string())
print(len(df),df.sold.sum(),df.rev.sum(),df.new_n.sum(),df.new_r.sum())
