import json,html
D=[e for e in json.load(open('pf_data.json')) if e['id']!='58']
for e in D: e['name']=e['name'].replace('Николай Басков. Юбилейное шоу','Н. Басков').replace('Музыкальная премия СуперЛайкШоу СТС Kids','СуперЛайк СТС Kids')+' · '+e['start'][8:10]+'.'+e['start'][5:7] if e['name'].startswith(('Николай','Сергей','Идеальный')) else e['name']
def st(e):
    if e['sold_p']==0: return ('Не открыто','mute') if e['cap']==0 else ('Нет продаж','crit')
    if e['since_last'] is not None and e['since_last']>=6: return ('Стоит','crit')
    if e['pw7']>=10 and e['w7']<0.5*e['pw7']: return ('Замедление','warn')
    if e['w7']>=10 and e['w7']>1.3*e['pw7']: return ('Ускорение','good')
    if e['days_left']<=30 and e['w7']<20: return ('Внимание','warn')
    return ('Норма','ok')
for e in D: e['st'],e['cls']=st(e)
tot=sum(e['sold'] for e in D); rev=sum(e['rev'] for e in D)
nn=sum(e['new_n'] for e in D); nr=sum(e['new_r'] for e in D)
cnt=lambda s:sum(1 for e in D if e['st']==s)
f=lambda x:f"{x:,.0f}".replace(',',' ')
act=[e for e in D if e['sold_p']>0]
lead=sorted(act,key=lambda e:-e['new_r'])[:5]
def bars(L,key,fmt,c):
    m=max(key(e) for e in L) or 1;o=''
    for e in L: o+=f'<div class=br><span class=l>{html.escape(e["name"][:30])}</span><span class=t><i style="width:{max(2,key(e)/m*100):.0f}%;background:{c}"></i></span><span class=v>{fmt(e)}</span></div>'
    return o
leaders=bars(lead,lambda e:e['new_r'],lambda e:f"+{e['new_n']} · {e['new_r']/1e6:.2f} млн",'#34d399')
prob=[e for e in D if e['cls'] in('crit','warn') and e['st']!='Не открыто']
prob=sorted(prob,key=lambda e:e['days_left'])
slow=sorted([e for e in act if e['pw7']>=10],key=lambda e:(e['w7']-e['pw7']))[:5]
slowb=''.join(f'<div class=br><span class=l>{html.escape(e["name"][:30])}</span><span class=t><i style="width:{min(100,abs(e["w7"]-e["pw7"])/max(1,max(abs(x["w7"]-x["pw7"]) for x in slow))*100):.0f}%;background:#ff8a5c"></i></span><span class=v>{e["w7"]-e["pw7"]:+d}</span></div>' for e in slow)
out=''
