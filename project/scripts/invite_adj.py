import sys,os,json,pandas as pd
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from avail import M
prev,cur,P=sys.argv[1],sys.argv[2],str(sys.argv[3]);asof=sys.argv[4] if len(sys.argv)>4 else '2000-01-01'
R=lambda D:pd.read_csv(D+'tickets.csv',dtype=str,usecols=['id','seat_id','performance_id','is_invite','deleted','created_at'])
def inv(D):
    t=R(D);return t[(t.performance_id==P)&(t.is_invite=='t')&(t.deleted!='t')]
ic,ip=inv(cur),inv(prev)
new=ic[~ic.id.isin(ip.id)]
rows=[];adj_n=adj_r=0
if len(new):
    g=M(prev,P,asof)['g']
    pr=g.set_index('seat_id')['p'] if 'p' in g else pd.Series(dtype=float)
    pr=pr[~pr.index.duplicated()]
    for _,r in new.iterrows():
        p=pr.get(r.seat_id)
        ok=p is not None and pd.notna(p) and float(p)>0
        rows.append(dict(ticket=r.id,seat=r.seat_id,created=r.created_at,price=float(p) if ok else None,corrects=bool(ok)))
        if ok:adj_n+=1;adj_r+=float(p)
print(json.dumps(dict(perf=P,n_new=len(new),adj_n=adj_n,adj_r=adj_r,rows=rows),ensure_ascii=False,indent=1))
