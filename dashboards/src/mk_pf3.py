"""Дополняет pf_data.json: вместимость по схеме (без пригласительных), план ₽, витрины. python3 mk_pf3.py"""
import pandas as pd, numpy as np, json
D='cur/'
pf=json.load(open('pf_data.json'))
p=pd.read_csv(D+'performances.csv',dtype=str).set_index('id')
b=pd.read_csv(D+'hall_schema_bindings.csv',dtype=str,usecols=['hall_schema_id','seat_id'])
se=pd.read_csv(D+'seats.csv',dtype=str,usecols=['id','limit']); se['n']=pd.to_numeric(se['limit'],errors='coerce').fillna(0).clip(lower=1)
b=b.merge(se,left_on='seat_id',right_on='id'); capsch=b.groupby('hall_schema_id').n.sum()
tg=pd.read_csv(D+'ticket_groups.csv',dtype=str,usecols=['id','performance_id'])
tr=pd.read_csv(D+'tariffs.csv',dtype=str); dt=tr[tr.is_default=='t'][['id','performance_id']]
tt=pd.read_csv(D+'tariff_ticket_groups.csv',dtype=str).merge(dt,left_on='tariff_id',right_on='id',suffixes=('','_t'))
pr=tt.drop_duplicates(['performance_id','ticket_group_id']).set_index(['performance_id','ticket_group_id']).price.astype(float)
gt=pd.read_csv(D+'ticket_group_tickets.csv',dtype=str).merge(tg,left_on='ticket_group_id',right_on='id',suffixes=('','_g'))
gt=gt.merge(se,left_on='seat_id',right_on='id',suffixes=('','_s'))
gt['p']=[pr.get((a,c),np.nan) for a,c in zip(gt.performance_id,gt.ticket_group_id)]
t=pd.read_csv(D+'tickets.csv',dtype=str,usecols=['seat_id','performance_id','deleted','is_invite','order_id'])
o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['id','sold_at'])
t=t.merge(o,left_on='order_id',right_on='id'); t=t[(t.deleted!='t')&(t.is_invite!='t')&t.sold_at.notna()]
sold=set(zip(t.performance_id,t.seat_id))
ch=pd.read_csv(D+'sale_channels.csv',dtype=str); ch=ch[ch.published=='t']
def vit(n):
    n=n.lower()
    for k,v in [('livearena','LA'),('widget','виджет'),('яндекс','Яндекс'),('кассир','Кассир'),('red kassa','Редкасса'),('redkassa','Редкасса'),('концерт','Концерт'),('афиша.ру','Афиша'),('м.видео','М.Видео'),('vk','VK'),('организатора','Орг. сайт')]:
        if k in n: return v
    return None
GOAL={'85':(7000,60e6),'83':(10857,60e6),'78':(747,2.3e6)}  # цели из карточек; Жара 78 — квота
for e in pf:
    pid=e['id']; sch=p.loc[pid,'hall_schema_id']
    e['cap_sch']=int(capsch.get(sch,0))
    g=gt[(gt.performance_id==pid)&(gt.in_sale=='t')].drop_duplicates('seat_id')
    g=g[np.array([(pid,s) not in sold for s in g.seat_id],dtype=bool)]
    avail_r=float((g.p.fillna(0)*g.n).sum())
    e['plan_t']=GOAL.get(pid,(e['cap_sch'],0))[0]
    e['plan_r']=GOAL[pid][1] if pid in GOAL else 0
    e['plan_src']='цель' if pid in GOAL else '—'
    e['vit']=sorted({v for v in (vit(n) for n in ch[ch.performance_id==pid].name) if v},key=lambda x:(x!='LA',x))
    s=e['series']; e['d3']=int(sum(s[-4:-1]))+int(s[-1]) if False else int(sum(s[-3:]))
json.dump(pf,open('pf_data.json','w'),ensure_ascii=False,indent=0)
for e in pf:
    if e['sold_p']>0: print(e['id'],e['name'][:28],e['start'][:10],e['sold_p'],e['plan_t'],round(e['rev']/1e6,2),round(e['plan_r']/1e6,2),e['plan_src'],e['w7'],e['pw7'],e['d3'],e['vit'])
