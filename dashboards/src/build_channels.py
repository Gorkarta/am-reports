"""build_channels.py — данные дашборда «Каналы продаж — портфельная аналитика» (Д4) из выгрузки БС (csv/ с GitHub).

Заменяет build_data.py: те же определения, что в действующем дашборде (снимок 03.10.2026), но без жёстко
заданных путей и справочников из папки проекта. Справочник каналов строится из sale_channels.csv и distributors.csv.

Запуск:  PYTHONPATH=. python3 -s build_channels.py <папка_выгрузки> <выходной.json> <ДД.ММ.ГГГГ дата выгрузки>

Определения (Правила обработки выгрузок БС v1.5):
  тестовые — performance_id ∈ {5,10,11,12,16,18} или «тест» в названии мероприятия (п. 3.2);
  служебные покупатели — orders.viewer_id ∈ {2608, 10}, кроме покупок в день мероприятия по Москве (п. 3.3);
  продано — билет не удалён, не пригласительный, заказ оплачен (orders.sold_at заполнено);
  ожидают оплаты — не удалён, не пригласительный, заказ не оплачен;
  аннулировано — deleted = t (возвраты и сгоревшие брони вместе; как в действующем дашборде);
  пригласительные — is_invite = t, не удалены; в каналах не участвуют.
Персональные данные (tickets.data, individuals, payments) не читаются.
"""
import sys, json, re, collections
import pandas as pd

D = sys.argv[1].rstrip('/') + '/'
OUT = sys.argv[2]
GENERATED = sys.argv[3]

TEST = {'5', '10', '11', '12', '16', '18'}
SERVICE = {'2608', '10'}

perf = pd.read_csv(D + 'performances.csv', dtype=str, usecols=['id', 'show_id', 'start_at'])
shows = pd.read_csv(D + 'shows.csv', dtype=str, usecols=['id', 'name'])
perf = perf.merge(shows.rename(columns={'id': 'show_id', 'name': 'show'}), on='show_id', how='left')
test_ids = set(perf.id[perf.id.isin(TEST) | perf.show.str.contains('тест', case=False, na=False)])
start_day = (pd.to_datetime(perf.start_at, format='mixed', utc=True) + pd.Timedelta(hours=3)).dt.strftime('%Y-%m-%d')
perf_day = dict(zip(perf.id, start_day))

sc = pd.read_csv(D + 'sale_channels.csv', dtype=str, usecols=['id', 'distributor_id', 'name'])
ds = pd.read_csv(D + 'distributors.csv', dtype=str, usecols=['id', 'name']).rename(columns={'id': 'distributor_id', 'name': 'distributor_name'})
sc = sc.merge(ds, on='distributor_id', how='left')
dist_of = dict(zip(sc.id, sc.distributor_name.fillna('').str.strip()))

t = pd.read_csv(D + 'tickets.csv', dtype=str,
                usecols=['id', 'order_id', 'performance_id', 'price', 'created_at', 'deleted', 'is_invite', 'sale_channel_id'])
o = pd.read_csv(D + 'orders.csv', dtype=str, usecols=['id', 'viewer_id', 'sold_at'])
total_raw = len(t)
t = t.merge(o.rename(columns={'id': 'order_id'}), on='order_id', how='left')

is_test = t.performance_id.isin(test_ids)
created_msk_day = (pd.to_datetime(t.created_at, format='mixed', utc=True) + pd.Timedelta(hours=3)).dt.strftime('%Y-%m-%d')
event_day = t.performance_id.map(perf_day)
is_service = t.viewer_id.isin(SERVICE) & (created_msk_day != event_day) & ~is_test
test_excluded = int(is_test.sum()); service_excluded = int(is_service.sum())
t = t[~is_test & ~is_service].copy()

DIRECT_KEY = 'Прямые продажи (сайт Арены)'
NOCHAN_KEY = 'Без канала (нет данных)'
GROUP_RULES = [
    (re.compile(r'live\s*arena|лайв\s*арена', re.I), DIRECT_KEY),
    (re.compile(r'пустой\s*дистрибьютор', re.I), DIRECT_KEY),
    (re.compile(r'шлюз\s*сайт|виджет|widget', re.I), DIRECT_KEY),
    (re.compile(r'яндекс', re.I), 'Яндекс Афиша'),
    (re.compile(r'кассир', re.I), 'Кассир.ру'),
    (re.compile(r'red\s*kassa', re.I), 'Red Kassa'),
    (re.compile(r'конц|concert', re.I), 'Концерт.ру'),
    (re.compile(r'м\.?\s*видео|m\.?\s*video', re.I), 'М.Видео'),
]

def group_name(raw):
    for rx, label in GROUP_RULES:
        if rx.search(raw):
            return label
    return raw

def channel_key(cid, invite):
    if not isinstance(cid, str) or cid == '':
        return None if invite else NOCHAN_KEY
    if cid not in dist_of:
        return f'Канал #{cid} (нет в справочнике)'
    dist = dist_of[cid]
    return DIRECT_KEY if not dist else group_name(dist)

grid = collections.defaultdict(lambda: {'tickets': 0, 'revenue': 0.0})
sold_rev = collections.Counter(); ch_tickets = collections.Counter()
invite_total = sold_total = cancelled_total = pending_total = 0
rev_sold = rev_cancelled = 0.0
dates = []

for cid, inv, dele, sold_at, price, created in zip(t.sale_channel_id, t.is_invite, t.deleted, t.sold_at, t.price, t.created_at):
    if not isinstance(created, str) or not created:
        continue
    month = created[:7]; dates.append(created[:10])
    invite = (inv == 't'); price = float(price) if isinstance(price, str) and price else 0.0
    if dele == 't':
        st = 'cancelled'
    elif invite:
        st = 'invite'
    elif isinstance(sold_at, str) and sold_at:
        st = 'sold'
    else:
        st = 'pending'
    if st == 'invite':
        invite_total += 1
        continue
    if st == 'pending':
        pending_total += 1
        continue
    ck = channel_key(cid, invite)
    if ck is None:
        continue
    g = grid[(month, ck, st)]; g['tickets'] += 1; g['revenue'] += price
    ch_tickets[ck] += 1
    if st == 'sold':
        sold_total += 1; rev_sold += price; sold_rev[ck] += price
    else:
        cancelled_total += 1; rev_cancelled += price

months = sorted({m for (m, c, s) in grid})
rank = [c for c, _ in sold_rev.most_common()]
rows = [{'m': m, 'c': c, 's': s, 't': a['tickets'], 'r': round(a['revenue'], 2)} for (m, c, s), a in grid.items()]

MIN_ISSUED = 300
cancel_by = collections.Counter()
for (m, c, s), a in grid.items():
    if s == 'cancelled':
        cancel_by[c] += a['tickets']
returns = []
for c, issued in ch_tickets.items():
    if issued < MIN_ISSUED:
        continue
    returns.append({'c': c, 'issued': issued, 'cancelled': cancel_by[c], 'rate': round(cancel_by[c] / issued, 4)})
returns.sort(key=lambda x: -x['rate'])
issued_all = sold_total + cancelled_total

data = {
    'meta': {
        'generated': GENERATED, 'total_tickets_raw': total_raw, 'test_excluded_tickets': test_excluded,
        'test_excluded_performances': len(test_ids), 'service_excluded_tickets': service_excluded,
        'tickets_in_scope': len(t), 'date_min': min(dates), 'date_max': max(dates),
        'sold_total': sold_total, 'invite_total': invite_total, 'pending_total': pending_total,
        'cancelled_total': cancelled_total, 'revenue_total_sold': round(rev_sold, 2),
        'revenue_total_cancelled': round(rev_cancelled, 2), 'channels_total': len(ch_tickets),
        'portfolio_return_rate': round(cancelled_total / issued_all, 4) if issued_all else 0,
    },
    'months': months, 'channel_rank': rank, 'top_bar_keys': rank[:8], 'top_time_keys': rank[:4],
    'rows': rows, 'returns': returns[:12],
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print(json.dumps(data['meta'], ensure_ascii=False, indent=1))
print('months', months[0], months[-1], 'rows', len(rows), 'rank', rank[:8])
