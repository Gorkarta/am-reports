import pandas as pd,sys
P=sys.argv[1];D='cur/';Pv='prev/'
cols=['id','performance_id','order_id','seat_id','price','is_invite','deleted','created_at']
t=pd.read_csv(D+'tickets.csv',dtype=str,usecols=cols);tp=pd.read_csv(Pv+'tickets.csv',dtype=str,usecols=['id'])
o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['id','status','viewer_id','sold_at'])
se=pd.read_csv(D+'seats.csv',dtype=str,usecols=['id','sector_id','row','num']) if True else None
sc=pd.read_csv(D+'sectors.csv',dtype=str,usecols=['id','name'])
t=t[(t.performance_id==P)&(t.is_invite!='t')&(t.deleted!='t')&~t.id.isin(tp.id)].merge(o,left_on='order_id',right_on='id',suffixes=('','_o'))
t=t[t.status.isin(['10','15'])&~t.viewer_id.isin(['2608','10'])]
t=t.merge(se.rename(columns={'id':'seat_id'}),on='seat_id',how='left').merge(sc.rename(columns={'id':'sector_id','name':'sec'}),on='sector_id',how='left')
t['src']=t.viewer_id.map({'19':'ЯАфиша','38':'Кассир.ру'}).fillna('LA')
t['ts']=pd.to_datetime(t.created_at,format='mixed',utc=True)+pd.Timedelta(hours=3);t['price']=t.price.astype(float)
for oid,g in t.groupby('order_id'):
    parts=[]
    for (sec,pr),x in g.groupby(['sec','price']):
        parts.append(f"{sec} р{','.join(sorted(set(x.row.dropna())))} м{','.join(sorted(x.num.astype(str)))} {len(x)}×{int(pr)}")
    print(oid,g.src.iloc[0],len(g),int(g.price.sum()),g.ts.min().strftime('%d.%m %H:%M'),'|',' ; '.join(parts))
print(t.groupby('src').agg(o=('order_id','nunique'),n=('price','size'),r=('price','sum')))
print(t.groupby('sec').agg(n=('price','size'),r=('price','sum')))
