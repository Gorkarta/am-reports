import pandas as pd
def zone(s):
  if s=='Танцпол':return 'Танцпол'
  if s=='Партер':return 'Партер'
  if s.startswith('Фан'):return 'Фан-зона'
  if s.startswith('Ложа'):return 'Ложи'
  if s.startswith(('Лаунж','Премиум')):return 'Лаунж и премиум-боксы'
  if s.startswith('Балкон'):return 'Балконы'
  return 'Секторы 100' if s[0]=='1' else 'Секторы 300'
def M(D,P,asof):
  P=str(P);R=lambda n,**k:pd.read_csv(D+n+'.csv',dtype=str,**k)
  perf=R('performances');perf=perf[perf.id==P].iloc[0]
  se=R('seats',usecols=['id','sector_id','limit']);sc=R('sectors',usecols=['id','name'])
  se=se.merge(sc.rename(columns={'id':'sector_id','name':'sec'}),on='sector_id',how='left')
  se['n']=pd.to_numeric(se['limit'],errors='coerce').fillna(0);se['n']=se.n.where(se.n>1,1)
  se=se.set_index('id')
  b=R('hall_schema_bindings');b=b[b.hall_schema_id==perf.hall_schema_id].drop_duplicates('seat_id')
  b=b[b.seat_id.isin(se.index)];plan=se.loc[b.seat_id]
  tg=R('ticket_groups');tg=tg[tg.performance_id==P]
  tr=R('tariffs');deft=tr[(tr.performance_id==P)&(tr.is_default=='t')].id
  tt=R('tariff_ticket_groups');tt=tt[tt.ticket_group_id.isin(tg.id)]
  has_tar=set(tt.ticket_group_id);dt_=tt[tt.tariff_id.isin(deft)].drop_duplicates('ticket_group_id').set_index('ticket_group_id').price.astype(float)
  scs=R('sale_channels');scs=scs[(scs.performance_id==P)&(scs.published=='t')]
  sg=R('sale_channel_ticket_groups');sg_all=sg
  ok=set()
  for c in scs.id:
    rec=sg_all[sg_all.sale_channel_id==c]
    if rec.empty: ok|=set(tg.id)
    else: ok|=set(rec.ticket_group_id)&set(tg.id)
  g=R('ticket_group_tickets');g=g[g.ticket_group_id.isin(tg.id)&g.seat_id.isin(b.seat_id)].drop_duplicates('seat_id')
  g['cg']=g.ticket_group_id;g['tar']=g.cg.isin(has_tar);g['chan']=g.cg.isin(ok);g['ins']=g.in_sale=='t'
  g=g.join(se[['sec','n']],on='seat_id');g['p']=g.cg.map(dt_)
  t=R('tickets');t=t[(t.performance_id==P)&(t.deleted!='t')]
  o=R('orders',usecols=['id','status','sold_at','pay_till','viewer_id']);t=t.merge(o,left_on='order_id',right_on='id',how='left',suffixes=('','_o'))
  inv=t.is_invite=='t';sold=(~inv)&t.sold_at.notna()
  pt=pd.to_datetime(t.pay_till,format='mixed',utc=True,errors='coerce')
  book=(~inv)&t.sold_at.isna()&(t.status=='0')&(pt>pd.Timestamp(asof,tz='UTC'))
  t['kind']='';t.loc[inv,'kind']='inv';t.loc[sold,'kind']='sold';t.loc[book,'kind']='book'
  return dict(perf=perf,plan=plan,g=g,t=t,tg=tg,price=dt_)
