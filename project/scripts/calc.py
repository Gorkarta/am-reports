import pandas as pd, json, sys
import avail
PERF=sys.argv[5] if len(sys.argv)>5 else '85'
def zone(s):
  if s=='Танцпол':return 'Танцпол'
  if s=='Партер':return 'Партер'
  if s.startswith('Фан'):return 'Фан-зона'
  if s.startswith('Ложа'):return 'Ложи'
  if s.startswith(('Лаунж','Премиум')):return 'Лаунж и премиум-боксы'
  if s.startswith('Балкон'):return 'Балконы'
  return 'Секторы 100' if s[0]=='1' else 'Секторы 300'
def load(D):
  tg=pd.read_csv(D+'ticket_groups.csv',dtype=str); tg=tg[tg.performance_id==PERF]
  tr=pd.read_csv(D+'tariffs.csv',dtype=str); deft=tr[(tr.performance_id==PERF)&(tr.is_default=='t')].id
  tt=pd.read_csv(D+'tariff_ticket_groups.csv',dtype=str)
  price=tt[tt.ticket_group_id.isin(tg.id)&tt.tariff_id.isin(deft)].drop_duplicates('ticket_group_id').set_index('ticket_group_id').price.astype(float)
  tgt=pd.read_csv(D+'ticket_group_tickets.csv',dtype=str); tgt=tgt[tgt.ticket_group_id.isin(tg.id)]
  se=pd.read_csv(D+'seats.csv',dtype=str,usecols=['id','sector_id','limit']); sc=pd.read_csv(D+'sectors.csv',dtype=str,usecols=['id','name'])
  se=se.merge(sc.rename(columns={'id':'sector_id','name':'sec'}),on='sector_id'); se['lim']=pd.to_numeric(se['limit'],errors='coerce').fillna(0)
  m=tgt.merge(se,left_on='seat_id',right_on='id'); m['n']=m.lim.where(m.lim>1,1); m['p']=m.ticket_group_id.map(price)
  t=pd.read_csv(D+'tickets.csv',dtype=str); o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['id','status'])
  t=t[(t.performance_id==PERF)&(t.is_invite!='t')&(t.deleted!='t')].merge(o,left_on='order_id',right_on='id',suffixes=('','_o')); t=t[t.status.isin(['10','15'])]
  t['price']=t.price.astype(float); t['ts']=pd.to_datetime(t.created_at,format='mixed',utc=True)+pd.Timedelta(hours=3); t['d']=t.ts.dt.date.astype(str)
  t['cg']=t.seat_id.map(tgt.drop_duplicates('seat_id').set_index('seat_id').ticket_group_id)
  t=t.merge(se[['id','sec']].rename(columns={'id':'seat_id'}),on='seat_id',how='left')
  return dict(tg=tg,price=price,m=m,t=t,rules=rules(D))
def rules(D):
  o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['updated_at']); asof=pd.to_datetime(o.updated_at,format='mixed',utc=True).max().tz_localize(None)
  X=avail.M(D,PERF,asof); g=X['g']; t=X['t']
  used=t[t.kind!=''].groupby('seat_id').size()
  av=g[g.tar&g.chan&g.ins].copy(); av['free']=(av.n-av.seat_id.map(used).fillna(0)).clip(lower=0)
  wd=g[g.tar&~(g.chan&g.ins)].copy(); wd['free']=(wd.n-wd.seat_id.map(used).fillna(0)).clip(lower=0)
  ing=set(g[g.tar].seat_id); tk=t[t.kind!='']
  inv_all=int((tk.kind=='inv').sum()); inv_g=int(((tk.kind=='inv')&tk.seat_id.isin(ing)).sum())
  n=float(av.free.sum()); avg=float((av.p*av.free).sum()/n) if n else 0
  return dict(plan=int(X['plan'].n.sum()),out=int(g[g.tar].n.sum()),avail=int(n),avg=avg,wd=int(wd.free.sum()),book=int((tk.kind=='book').sum()),
    inv_all=inv_all,inv_out=inv_all-inv_g,sold_all=int((tk.kind=='sold').sum()))
def avg_unsold(X):
  r=X['rules']; return dict(avg=r['avg'],n=r['avail'])
def run(prev,cur,d7from):
  A=load(prev); B=load(cur); tg=B['tg'].set_index('id'); m=B['m']; t=B['t']; price=B['price']
  ins=m[m.in_sale=='t']
  mA=A['m']; pA=mA[mA.in_sale=='t'].set_index('seat_id').p
  G=[]
  for gid,g in ins.groupby('ticket_group_id'):
    tk=t[t.cg==gid]
    G.append(dict(id=gid,name=tg.name[gid],price=float(price.get(gid,0)),cap=int(g.n.sum()),sold=len(tk),rev=float(tk.price.sum()),
      w7=int((tk.d>=d7from).sum()),secs=sorted(g.sec.unique().tolist()),created=tg.created_at[gid],
      sold_prices=sorted(set(tk.price.tolist())),prev=sorted(set(float(v) for v in pA.reindex(g.seat_id).dropna().tolist()))))
  AU=avg_unsold(B); AU['prev']=avg_unsold(A)
  G.sort(key=lambda x:(-x['price'],x['name']))
  orphan=t[~t.cg.isin(ins.ticket_group_id)]
  cap=ins.groupby('sec').n.sum(); pr=ins.groupby('sec').p.agg(['min','max']); s=t.groupby('sec').agg(n=('price','size'),r=('price','sum'))
  sec=pd.concat([cap.rename('cap'),s,pr],axis=1).fillna({'n':0,'r':0,'cap':0}).reset_index().rename(columns={'index':'sec'})
  parter=[]
  for gid,g in ins[ins.sec=='Партер'].groupby('ticket_group_id'):
    tk=t[(t.sec=='Партер')&(t.cg==gid)]; parter.append(dict(id=gid,name=tg.name[gid],price=float(price[gid]),cap=int(g.n.sum()),n=len(tk),r=float(tk.price.sum())))
  parter.sort(key=lambda x:-x['price'])
  def sm(M):
    x=M.copy(); x.loc[x.in_sale!='t','p']=None; return x.set_index('seat_id')[['sec','p','n']]
  x=sm(A['m']).join(sm(m),how='outer',lsuffix='0',rsuffix='1'); x['sec']=x.sec1.fillna(x.sec0); x['n']=x.n1.fillna(x.n0)
  ch=x[x.p0.fillna(-1)!=x.p1.fillna(-1)].copy(); ch['z']=ch.sec.map(zone)
  diff=ch.groupby(['z','p0','p1'],dropna=False).agg(n=('n','sum'),secs=('sec',lambda s:', '.join(sorted(s.unique())))).reset_index().to_dict('records')
  tgA=A['tg'].set_index('id'); lastA=A['t'].ts.max()
  newg=[gid for gid in tg.index if gid not in tgA.index]
  upd=tg[pd.to_datetime(tg.updated_at,format='mixed',utc=True)+pd.Timedelta(hours=3)>lastA]
  times=pd.to_datetime(pd.concat([upd.updated_at,tg.loc[newg].created_at]),format='mixed',utc=True)+pd.Timedelta(hours=3)
  nw=t[~t.id.isin(A['t'].id)]
  od=nw.groupby('order_id').agg(n=('price','size'),r=('price','sum'),ts=('ts','min'),secs=('sec',lambda s:', '.join(sorted(s.dropna().unique()))),p=('price',lambda s:', '.join(str(int(v)) for v in sorted(s.unique())))).sort_values('r',ascending=False)
  nz=nw.assign(z=nw.sec.map(zone)).groupby('z').agg(n=('price','size'),r=('price','sum'))
  nsec=nw.groupby('sec').size().sort_values(ascending=False)
  daily=t.groupby('d').agg(n=('price','size'),r=('price','sum'))
  out=dict(au=AU,groups=G,orphan=dict(n=len(orphan),r=float(orphan.price.sum()),secs=orphan.sec.value_counts().to_dict(),grp=orphan.ticket_group_id.map(lambda g: tg.name.get(g,'?')).value_counts().to_dict()),
    sec=sec.to_dict('records'),parter=parter,diff=diff,
    change_window=[str(times.min()),str(times.max())] if len(times) else None,newgroups=[tg.name[g] for g in newg],
    new=dict(n=len(nw),r=float(nw.price.sum()),orders=int(nw.order_id.nunique()),top=od.head(6).reset_index().astype(str).to_dict('records'),zones=nz.reset_index().to_dict('records'),secs=nsec.head(8).to_dict(),
      frm=str(lastA),to=str(t.ts.max())),
    daily=daily.reset_index().to_dict('records'),total=dict(n=len(t),r=float(t.price.sum()),avg=float(t.price.mean()),hall_avg=float(t[t.sec!='Танцпол'].price.mean())),
    cap=int(ins.n.sum()),last=str(t.ts.max()),rules=B['rules'])
  return out
if __name__=='__main__':
  o=run(sys.argv[1],sys.argv[2],sys.argv[3]); json.dump(o,open(sys.argv[4],'w'),ensure_ascii=False,default=str,indent=0)
  print('cap',o['cap'],'total',o['total'],'last',o['last'])
  print('new',o['new']['n'],o['new']['r'],o['new']['orders'])
