# Доступность каналов продаж (основной канал — сайт livearena.ru).
# python3 -I site_check.py --repo <клон bs-reports> --rev <коммит выгрузки> --prev <коммит прошлой выгрузки> --out avail.json
# Читает csv/ прямо из git (git show), ничего в репозитории не меняет.
import csv,subprocess,io,collections,json,argparse,datetime as dt
ap=argparse.ArgumentParser()
for a in('--repo','--rev','--prev','--out'): ap.add_argument(a,required=True)
A=ap.parse_args()
def git(*a): return subprocess.run(['git','-C',A.repo,*a],capture_output=True,text=True,check=True).stdout
def rows(rev,f): return list(csv.DictReader(io.StringIO(git('show',f'{rev}:csv/{f}'))))
def ctime(rev): return dt.datetime.fromisoformat(git('log','-1','--format=%cI',rev).strip()).astimezone(dt.timezone.utc).replace(tzinfo=None)
T=lambda v:v in('t','true','True','1')
def U(s): return dt.datetime.fromisoformat(s[:19]) if s else None
def is_site(n): n=n.lower(); return 'livearena' in n and 'резерв' not in n
def calc(rev,snap):
    perf={r['id']:r for r in rows(rev,'performances.csv')}
    shows={r['id']:r['name'] for r in rows(rev,'shows.csv')}
    tg={r['id']:r for r in rows(rev,'ticket_groups.csv')}
    tar={r['ticket_group_id']:float(r['price'] or 0) for r in rows(rev,'tariff_ticket_groups.csv')}
    lim={r['id']:max(1,int(float(r.get('limit') or 1))) for r in rows(rev,'seats.csv')}
    ch={r['id']:r for r in rows(rev,'sale_channels.csv')}
    scg=collections.defaultdict(set)
    for r in rows(rev,'sale_channel_ticket_groups.csv'): scg[r['sale_channel_id']].add(r['ticket_group_id'])
    o={r['id']:r for r in rows(rev,'orders.csv')}
    busy=collections.Counter(); sold=[]
    for t in rows(rev,'tickets.csv'):
        if T(t['deleted']): continue
        od=o.get(t['order_id'],{}); p=t['performance_id']; s=bool(od.get('sold_at'))
        bk=od.get('status')=='0' and not s and not T(t['is_invite']) and (not od.get('pay_till') or U(od['pay_till'])>snap)
        if T(t['is_invite']) or s or bk: busy[(p,t['seat_id'])]+=1
        if s and not T(t['is_invite']) and od.get('viewer_id') not in('2608','10'):
            c=t['sale_channel_id']; sold.append((p,U(od['sold_at']),c in ch and is_site(ch[c]['name']),c))
    avail=collections.defaultdict(dict)
    for r in rows(rev,'ticket_group_tickets.csv'):
        g=r['ticket_group_id']
        if g not in tg or g not in tar or not T(r['in_sale']): continue
        p=tg[g]['performance_id']
        avail[p][g]=avail[p].get(g,0)+max(0,lim.get(r['seat_id'],1)-busy[(p,r['seat_id'])])
    byp=collections.defaultdict(list)
    for x in sold: byp[x[0]].append(x)
    out={}
    for p,pr in perf.items():
        st=U(pr['start_at'])
        if not st or st<=snap: continue
        tot=sum(avail[p].values()); S=[x for x in byp[p] if x[1]<snap]
        w7=[x for x in S if x[1]>=snap-dt.timedelta(days=7)]
        chs=[]
        for c,cr in ch.items():
            if cr['performance_id']!=p or not T(cr['published']): continue
            gs=scg[c]
            chs.append(dict(id=c,name=cr['name'],site=is_site(cr['name']),
                avail=tot if not gs else sum(v for g,v in avail[p].items() if g in gs),
                bound=[dict(name=tg[g]['name'],price=tar.get(g,float(tg[g]['price'] or 0)),free=avail[p].get(g,0),created=tg[g]['created_at'][:16]) for g in gs if g in tg],
                upd=cr['updated_at'][:16],sales7=sum(1 for x in w7 if x[3]==c)))
        if not any(c['site'] for c in chs): continue
        if tot==0 and not w7: continue
        la=max((x[1] for x in S),default=None); ls=max((x[1] for x in S if x[2]),default=None)
        e=dict(id=p,name=shows.get(pr['show_id'],''),start=pr['start_at'][:16],total=tot,
               site=max(c['avail'] for c in chs if c['site']),sales7=len(w7),site7=sum(1 for x in w7 if x[2]),
               last_any=la.isoformat(' ')[:16] if la else None,last_site=ls.isoformat(' ')[:16] if ls else None,
               idle_days=(snap-la).total_seconds()/86400 if la else None,channels=chs)
        e['alert']=tot>0 and e['site']<0.5*tot
        e['warn']=not e['alert'] and (la is None or e['idle_days']>3)
        if e['alert']:
            # момент закрытия: изменение настроек сайт-канала (привязка групп), иначе — последняя продажа на сайте
            sc=[c for c in chs if c['site']]
            cl=max([U(c['upd']) for c in sc if c['bound']] or [ls] if ls else [None])
            e['closed_at']=cl.isoformat(' ')[:16] if cl else None
            e['closed_days']=(snap-cl).total_seconds()/86400 if cl else None
            if cl:
                b=[x for x in byp[p] if cl-dt.timedelta(days=7)<=x[1]<cl]
                e['before7']=dict(frm=(cl-dt.timedelta(days=7)).isoformat()[:10],to=(cl-dt.timedelta(days=1)).isoformat()[:10],
                                  site=sum(1 for x in b if x[2]),other=sum(1 for x in b if not x[2]))
            e['reason']=('к каналу привязаны только отдельные группы' if any(c['bound'] for c in sc) else
                         'места сняты с продажи или канал не видит группы')
        out[p]=e
    return out
snap=ctime(A.rev); psnap=ctime(A.prev)
cur=calc(A.rev,snap); pv=calc(A.prev,psnap)
for p,e in cur.items():
    q=pv.get(p,{})
    e['site_prev']=q.get('site'); e['total_prev']=q.get('total')
    pc={c['id']:c for c in q.get('channels',[])}
    e['ch_changes']=[dict(name=c['name'],was=[b['name'] for b in pc[c['id']]['bound']],now=[b['name'] for b in c['bound']],upd=c['upd'])
                     for c in e['channels'] if c['id'] in pc and {b['name'] for b in pc[c['id']]['bound']}!={b['name'] for b in c['bound']}]
    e['new_alert']=e['alert'] and not q.get('alert')
json.dump(dict(snap=snap.isoformat(' ')[:16],prev=psnap.isoformat(' ')[:16],events=cur),open(A.out,'w'),ensure_ascii=False,indent=1)
for e in sorted(cur.values(),key=lambda e:e['start']):
    tag='ТРЕВОГА' if e['alert'] else 'ВНИМАНИЕ' if e['warn'] else ''
    print(f"{e['id']:>4} {e['name'][:34]:34} {e['start'][:10]} сайт {e['site']}/{e['total']} 7д {e['site7']}/{e['sales7']} {tag}")
