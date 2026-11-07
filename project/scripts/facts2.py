import pandas as pd,sys,json
def load(D,P):
    t=pd.read_csv(D+'tickets.csv',dtype=str);o=pd.read_csv(D+'orders.csv',dtype=str)
    t=t[t.performance_id==P].merge(o[['id','sold_at','status','viewer_id']].rename(columns={'id':'order_id'}),on='order_id',how='left')
    return t
for P in ('85','78','83','57'):
    out={}
    for nm,D in (('prev','prev/'),('cur','cur/')):
        t=load(D,P)
        ret=t[(t.deleted=='t')&t.sold_at.notna()&(t.is_invite!='t')]
        inv=t[(t.is_invite=='t')&(t.deleted!='t')]
        out[nm]=dict(ret=len(ret),ret_r=ret.price.astype(float).sum(),inv=len(inv),ids=set(ret.id),invids=set(inv.id))
    p,c=out['prev'],out['cur']
    nr=c['ids']-p['ids'];ni=c['invids']-p['invids']
    t=load('cur/',P)
    print(P,'ret',p['ret'],'->',c['ret'],'new ret',len(nr),t[t.id.isin(nr)].price.astype(float).sum(),'inv',p['inv'],'->',c['inv'],'new inv',len(ni),'lost inv',len(p['invids']-c['invids']))
