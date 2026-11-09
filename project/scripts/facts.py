import pandas as pd,json,sys
# Источник заказа = канал продаж билета (Инструкция, п. 4.16, с 09.11.2026); viewer 19 / 38 — аккаунты ЯАфиши / Кассир.ру
CH=[('яндекс','ЯАфиша'),('кассир.ру','Кассир.ру'),('livearena','LA'),('организатор','Сайт организатора'),('концерт','Концерт.ру'),('афиша','Афиша.ру'),('red kassa','Red Kassa'),('редкасса','Red Kassa')]
def chan(v,name):
    if v in ('19','38'):return {'19':'ЯАфиша','38':'Кассир.ру'}[v]
    n=name.lower() if isinstance(name,str) else ''
    for k,l in CH:
        if k in n:return l
    return name if n else 'LA'
P=sys.argv[1]
def ld(D):
    t=pd.read_csv(D+'tickets.csv',dtype=str,usecols=['id','order_id','seat_id','performance_id','price','deleted','is_invite','created_at','updated_at','sale_channel_id'])
    o=pd.read_csv(D+'orders.csv',dtype=str,usecols=['id','status','viewer_id','sold_at'])
    t=t[t.performance_id==P].merge(o,left_on='order_id',right_on='id',how='left',suffixes=('','_o'));return t
A=ld('prev/');B=ld('cur/')
def ret(t):return t[(t.deleted=='t')&(t.is_invite!='t')&t.sold_at.notna()]
def inv(t):return t[(t.is_invite=='t')&(t.deleted!='t')]
print('returns prev',len(ret(A)),'cur',len(ret(B)),'new',len(set(ret(B).id)-set(ret(A).id)),'sum new ret price',pd.to_numeric(ret(B)[~ret(B).id.isin(ret(A).id)].price).sum())
print('inv prev',len(inv(A)),'cur',len(inv(B)))
# annulled paid w/o refund? status -10
sold=lambda t:t[(t.deleted!='t')&(t.is_invite!='t')&t.status.isin(['10','15'])&~t.viewer_id.isin(['2608','10'])]
a,b=sold(A),sold(B)
print('sold prev',len(a),'cur',len(b))
n=b[~b.id.isin(a.id)].copy();n['price']=n.price.astype(float)
chn=pd.read_csv('cur/sale_channels.csv',dtype=str,usecols=['id','name']).rename(columns={'id':'sale_channel_id','name':'chname'})
n=n.merge(chn,on='sale_channel_id',how='left')
n['src']=[chan(v,c) for v,c in zip(n.viewer_id,n.chname)]
g=n.groupby('order_id').agg(src=('src','first'),n=('price','size'),r=('price','sum'))
print('orders',len(g),'avg order',g.r.mean(),'n',len(n))
print(g.groupby('src').agg(orders=('n','size'),t=('n','sum'),r=('r','sum')))
print('large (> avg):');print(g[g.r>g.r.mean()].sort_values('r',ascending=False).head(10))
gone=a[~a.id.isin(b.id)];print('tickets gone from sold',len(gone))
# gone: reason
print(gone.merge(B[['id','deleted','status','sold_at']],on='id',how='left',suffixes=('','_b'))[['id','price','deleted_b','status_b','sold_at_b']].head(20))
