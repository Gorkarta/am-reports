"""Кривая продаж по Методике v1.7, п. 2.1 (с 02.11.2026; заменяет кривую сервиса «Концерты и шоу»).

Запуск:  python3 curve.py --csv cur/ W:ГГГГ-ММ-ДД[:fan] [W:ГГГГ-ММ-ДД[:fan] ...]
  W          — окно продаж плана, дней (от старта продаж до концерта);
  ГГГГ-ММ-ДД — дата концерта (нужна для поправки на Новый год, п. 2.11);
  :fan       — фанатский старт (п. 2.12; сейчас — Blok3): 20% продаж в первые 7 дней окна.
Пишет curve{W}.json (билеты) и curve{W}_r.json (выручка) в формате прежнего curve.py:
  {"0": 1.0, ..., "W": 0.0} — доля цели, проданная к моменту «за d дней до концерта».
План-прогноз: билеты = цель_билеты × curve{W}[d]; выручка = цель_₽ × curve{W}_r[d].

Выборка (п. 2.1.2, 2.10): только репрезентативные завершённые мероприятия класса
«звёздный концерт / премия». Новое событие добавлять в REF после проверки по п. 2.10
и подтверждения владельца (Инструкция, п. 3.6).
"""
import csv, sys, os, json, datetime as dt, statistics as st
from collections import defaultdict

REF = [21, 23, 48]          # Премия МУЗ-ТВ 2026, Бузова, СуперЛайкШоу СТС Kids
SERVICE = {2608, 10}        # служебные покупатели (Правила, п. 3.3)
TEST = {5, 10, 11, 12, 16, 18}
FAN_L = 0.20                # доля первой недели при фанатском старте (п. 2.12)
MSK = dt.timezone(dt.timedelta(hours=3))
S = os.path.dirname(os.path.abspath(__file__)) + '/'


def ts(x):
    if not x:
        return None
    x = x.replace(' ', 'T')
    if x.endswith('+00'):
        x += ':00'
    return dt.datetime.fromisoformat(x).astimezone(MSK)


def load(csvdir):
    """Продажи эталонных событий: {pid: [(days_before_event, price), ...]}, окно каждого события."""
    perf = {}
    for r in csv.DictReader(open(csvdir + 'performances.csv', encoding='utf-8')):
        if int(r['id']) in REF:
            perf[int(r['id'])] = ts(r['start_at']).date()
    orders = {}
    for r in csv.DictReader(open(csvdir + 'orders.csv', encoding='utf-8')):
        orders[r['id']] = (r['viewer_id'], ts(r['sold_at']))
    sales = defaultdict(list)
    for r in csv.DictReader(open(csvdir + 'tickets.csv', encoding='utf-8')):
        pid = int(r['performance_id'] or 0)
        if pid not in perf or pid in TEST or r['deleted'] == 't' or r['is_invite'] == 't':
            continue
        o = orders.get(r['order_id'])
        if not o or o[1] is None:
            continue
        day = o[1].date()
        if o[0] and int(o[0]) in SERVICE and day != perf[pid]:
            continue
        sales[pid].append(((perf[pid] - day).days, float(r['price'] or 0)))
    win = {p: max(d for d, _ in v) for p, v in sales.items()}
    return sales, win


def base_curve(sales, win, W, rev):
    """Медиана по событиям долей, перенесённых на окно W (п. 2.1.2, шаги 2–4)."""
    per = []
    for p, v in sales.items():
        if win[p] < W:          # короткие окна не растягиваем
            continue
        tot = sum(pr if rev else 1 for _, pr in v)
        a = [sum(pr if rev else 1 for d, pr in v if d >= T) / tot for T in range(W + 1)]
        b = a[W]
        per.append([(x - b) / (1 - b) for x in a])
    if not per:
        print(f'curve.py: нет эталонных событий с окном ≥ {W} дн. — равномерная кривая', file=sys.stderr)
        return [1 - T / W for T in range(W + 1)], 0
    arr = [st.median(c[T] for c in per) for T in range(W + 1)]
    arr[0], arr[W] = 1.0, 0.0
    for T in range(W - 1, -1, -1):
        arr[T] = max(arr[T], arr[T + 1])
    return arr, len(per)


def ny_factor(d):
    """Доля продаж, которая уходит из дня (п. 2.11)."""
    if d.month == 12 and d.day == 31:
        return 0.6
    if d.month == 1 and d.day <= 2:
        return 1.0
    if d.month == 1 and d.day <= 8:
        return 0.6
    if d.month == 1 and d.day <= 20:
        return 0.4
    return 0.0


def adjust(arr, W, ev, fan):
    inc = {T: arr[T] - arr[T + 1] for T in range(W)}          # продажи дня, когда до концерта T дней
    if fan:                                                     # п. 2.12
        for T in inc:
            inc[T] *= 1 - FAN_L
        for T in range(W - 7, W):
            inc[T] += FAN_L / 7
    moved = 0.0
    for T in inc:                                               # п. 2.11
        f = ny_factor(ev - dt.timedelta(days=T))
        if f:
            moved += inc[T] * f
            inc[T] *= 1 - f
    if moved:
        def catch(d):
            return (d.month == 1 and d.day >= 21) or d.month == 2
        tgt = [T for T in inc if catch(ev - dt.timedelta(days=T))]
        if not tgt:   # концерт до 21.01 — догон в оставшиеся дни после праздников
            tgt = [T for T in inc if ny_factor(ev - dt.timedelta(days=T)) == 0 and (ev - dt.timedelta(days=T)).month == 1]
        if tgt:
            for T in tgt:
                inc[T] += moved / len(tgt)
        else:         # догнать некуда — поправку не применяем
            return arr
    out = [0.0] * (W + 1)
    acc = 0.0
    for T in range(W - 1, -1, -1):
        acc += inc[T]
        out[T] = acc
    out[W] = 0.0
    out[0] = 1.0
    return out


def main():
    args = sys.argv[1:]
    csvdir = 'cur/'
    if '--csv' in args:
        i = args.index('--csv')
        csvdir = args[i + 1]
        del args[i:i + 2]
    csvdir = csvdir.rstrip('/') + '/'
    sales, win = load(csvdir)
    for a in args:
        parts = a.split(':')
        W = int(parts[0])
        ev = dt.date.fromisoformat(parts[1]) if len(parts) > 1 else None
        fan = 'fan' in parts[2:]
        for rev, suf in ((False, ''), (True, '_r')):
            arr, n = base_curve(sales, win, W, rev)
            if ev:
                arr = adjust(arr, W, ev, fan)
            json.dump({str(d): round(arr[d], 6) for d in range(W + 1)}, open(S + f'curve{W}{suf}.json', 'w'))
        pts = [d for d in (90, 60, 30, 14, 7, 3) if d < W]
        print(W, ev, 'fan' if fan else '', f'событий {n}:',
              [(d, round(arr[d], 3)) for d in pts])


if __name__ == '__main__':
    main()
