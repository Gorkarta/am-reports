"""build_events.py — данные дашборда «Анализ продажи билетов» (Д3) из выгрузки БС (csv/ с GitHub).

Заменяет вшитый в HTML массив DATA: один объект на мероприятие (performance) — счётчики, выручка,
разбивки по ценовым группам и каналам в пяти срезах (all/active/sold/invite/cancelled) и посуточные продажи.

Запуск:  PYTHONPATH=. python3 -s build_events.py <папка_выгрузки> <выходной.json> '<ГГГГ-ММ-ДД ЧЧ:ММ время выгрузки, МСК>'

Определения (Правила обработки выгрузок БС v1.5):
  тестовые — performance_id ∈ {5,10,11,12,16,18} или «тест» в названии; служебные покупатели — orders.viewer_id ∈ {2608, 10},
  кроме покупок в день мероприятия (МСК); служебные — отдельный счётчик, в остальное не входят;
  продано — не удалён, не пригласительный, заказ оплачен (orders.sold_at заполнено); ожидают оплаты — то же, заказ не оплачен;
  пригласительные — is_invite = t, не удалены; аннулировано — deleted = t;
  возврат — удалённый билет оплаченного заказа; сгоревшая бронь — удалённый билет неоплаченного заказа;
  действующих = продано + пригласительные; всего = действующих + ожидают оплаты + аннулировано.
Названия каналов — sale_channels.name (канал заводится на мероприятие); группа — ticket_groups.name.
Персональные данные (tickets.data, individuals, payments) не читаются.
"""
import sys, json
import pandas as pd

D = sys.argv[1].rstrip('/') + '/'
OUT = sys.argv[2]
EXPORT_TIME = sys.argv[3]

TEST = {'5', '10', '11', '12', '16', '18'}
SERVICE = {'2608', '10'}

perf = pd.read_csv(D + 'performances.csv', dtype=str, usecols=['id', 'show_id', 'hall_id', 'venue_id', 'start_at'])
shows = pd.read_csv(D + 'shows.csv', dtype=str, usecols=['id', 'name'])
perf = perf.merge(shows.rename(columns={'id': 'show_id', 'name': 'show'}), on='show_id', how='left')
halls = pd.read_csv(D + 'halls.csv', dtype=str)
venues = pd.read_csv(D + 'venues.csv', dtype=str)
hall_name = dict(zip(halls.id, halls.name.fillna('')))
venue_name = dict(zip(venues.id, venues.name.fillna('')))
test_ids = set(perf.id[perf.id.isin(TEST) | perf.show.str.contains('тест', case=False, na=False)])
# start_at в выгрузке — уже местное (МСК) время с пометкой +00: сдвиг не нужен (концерт 17:00 хранится как 17:00+00)
perf['start_msk'] = pd.to_datetime(perf.start_at, format='mixed', utc=True)
perf['day'] = perf.start_msk.dt.strftime('%Y-%m-%d')
perf['date'] = perf.start_msk.dt.strftime('%Y-%m-%d %H:%M')
perf = perf[~perf.id.isin(test_ids)].set_index('id')

sc = pd.read_csv(D + 'sale_channels.csv', dtype=str, usecols=['id', 'distributor_id', 'name'])
ds = pd.read_csv(D + 'distributors.csv', dtype=str, usecols=['id', 'name']).rename(columns={'id': 'distributor_id', 'name': 'dname'})
sc = sc.merge(ds, on='distributor_id', how='left')
chan_name = {r.id: (r['name'] if isinstance(r['name'], str) and r['name'].strip() else (r.dname if isinstance(r.dname, str) else ''))
             for _, r in sc.iterrows()}
tg = pd.read_csv(D + 'ticket_groups.csv', dtype=str, usecols=['id', 'name'])
group_name = dict(zip(tg.id, tg.name.fillna('')))

t = pd.read_csv(D + 'tickets.csv', dtype=str,
                usecols=['id', 'order_id', 'performance_id', 'price', 'created_at', 'deleted', 'is_invite', 'sale_channel_id', 'ticket_group_id'])
o = pd.read_csv(D + 'orders.csv', dtype=str, usecols=['id', 'viewer_id', 'sold_at'])
t = t.merge(o.rename(columns={'id': 'order_id'}), on='order_id', how='left')
t = t[t.performance_id.isin(perf.index)].copy()
t['price'] = pd.to_numeric(t.price, errors='coerce').fillna(0.0)
t['created_day'] = (pd.to_datetime(t.created_at, format='mixed', utc=True) + pd.Timedelta(hours=3)).dt.strftime('%Y-%m-%d')
t['ev_day'] = t.performance_id.map(perf.day)
svc = t.viewer_id.isin(SERVICE) & (t.created_day != t.ev_day)
t_svc = t[svc]; t = t[~svc].copy()

deleted = t.deleted == 't'
invite = (t.is_invite == 't') & ~deleted
paid = t.sold_at.notna() & (t.sold_at != '')
sold = ~deleted & (t.is_invite != 't') & paid
pending = ~deleted & (t.is_invite != 't') & ~paid
refund = deleted & (t.is_invite != 't') & paid
t['f_sold'], t['f_invite'], t['f_pending'], t['f_cancel'], t['f_refund'] = sold, invite, pending, deleted, refund
t['zone'] = t.ticket_group_id.map(group_name).replace('', pd.NA).fillna('Без сектора')


def chan(r):
    if r.f_invite:
        return 'Пригласительные'
    cid = r.sale_channel_id
    if not isinstance(cid, str) or cid == '':
        return 'Без канала (нет данных)'
    return chan_name.get(cid) or f'Канал #{cid} (нет в справочнике)'


t['chan'] = [chan(r) for r in t.itertuples()]
SLICES = {'all': pd.Series(True, index=t.index), 'active': t.f_sold | t.f_invite, 'sold': t.f_sold,
          'invite': t.f_invite, 'cancelled': t.f_cancel}


def rows(df, col):
    n, rev = len(df), float(df.price.sum())
    g = df.groupby(col).agg(count=('price', 'size'), revenue=('price', 'sum')).reset_index()
    g = g.sort_values(['revenue', 'count', col], ascending=[False, False, True])
    return [{'name': r[col], 'count': int(r['count']), 'pct': round(100 * r['count'] / n, 1) if n else 0.0,
             'revenue': round(float(r['revenue']), 2), 'revenue_pct': round(100 * r['revenue'] / rev, 1) if rev else 0.0}
            for _, r in g.iterrows()]


exp_day = EXPORT_TIME[:10]
events = []
svc_n = t_svc.groupby('performance_id').size().to_dict()
for pid in perf.index:
    p = perf.loc[pid]
    df = t[t.performance_id == pid]
    if df.empty and pid not in svc_n:
        continue
    s_ = df[df.f_sold]
    c = {'sold': int(len(s_)), 'all': int(len(df)), 'cancelled': int(df.f_cancel.sum()), 'invite': int(df.f_invite.sum()),
         'pending': int(df.f_pending.sum()), 'refund': int(df.f_refund.sum())}
    c['active'] = c['sold'] + c['invite']
    c['burned'] = c['cancelled'] - c['refund']
    c['service'] = int(svc_n.get(pid, 0))
    bd = {}
    for k, mask in SLICES.items():
        d = df[mask.loc[df.index]]
        bd[k] = {'count': int(len(d)), 'revenue': round(float(d.price.sum()), 2), 'zones': rows(d, 'zone'), 'channels': rows(d, 'chan')}
    daily = s_.groupby('created_day').agg(tickets=('price', 'size'), revenue=('price', 'sum')).reset_index().sort_values('created_day')
    events.append({
        'event_id': f"{p.show} | {p.date}", 'perf_id': pid, 'show_name': p.show, 'hall_name': hall_name.get(p.hall_id, ''),
        'venue_name': venue_name.get(p.venue_id, ''), 'date': p.date, 'status': 'past' if p.day < exp_day else 'upcoming',
        'counts': c, 'revenue_sold': round(float(s_.price.sum()), 2),
        'avg_price': round(float(s_.price.mean()), 2) if len(s_) else 0.0, 'breakdowns': bd,
        'daily': [{'date': r.created_day, 'tickets': int(r.tickets), 'revenue': round(float(r.revenue), 2)} for r in daily.itertuples()],
    })
seen = {}
for e in events:
    seen[e['event_id']] = seen.get(e['event_id'], 0) + 1
for e in events:
    if seen[e['event_id']] > 1:
        e['event_id'] += f" · №{e['perf_id']}"
events.sort(key=lambda e: (e['date'], e['show_name']))
json.dump({'export_cur': EXPORT_TIME, 'events': events}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'мероприятий: {len(events)}; продано: {sum(e["counts"]["sold"] for e in events)}; служебных: {len(t_svc)}')
